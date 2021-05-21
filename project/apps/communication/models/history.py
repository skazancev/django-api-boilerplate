from django.contrib.auth import get_user_model
from django.db import models
from djchoices import DjangoChoices, ChoiceItem

from apps.bases.models import BaseModel
from .user_flow import UserFlow
from .template import Template


class CommunicationHistoryError(Exception):
    pass


class CommunicationHistoryFrequencyError(CommunicationHistoryError):
    pass


class CommunicationHistory(BaseModel):

    class Direction(DjangoChoices):
        incoming = ChoiceItem('incoming', label=_('Входящая'))
        outgoing = ChoiceItem('outgoing', label=_('Исходящая'))

    hash = models.SlugField()
    direction = models.CharField(choices=Direction.choices, max_length=50, default=Direction.outgoing)
    target = models.CharField(max_length=50)
    trigger_type = models.CharField(choices=UserFlow.Type.choices, max_length=20, default=UserFlow.Type.automatic)
    type = models.CharField(choices=Template.Types.choices, max_length=20, default=Template.Types.mail)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='communications')
    agent = models.ForeignKey(
        get_user_model(),
        related_name='agent_communications',
        on_delete=models.SET_NULL,
        null=True, blank=True, limit_choices_to={'is_staff': True},
    )
    user_flow_action = models.ForeignKey('UserFlowAction', models.SET_NULL, null=True, blank=True)
    sent = models.BooleanField(default=False)
    parent = models.ForeignKey('self', models.SET_NULL, null=True, blank=True)

    def str(self):
        return f'{self.user} - {self.target}'

    class Meta:
        verbose_name = _('Коммуникация')
        verbose_name_plural = _('Коммуникации')
