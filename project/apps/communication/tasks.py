from typing import List

from apps.communication.models import CommunicationHistory, Template
from apps.communication.services import communications as communications_service
from apps.integrations.slack.tasks import send_slack_msg
from celeryapp.app import app


@app.task
def send_communications(communications: List[int]):
    queryset = CommunicationHistory.objects.filter(id__in=communications)
    communications_service.send_multiple(queryset)


@app.task
def send_templated_message(template_type, **kwargs):
    if not (templates := Template.objects.active().filter(type=template_type)):
        send_slack_msg.delay('qa-notifications', f'<!channel> Template was not found: `{template_type}`')
        return

    communications = list()
    for template in templates:
        if communication := communications_service.generate(template=template, **kwargs):
            CommunicationHistory.send(communication)
            communications.append(communication.id)

    return communications
