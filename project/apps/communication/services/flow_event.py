import logging

from apps.communication.models import FlowEvent


logger = logging.getLogger(__name__)


def get_event(event_name):
    return FlowEvent.objects.get_or_create(title=event_name)[0]
