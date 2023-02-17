from django.conf import settings

from .client import KlaviyoClient
from celeryapp.app import app


@app.task
def create_klaviyo_event(event_name):
    KlaviyoClient.send_event(email=settings.DEFAULT_FROM_EMAIL, event=event_name)


@app.task
def klaviyo_send_communication(communication_id: int, event_name: str):
    from ...communication.models import CommunicationHistory

    communication = CommunicationHistory.objects.get(id=communication_id)
    if KlaviyoClient.send_event(communication.user.email, event_name, event_properties=communication.get_context()):
        communication.sent = True
        communication.save()
