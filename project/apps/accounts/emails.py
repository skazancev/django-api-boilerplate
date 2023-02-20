import logging

from django.contrib.auth import get_user_model
from django.utils.http import int_to_base36

from apps.communication.models import Template, CommunicationHistory
from apps.communication.tasks import send_templated_message
from public_urls import account_email_confirm_url
from utils.tasks import get_object_with_logging
from apps.accounts.services import auth as auth_service


logger = logging.getLogger(__name__)


def send_password_reset_email(*, user_id, next_url=''):
    user = get_object_with_logging(get_user_model(), user_id)
    if not user:
        return

    context = {
        'user': ('accounts.User', user.id),
        'password_reset_url': auth_service.get_reset_url(user, next_url=next_url),
    }

    return send_templated_message.delay(
        template_type=Template.Types.accounts_password_reset,
        context=context,
        communication_user_id=user_id,
        communication_type=CommunicationHistory.Type.user,
    )


def send_email_confirmation(*, user_id):
    from apps.accounts.tokens import user_token_generator

    user = get_object_with_logging(get_user_model(), user_id)
    if not user:
        return

    url_kwargs = {
        'uidb36': int_to_base36(user_id),
        'token': user_token_generator.make_token(user)
    }

    return send_templated_message.delay(
        template_type=Template.Types.accounts_email_confirm,
        context={
            'user': user,
            'email_confirm_url': account_email_confirm_url(**url_kwargs),
            'email': user.email,
            **url_kwargs
        },
        communication_user_id=user_id,
        communication_type=CommunicationHistory.Type.user,
    )


def send_magic_link(user_id, next_url=''):
    user = get_object_with_logging(get_user_model(), user_id)
    if not user:
        return

    return send_templated_message.delay(
        template_type=Template.Types.accounts_password_reset_magic_link,
        context={
            'user': user,
            'magic_link': auth_service.get_magic_link(user, next_url=next_url),
        },
        communication_user_id=user_id,
        communication_type=CommunicationHistory.Type.user,
    )
