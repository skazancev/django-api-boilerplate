from django.db import models
from djchoices import DjangoChoices, ChoiceItem

from apps.bases.models import BaseModel
from utils.fields import ActiveField


class Config(BaseModel):
    class Type(DjangoChoices):
        whatsapp_business_account_id = ChoiceItem(
            'whatsapp_business_account_id',
            label=_('WhatsApp Business Account ID'),
            type=int,
            default=101889599456862,
        )

    is_active = ActiveField()
    type = models.CharField(choices=Type.choices, max_length=38, unique=True)
    value = models.CharField(max_length=255)
    visible = models.BooleanField(default=True, editable=False)

    def str(self):
        return self.type

    @classmethod
    def convert(cls, type_, value):
        try:
            return cls.Type.get_choice(type_).type(value)
        except AttributeError:
            return value

    @classmethod
    def get_dict(cls):
        return {
            key: cls.convert(key, value)
            for key, value in cls.objects.active().values_list('type', 'value')
            if key in cls.Type.attributes
        }

    @classmethod
    def get(cls, key, default=None):
        try:
            return Config.get_dict()[key]
        except KeyError:
            return getattr(Config.Type.get_choice(key), 'default', default)

    @classmethod
    def set(cls, key, value):
        return Config.objects.update_or_create(key=key, defaults={'value': value})
