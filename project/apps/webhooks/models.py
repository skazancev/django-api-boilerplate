from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models

from apps.bases.models import BaseModel
from utils.core import Dict


class WebhookData(BaseModel):
    class Sources(models.TextChoices):
        google_forms = 'google_forms', 'Google Forms'
        paybox = 'paybox', 'PayBox'
        telegram = 'telegram', 'Telegram'
        sendgrid = 'sendgrid', 'Sendgrid'
        slack = 'slack', 'Slack'
        stripe = 'stripe', 'Stripe'
        apple = 'apple', 'Apple'
        facebook_whatsapp = 'facebook_whatsapp', 'Facebook WhatsApp'

    source = models.CharField(max_length=250, choices=Sources.choices)
    remote_ip = models.GenericIPAddressField(default='127.0.0.1')
    content = models.JSONField()
    is_processed = models.BooleanField(default=False)
    content_search = SearchVectorField(null=True)

    class Meta:
        verbose_name = 'Данные вебхука'
        verbose_name_plural = 'Данные вебхуков'
        indexes = [GinIndex(fields=['content_search'])]

    def str(self):
        return f'from {self.source}'

    @property
    def data(self) -> Dict:
        return Dict.convert(self.content)
