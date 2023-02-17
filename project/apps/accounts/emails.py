import logging

from django.contrib.auth import get_user_model
from django.utils.http import int_to_base36

from apps.communication.models import Template, CommunicationHistory
from apps.communication.services.communications import send_templated_message
from public_urls import account_email_confirm_url
from utils.tasks import get_object_with_logging

logger = logging.getLogger(__name__)


def send_password_reset_email(*, user_id, reset_type, next_url=''):
    user = get_object_with_logging(get_user_model(), user_id)
    if not user:
        return

    context = {
        'user': ('accounts.User', user.id),
    }
    if reset_type == 'otp':
        template_type = Template.Types.accounts_password_reset_otp
        code, _ = otp.generate_otp(user)
        context.update({
            'otp': code,
            'whatsapp': {
                'template_body_parameters': [
                    {
                        'type': 'text',
                        'text': code,
                    }
                ]
            }
        })
    elif reset_type == 'magic_link':
        template_type = Template.Types.accounts_password_reset_magic_link
        context['magic_link'] = user.get_magic_link(next_url)
    elif reset_type == 'token':
        template_type = Template.Types.accounts_password_reset
        context['password_reset_url'] = user.get_reset_url(next_url=next_url)
    else:
        raise AttributeError

    send_templated_message.delay(
        template_type=template_type,
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
