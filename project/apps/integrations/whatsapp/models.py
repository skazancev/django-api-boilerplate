from django.db import models

from apps.bases.models import BaseModel
from utils.fields import ActiveField, ChoiceField


class WhatsAppTemplate(BaseModel):
    name = models.CharField(max_length=255)

    def str_model_name(self):
        return 'WA Template'

    def str(self):
        return self.name


class BaseWhatsAppAdmin(BaseModel):
    def str_model_name(self):
        return ''

    class Meta:
        abstract = True


class WhatsAppTemplateVersion(BaseWhatsAppAdmin):
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


class WhatsAppPhoneNumber(BaseWhatsAppAdmin):
    class Type(models.TextChoices):
        contact = 'contact'
        system = 'system'

    vendor_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    display = models.CharField(max_length=255, blank=True)
    default = models.BooleanField(default=False)
    type = ChoiceField(choices=Type.choices, default=Type.contact)

    def str_model_name(self):
        return ''

    def str(self):
        return f'<{self.get_type_display()}{f": {self.name}" if self.name else ""}> ({self.vendor_id})'


class WhatsAppMessage(BaseWhatsAppAdmin):
    class Types(models.TextChoices):
        text = 'text'
        image = 'image'
        video = 'video'
        audio = 'audio'
        document = 'document'
        template = 'template'

    business_account_id = models.CharField(max_length=255)
    vendor_id = models.CharField(max_length=255)
    from_number = models.ForeignKey(WhatsAppPhoneNumber, models.CASCADE, related_name='from_messages')
    to_number = models.ForeignKey(WhatsAppPhoneNumber, models.CASCADE, related_name='to_messages')
    type = ChoiceField(choices=Types.choices, default=Types.text)
    date = models.DateTimeField()
    text = models.TextField(blank=True)
    file = models.FileField(null=True, blank=True, upload_to='whatsapp_messages')
    raw_data = models.JSONField(default=dict)

    def str(self):
        return f'{self.vendor_id} — {self.from_number}: {self.type}'

    class Meta:
        ordering = ['-date']


class WhatsAppMessageEvent(BaseWhatsAppAdmin):
    class Types(models.TextChoices):
        sent = 'sent'
        delivered = 'delivered'
        read = 'read'

    message = models.ForeignKey(WhatsAppMessage, models.CASCADE, related_name='events')
    type = ChoiceField(choices=Types.choices)
    date = models.DateTimeField()

    def str(self):
        return self.get_type_display()
