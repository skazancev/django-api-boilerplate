import logging

from django.contrib.auth import get_user_model
from django.utils.http import int_to_base36

from apps.emails.models import EmailTemplate
from apps.emails.tasks import send_templated_mail
from utils.tasks import get_object_with_logging

logger = logging.getLogger(__name__)


def send_password_reset_email(*, user_id, next_url=''):
    user = get_object_with_logging(get_user_model(), user_id)
    if not user:
        return

    send_templated_mail.delay(
        template_type=EmailTemplate.Types.accounts_password_reset,
        context={
            'user': ('accounts.USer', user.id),
            'password_reset_url': user.get_reset_url(next_url=next_url),
        },
        recipient_list=user.pretty_email,
    )


def send_email_confirmation(*, user_id):
    from apps.accounts.tokens import user_token_generator
    from public_urls import account_email_confirm_url

    user = get_object_with_logging(get_user_model(), user_id)
    if not user:
        return

    url_kwargs = {
        'uidb36': int_to_base36(user_id),
        'token': user_token_generator.make_token(user)
    }

    return send_templated_mail(
        template_type='accounts_email_confirm',
        context={
            'user': ('accounts.User', user.id),
            'email_confirm_url': account_email_confirm_url(**url_kwargs),
            'email': user.email,
            **url_kwargs
        },
        recipient_list=user.pretty_email,
    )
