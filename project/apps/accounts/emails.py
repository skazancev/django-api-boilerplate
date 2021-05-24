import logging

from django.contrib.auth import get_user_model
from django.utils.http import int_to_base36

from apps.communication import flow_events
from apps.communication.services import flow as flow_service
from public_urls import account_email_confirm_url
from utils.tasks import get_object_with_logging

logger = logging.getLogger(__name__)


def send_password_reset_email(*, user_id, next_url=''):
    user = get_object_with_logging(get_user_model(), user_id)
    if not user:
        return

    flow_service.trigger_flow_event(
        flow_events.RESET_PASSWORD,
        user,
        context={
            'user': user,
            'password_reset_url': user.get_reset_url(next_url=next_url),
        },
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

    return flow_service.trigger_flow_event(
        event=flow_events.CONFIRM_EMAIL,
        user=user,
        context={
            'user': user,
            'email_confirm_url': account_email_confirm_url(**url_kwargs),
            'email': user.email,
            **url_kwargs
        },
    )
