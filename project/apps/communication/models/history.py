import hashlib
from itertools import groupby
from typing import Union

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.forms import model_to_dict
from django.utils import timezone
from djchoices import DjangoChoices, ChoiceItem

from apps.bases.models import BaseModel
from apps.communication.models.template import Template
from utils.fields import ChoiceField
from utils.json import JSONEncoder


class CommunicationHistory(BaseModel):
    repeat_delays = settings.EMAILS_REPEAT_DELAYS

    class Direction(DjangoChoices):
        incoming = ChoiceItem('incoming', label=_('Входящая'))
        outgoing = ChoiceItem('outgoing', label=_('Исходящая'))

    class Type(DjangoChoices):
        manual = ChoiceItem('manual', label=_('Ручная'))
        automatic = ChoiceItem('automatic', label=_('Автоматическая'))
        user = ChoiceItem('user', label=_('Пользователь'))

    hash = models.SlugField()
    direction = models.CharField(choices=Direction.choices, max_length=100, default=Direction.outgoing)
    target = models.CharField(max_length=100)
    type = models.CharField(choices=Type.choices, max_length=20, default=Type.automatic)
    template_type = models.CharField(choices=Template.Types.choices, max_length=50, db_index=True)
    template_vendor = ChoiceField(Template.Vendors.choices, null=True, blank=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='communications')
    agent = models.ForeignKey(
        get_user_model(),
        related_name='agent_communications',
        on_delete=models.SET_NULL,
        null=True, blank=True, limit_choices_to={'is_staff': True},
    )
    sent = models.BooleanField(default=False)
    parent = models.ForeignKey('self', models.SET_NULL, null=True, blank=True)

    response = models.JSONField(blank=True, default=dict)
    context = models.JSONField(null=True, blank=True, encoder=JSONEncoder)
    meta = models.JSONField(null=True, blank=True)

    def str(self):
        return f'{self.user} - {self.target} - {self.direction}'

    class Meta:
        verbose_name = _('Коммуникация')
        verbose_name_plural = _('Коммуникации')

    def get_context(self):
        context: dict = self.context.copy()
        context['now'] = timezone.now().isoformat()
        context['communication_history_id'] = self.id
        context['communication_type'] = self.type

        return context

    @classmethod
    def get_repeat_delay(cls, value):
        if value in cls.repeat_delays:
            return cls.repeat_delays[value]
        return None

    @classmethod
    def generate(cls, **kwargs):
        from apps.communication.services.communications import generate_hash

        instance = cls(**kwargs)
        hash_str = generate_hash(
            model_to_dict(
                instance,
                fields=['direction', 'target', 'type', 'template_type', 'template_vendor', 'user', 'context'],
            ),
        )
        instance.hash = hashlib.md5(hash_str.encode()).hexdigest()

        if not cls.can_be_sent(instance.template_type, instance.user_id, instance.hash):
            if instance.type != cls.Type.manual:
                return None
        return instance

    @classmethod
    def can_be_sent(cls, template_type, user_id, _hash=None):
        kwargs = {
            'user_id': user_id,
            'template_type': template_type,
        }
        if (repeat_delay := cls.get_repeat_delay(template_type)) is not None:
            kwargs['created__gte'] = timezone.now() - timedelta(seconds=repeat_delay)

        if _hash:
            kwargs['hash'] = _hash

        return not CommunicationHistory.objects.filter(**kwargs).exists()

    def as_dict(self) -> dict:
        return {"email": self.user.email, 'name': self.user.name}

    @classmethod
    def send(cls, communications: Union['CommunicationHistory', 'CommunicationHistory.objects'], **kwargs):
        if isinstance(communications, CommunicationHistory):
            communications = [communications]

        grouped = groupby(
            filter(lambda item: not item.sent, communications),
            key=lambda item: item.meta.get('template_id'),
        )
        for template_id, items in grouped:
            if template := Template.objects.active().filter(pk=template_id).first():
                template.helper.send(communications, **kwargs)
