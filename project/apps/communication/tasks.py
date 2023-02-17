from typing import List

from apps.communication.models import CommunicationHistory
from celeryapp.app import app


@app.task
def send_communications(communications: List[int]):
    from apps.communication.services import communications as communications_service
    queryset = CommunicationHistory.objects.filter(id__in=communications)
    communications_service.send_multiple(queryset)
