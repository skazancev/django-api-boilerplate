from django.conf import settings

from api.webhooks.clients.base import BaseClient


class WhatsappClient(BaseClient):
    def process_type(self):
        return self.content.get('hub.mode') or self.content.object

    def subscribe(self):
        if self.content['hub.verify_token'] == settings.FACEBOOK_VALIDATION_MARKER:
            return int(self.content['hub.challenge'])
        return None

    def whatsapp_business_account(self):
        print(self.content)
