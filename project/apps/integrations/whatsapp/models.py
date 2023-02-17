from django.db import models

from apps.bases.models import BaseModel
from utils.fields import ActiveField


class WhatsAppTemplate(BaseModel):
    name = models.CharField(max_length=255)

    def str_model_name(self):
        return 'WA Template'

    def str(self):
        return self.name


class WhatsAppTemplateVersion(BaseModel):
    is_active = ActiveField()
    template = models.ForeignKey(WhatsAppTemplate, models.CASCADE, related_name='versions')
    vendor_id = models.CharField(max_length=255)
    language = models.CharField(max_length=5)
    category = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    components = models.JSONField(default=dict)

    def str_model_name(self):
        return 'WA Template Version'

    def str(self):
        return f'{self.template.name} — {self.language} ({self.vendor_id})'


class WhatsAppPhoneNumber(BaseModel):
    vendor_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    display = models.CharField(max_length=255)
    default = models.BooleanField(default=False)

    def str(self):
        return f'{self.name} ({self.vendor_id})'
