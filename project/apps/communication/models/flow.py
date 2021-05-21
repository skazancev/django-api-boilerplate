from datetime import timedelta, datetime

from django.db import models
from django.utils import timezone

from apps.bases.models import BaseModel
from utils.fields import ActiveField
from .flow_event import FlowEvent


class Flow(BaseModel):
    is_active = ActiveField()
    title = models.CharField(max_length=255)
    event = models.OneToOneField(FlowEvent, models.CASCADE)

    def str(self):
        return self.title


class FlowAction(BaseModel):
    class DelayTypes(models.TextChoices):
        days = 'days', _('Days')
        hours = 'hours', _('Hours')
        minutes = 'minutes', _('Minutes')
        seconds = 'seconds', _('Seconds')

    flow = models.ForeignKey(Flow, models.CASCADE, related_name='actions')

    # email
    template = models.ForeignKey('Template', models.PROTECT, limit_choices_to={
        'is_active': True,
    })
    delay = models.PositiveIntegerField(default=0)
    send_time = models.TimeField(null=True, blank=True)
    delay_type = models.CharField(choices=DelayTypes.choices, default=DelayTypes.minutes, max_length=7)
    delay_seconds = models.IntegerField(editable=False)

    class Meta:
        ordering = ('delay_seconds',)

    def calculate_delay_seconds(self):
        now = timezone.now()
        return (self.get_send_date(now) - now).total_seconds()

    def get_send_date(self, start_date: datetime):
        start_date += timedelta(**{self.delay_type: self.delay})
        if self.delay_type == self.DelayTypes.days and self.send_time:
            start_date = datetime.combine(start_date, self.send_time)

        if timezone.is_naive(start_date):
            start_date = timezone.make_aware(start_date)

        return start_date

    def save(self, *args, **kwargs):
        if self._created or (self.tracker.has_changed('delay') or self.tracker.has_changed('delay_type')):
            self.delay_seconds = self.calculate_delay_seconds()

        if self.delay_type != self.DelayTypes.days:
            self.send_time = None

        super().save(*args, **kwargs)
