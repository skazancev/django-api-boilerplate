from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from apps.bases.models import BaseQuerySet, BaseModel
from utils.fields import ActiveField, RoundedDateTimeField
from utils.models import JSONEncoder


class UserFlowQuerySet(BaseQuerySet):
    def active(self):
        return super().active().filter(is_completed=False)


class UserFlow(BaseModel):
    class Type(models.TextChoices):
        manual = 'manual', _('Ручная')
        automatic = 'automatic', _('Автоматическая')
        user = 'user', _('Пользователь')

    user = models.ForeignKey(get_user_model(), models.CASCADE, related_name='flows')
    flow = models.ForeignKey('communication.Flow', models.CASCADE, related_name='users')
    context = models.JSONField(null=True, blank=True, encoder=JSONEncoder)
    is_completed = models.BooleanField(default=False)
    start_date = RoundedDateTimeField(default=timezone.now)
    metadata = models.JSONField(null=True, blank=True)
    active = ActiveField(default=True)
    trigger_type = models.CharField(max_length=9, choices=Type.choices, default=Type.automatic)
    agent = models.ForeignKey(get_user_model(), models.SET_NULL, null=True, blank=True)

    objects = UserFlowQuerySet.as_manager()


class UserFlowAction(BaseModel):
    flow = models.ForeignKey(UserFlow, models.CASCADE, related_name='actions')
    action = models.ForeignKey('communication.FlowAction', models.CASCADE, related_name='user_actions')
    eta = models.DateTimeField()

    @property
    def is_last(self):
        return self.flow.flow.actions.last().id == self.action_id
