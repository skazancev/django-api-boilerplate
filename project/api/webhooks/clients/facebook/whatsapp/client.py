from functools import cached_property

from django.conf import settings

from api.webhooks.clients.base import BaseClient
from api.webhooks.clients.facebook.whatsapp.mixins import BusinessAccountMixin
from clients import WhatsAppClient as WhatsAppAPIClient


class WhatsAppClient(BusinessAccountMixin, BaseClient):
    def process_type(self):
        return self.content.get('hub.mode') or self.content.object

    def subscribe(self):
        if self.content['hub.verify_token'] == settings.FACEBOOK_VALIDATION_MARKER:
            return int(self.content['hub.challenge'])
        return None

    @cached_property
    def _api_client(self):
        return WhatsAppAPIClient()
