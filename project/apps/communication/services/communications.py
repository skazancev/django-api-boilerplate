import hashlib
import json
from typing import Optional, List

from django.forms import model_to_dict

from apps.communication.models import UserFlow, CommunicationHistory
from apps.communication.services.emails import Message
from utils.models import JSONEncoder


def generate(**kwargs) -> Optional[CommunicationHistory]:
    instance = CommunicationHistory(**kwargs)
    hash_data = json.dumps(
        {
            **model_to_dict(
                instance,
                fields=['direction', 'target', 'trigger_type', 'user'],
            ),
            **instance.user_flow_action.flow.context,
        },
        sort_keys=True,
        cls=JSONEncoder,
    )
    instance.hash = hashlib.md5(hash_data.encode()).hexdigest()

    # try to prevent sending duplicated events
    if instance.trigger_type == UserFlow.Type.automatic and \
            CommunicationHistory.objects.filter(hash=instance.hash).exists():
        return None

    return instance


def send(communication: CommunicationHistory):
    message = Message(
        communication.user_flow_action.action.template,
        communication.user_flow_action.flow.context,
        to=communication.user,
    )
    if message.send():
        communication.sent = True
        communication.save()


def send_multiple(communications: List[CommunicationHistory]):
    for communication in communications:
        message = Message(
            communication.user_flow_action.action.template,
            communication.user_flow_action.flow.context,
            to=communication.user,
        )
        if message.send():
            communication.sent = True

    CommunicationHistory.objects.bulk_update(communications, fields=['sent', 'modified'])
