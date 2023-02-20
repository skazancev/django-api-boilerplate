from apps.integrations.whatsapp.models import WhatsAppTemplateVersion
from celeryapp.app import app
from clients import WhatsAppMessageReceiver, WhatsAppClient
from clients.facebook import WhatsAppError, WhatsAppResponseError
from utils.core import recursive_get


@app.task
def send_whatsapp_message(communication_id, template_version_id):
    from apps.communication.models import CommunicationHistory

    communication = CommunicationHistory.objects.get(id=communication_id)
    version = WhatsAppTemplateVersion.objects.get(id=template_version_id)
    receiver = WhatsAppMessageReceiver(
        phone_number=communication.user.phone if communication.user.whatsapp_enabled is not False else None,
        template_name=version.template.name,
        template_language=version.language,
        **communication.context.get('whatsapp', {}),
    )
    try:
        if response := WhatsAppClient().send_message(receiver):
            communication.sent = True
            communication.response = dict(response)
            if communication.user.whatsapp_enabled:
                communication.user.whatsapp_enabled = True
                communication.user.save(update_fields=['whatsapp_enabled'])

    except WhatsAppError as e:
        communication.response = e.data
        communication.sent = False

    except WhatsAppResponseError as e:
        if recursive_get(e.response_json, 'error', 'error_subcode') == 2494010:
            communication.user.whatsapp_enabled = False
            communication.user.save()

        communication.response = e.response_json
        communication.sent = False
    finally:
        communication.save()
