import json
from urllib.parse import urlencode

import klaviyo
import requests
from django.conf import settings


class KlaviyoClient:
    @staticmethod
    def client():
        return klaviyo.Klaviyo(public_token=settings.KLAVIYO_PUBLIC_TOKEN,
                               private_token=settings.KLAVIYO_PRIVATE_TOKEN)

    @staticmethod
    def generate_payload(event, email, customer_properties, event_properties):
        payload = {
            "token": settings.KLAVIYO_PUBLIC_TOKEN,
            "event": event,
            "customer_properties": {
                "$email": email
            }
        }
        if event_properties:
            payload['properties'] = event_properties
        if customer_properties:
            payload['customer_properties'].update(customer_properties)

        return urlencode({'data': json.dumps(payload)})

    @classmethod
    def send_event(cls, email, event, customer_properties=None, event_properties=None):
        event = event + ' Dev' if settings.DEBUG else event
        if settings.KLAVIYO_ENABLED:
            if not settings.DEBUG or email.rsplit('@', maxsplit=1)[-1] in settings.DOMAIN_NAMES:
                headers = {
                    "Accept": "text/html",
                    "Content-Type": "application/x-www-form-urlencoded"
                }
                data = cls.generate_payload(event, email, customer_properties, event_properties)
                response = requests.post('https://a.klaviyo.com/api/track', data=data, headers=headers)
                response.raise_for_status()
                return response

        return (f"Klaviyo event hasn't been send: KLAVIYO_ENABLED: "
                f"{settings.KLAVIYO_ENABLED} or settings.Debug and domain is not one of {settings.DOMAIN_NAMES}")

    @classmethod
    def subscribe_to_list(cls, list_id, profiles):
        return cls.client().Lists.add_subscribers_to_list(list_id, profiles)
