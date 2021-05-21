from functools import cached_property
from typing import List

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from sendgrid import sendgrid

from apps.communication.models import Template


class Message:
    def __init__(self, template, context, *, to: get_user_model(), **kwargs):
        self.template = template
        self.context = context
        self.to = to
        self.kwargs = kwargs

    def send(self):
        if self.template.type == Template.Types.mail:
            if settings.SENDGRID_ENABLED:
                return self._send_sendgrid_mail()
            return self._send_mail()
        elif self.template.type == Template.Types.sms:
            return self._send_sms()

    @cached_property
    def _get_context(self):
        self.context['now'] = timezone.now()
        return self.context

    def _get_subject(self):
        return self.template.format_subject(self._get_context)

    def _get_body(self):
        return self.template.format_body(self._get_context)

    def _prepare_sendgrid_personalization(self):
        personalization = {
            'to': [{"email": self.to.email, 'name': self.to.name}],
        }
        if self.template.sendgrid_template_id:
            personalization['dynamic_template_data'] = self._get_context

        return personalization

    def _send_sendgrid_mail(self):
        request_body = {
            'from': {
                'email': settings.DEFAULT_FROM_EMAIL,
                'name': settings.COMPANY_NAME,
            },
            'personalizations': [self._prepare_sendgrid_personalization()],
        }

        if self.template.sendgrid_template_id is not None:
            request_body['template_id'] = self.template.sendgrid_template_id
        else:
            request_body.update({
                'subject': self._get_subject(),
                'content': [
                    {
                        'type': 'text/plain',
                        'value': self._get_body(),
                    },
                ],
            })

        if self.template.bcc_emails:
            request_body['personalizations'].extend([
                {'bcc': email}
                for email in self.template.bcc_emails
            ])
        sg = sendgrid.SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.client.mail.send.post(request_body=request_body)
        if response.status_code >= 202:
            return True
        return False

    def _send_mail(self):
        msg = EmailMultiAlternatives(
            subject=self._get_subject(),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[f'{self.to.name} <{self.to.email}>'],
            body=self._get_body(),
            bcc=self.template.bcc_emails,
        )
        return msg.send()

    def _send_sms(self):
        pass


class BulkMessage:
    def __init__(self, messages: List[Message]):
        self.messages = messages

    def send(self):
        for message in self.messages:
            message.send()
