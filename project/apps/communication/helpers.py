from typing import List, TYPE_CHECKING

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.integrations.klaviyo.tasks import create_klaviyo_event, klaviyo_send_communication
from utils.cache import cached_method

if TYPE_CHECKING:
    from apps.communication.models import CommunicationHistory


class BaseTemplateHelper:
    def __init__(self, template):
        self.template = template

    @property
    def target(self):
        raise NotImplementedError

    def get_id(self, user=None):
        raise NotImplementedError

    def clean(self):
        pass

    def before_save(self):
        pass

    def send(self, communications: List['CommunicationHistory'], **kwargs):
        raise NotImplementedError


class KlaviyoTemplateHelper(BaseTemplateHelper):

    @property
    def target(self):
        return self.template.klaviyo_event.name

    def get_id(self, user=None):
        return self.template.klaviyo_event.name

    def clean(self):
        if not self.template.klaviyo_event_id:
            raise ValidationError('Klaviyo event is required for selected vendor')

    def before_save(self):
        if self.template.tracker.has_changed('klaviyo_event_id'):
            transaction.on_commit(lambda: create_klaviyo_event.delay(self.template.klaviyo_event.name))

    def send(self, communications: List['CommunicationHistory'], **kwargs):
        for item in communications:
            klaviyo_send_communication.delay(item.id, self.get_id())


class WhatsAppTemplateHelper(BaseTemplateHelper):

    @cached_method
    def get_version(self, user=None):
        if template := self.template.whatsapp_template.versions.filter(language='en_US').first():
            return template
        return self.template.whatsapp_template.versions.first()

    @property
    def target(self):
        return self.template.whatsapp_template.name

    def get_id(self, user=None):
        return self.get_version(user=user).vendor_id

    def clean(self):
        if not self.template.whatsapp_template_id:
            raise ValidationError('WhatsApp template is required for selected vendor')

    def send(self, communications: List['CommunicationHistory'], **kwargs):
        from project.apps.emails.tasks import send_whatsapp_message
        for communication in communications:
            send_whatsapp_message.delay(communication.id, self.get_version(communication.user).id)
