from datetime import datetime
from typing import TYPE_CHECKING

import pytz
from django.core.files import File

from apps.core.models import Config
from apps.integrations.whatsapp.models import WhatsAppPhoneNumber, WhatsAppMessage, WhatsAppMessageEvent

if TYPE_CHECKING:
    from .client import WhatsAppClient

    class BaseClass(WhatsAppClient):
        pass
else:
    class BaseClass:
        pass


class BusinessAccountMixin(BaseClass):
    def whatsapp_business_account(self):
        for entry in self.content.get('entry', []):
            self._process_entry(entry)

    def _process_entry(self, entry):
        if entry.id != str(Config.get(Config.Type.whatsapp_business_account_id)):
            return

        for change in entry.changes:
            self._process_change(change)

    def _process_change(self, change):
        if change.field != 'messages':
            return

        value = change.value
        metadata = value.metadata
        phone_number = WhatsAppPhoneNumber.objects.filter(
            vendor_id=metadata.phone_number_id,
            type=WhatsAppPhoneNumber.Type.system,
        ).first()
        if not phone_number:
            return

        for status in value.get('statuses', []):
            self._process_message_status(status)

        messages = value.get('messages', [])
        if messages:
            contacts = {
                contact.wa_id: contact
                for contact in value.contacts
            }

            for message in messages:
                self._process_message(message, contacts.get(message['from']), phone_number)

    def _process_message_status(self, status):
        message = WhatsAppMessage.objects.filter(vendor_id=status.id).first()
        if not message:
            return

        WhatsAppMessageEvent.objects.create(
            message=message,
            type=status.status,
            date=datetime.fromtimestamp(int(status.timestamp), tz=pytz.UTC),
        )

    def _process_message(self, message, contact, phone_number):
        contact = WhatsAppPhoneNumber.objects.update_or_create(
            vendor_id=contact.wa_id,
            defaults={
                'name': contact.profile.name,
            },
        )[0]
        WhatsAppMessage.objects.create(
            business_account_id=Config.get(Config.Type.whatsapp_business_account_id),
            vendor_id=message.id,
            from_number=contact,
            to_number=phone_number,
            type=message.type,
            date=datetime.fromtimestamp(int(message.timestamp), tz=pytz.UTC),
            raw_data=dict(message),
            **self._message_type_data(message),
        )
        self._api_client.mark_message_as_read(phone_number.vendor_id, message.id)

    def _message_type_data(self, message) -> dict:
        if message.type == WhatsAppMessage.Types.text:
            return {'text': message.text.body}
        if message.type in [
            WhatsAppMessage.Types.image,
            WhatsAppMessage.Types.video,
            WhatsAppMessage.Types.audio,
            WhatsAppMessage.Types.document,
        ]:
            media = self._api_client.download_media(message[message.type].id)
            return {'file': File(media)}

        return {}
