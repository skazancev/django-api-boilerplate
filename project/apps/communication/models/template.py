from functools import cached_property

from django.db import models
from simple_history.models import HistoricalRecords

from apps.bases.models import BaseModel
from utils.fields import ActiveField, ChoiceField
from .. import helpers
from ...integrations.klaviyo.models import KlaviyoEvent
from ...integrations.whatsapp.models import WhatsAppTemplate


class Template(BaseModel):
    class VendorType(str):
        def __new__(cls, string, helper=None):
            self = str.__new__(cls, string)
            self.helper = helper
            return self

    class Vendors(VendorType, models.Choices):
        klaviyo = 'klaviyo', helpers.KlaviyoTemplateHelper
        whatsapp = 'whatsapp', helpers.WhatsAppTemplateHelper

    class Types(models.TextChoices):
        accounts_password_reset = 'accounts_password_reset', _('Восстановление пароля')
        accounts_password_reset_otp = 'accounts_password_reset_otp', _('Восстановление пароля одноразовым кодом')
        accounts_password_reset_magic_link = (
            'accounts_password_reset_magic_link',
            _('Восстановление пароля через magic link'),
        )
        accounts_email_confirm = 'accounts_email_confirm', _('Подтверждение адреса эл. почты')

    is_active = ActiveField()
    vendor = ChoiceField(choices=Vendors.choices)
    type = models.CharField(
        max_length=50,
        choices=Types.choices,
    )

    whatsapp_template = models.ForeignKey(WhatsAppTemplate, models.PROTECT, null=True, blank=True)
    klaviyo_event = models.ForeignKey(KlaviyoEvent, models.PROTECT, null=True, blank=True)

    history = HistoricalRecords()

    class Meta:
        ordering = ['type']
        verbose_name = _('Шаблон письма')
        verbose_name_plural = _('Шаблоны писем')
        tracker_fields = ('klaviyo_event_id',)
        unique_together = ('vendor', 'type')

    def __str__(self):
        return f'({self.get_vendor_display()}) {self.get_vendor_target()}'

    @cached_property
    def helper(self) -> helpers.BaseTemplateHelper:
        return self.Vendors._value2member_map_[self.vendor].helper(self)

    def clean(self):
        super().clean()
        self.helper.clean()

    def save(self, *args, **kwargs):
        self.helper.before_save()
        super().save(*args, **kwargs)

    def get_vendor_target(self):
        return self.helper.target
    get_vendor_target.short_description = 'Vendor target'
    get_vendor_target.admin_order_field = 'Vendor target'
