from datetime import datetime

from django.apps import apps
from django.conf import settings

from celeryapp.app import app

import logging

from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives

from apps.emails.models import EmailTemplate
from utils.urls import get_base_url


logger = logging.getLogger(__name__)


class EmailError(Exception):
    pass


def perform_context(context):
    for key, value in context.items():
        try:
            if isinstance(value, list) and len(value) == 2 and (model := apps.get_model(value[0])):
                context[key] = model.objects.filter(id=value[1]).last() or value

            if isinstance(value, str) and value.startswith('_date-'):
                value = datetime.fromisoformat(value)
                value_time = value.time()
                if not any([value_time.hour, value_time.minute, value_time.second]):
                    value = value.date()

                context[key] = value

        except (ValueError, LookupError):
            pass

    return context


def send_mail(context, template, recipient_list, **kwargs):
    if recipient_list is None:
        recipient_list = []

    if not isinstance(recipient_list, (list, tuple)):
        recipient_list = [recipient_list]

    recipient_list.extend(template.extra_recipients or [])
    msg = EmailMultiAlternatives(
        subject=template.format_subject(context),
        from_email=template.from_addr or settings.DEFAULT_FROM_EMAIL,
        to=recipient_list,
        bcc=template.cc_emails,
        **kwargs,
    )
    msg.attach_alternative(template.format_body(context), "text/html")
    return msg.send()


@app.task
def send_templated_mail(*,
                        template_type,
                        context=None,
                        recipient_list=None,
                        **kwargs):
    template: EmailTemplate = EmailTemplate.objects.active().filter(type=template_type).last()
    if not template:
        raise EmailError(f'Template does not exist: {template_type}')

    context = perform_context(context) if context else {}
    site = Site.objects.get_current()
    extra_context = {
        'website': {
            'name': site.name,
            'url': site.domain,
            'base_url': get_base_url(),
        }
    }

    if set(extra_context) & set(context):
        raise ValueError(f'"context" contains unacceptable values ({", ".join(list(extra_context.keys()))})')

    context.update(extra_context)
    return send_mail(context, template, recipient_list, **kwargs)
