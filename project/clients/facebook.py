import json

import requests
from django.conf import settings
from phonenumber_field.phonenumber import PhoneNumber

from apps.core.models import Config
from project.apps.facebook.whatsapp.models import WhatsAppPhoneNumber
from project.apps.facebook.whatsapp.services import get_default_phone_number
from utils.core import recursive_get, Dict


class WhatsAppError(Exception):
    def __init__(self, data):
        self.data = data


class WhatsAppResponseError(requests.HTTPError):
    def __init__(self, message, response):
        try:
            self.response_json = response.json()
            message = recursive_get(self.response_json, 'error', 'message', default=message)
        except json.JSONDecodeError:
            self.response_json = None

        super().__init__(message, response=response)


class MessageTemplateParameters:
    COMPONENT_HEAD = 'head'
    COMPONENT_BODY = 'body'
    COMPONENT_FOOTER = 'footer'

    def __init__(self, component, parameters):
        self.component = component
        self.parameters = parameters

    def get_request_payload(self):
        if self.parameters:
            return {
                'type': self.component,
                'parameters': self.parameters,
            }


class WhatsAppMessageReceiver:
    TYPE_TEMPLATE = 'template'
    TYPE_TEXT = 'text'

    def __init__(
        self,
        phone_number,
        from_phone_number=None,
        message=None,
        template_name=None,
        template_language='ru',
        template_head_parameters=None,
        template_body_parameters=None,
        template_footer_parameters=None,
    ):
        if isinstance(phone_number, PhoneNumber):
            phone_number = phone_number.as_e164[1:]  # cut + from the beginning of the phone number

        self.phone_number = phone_number
        self.message = message
        self.template_name = template_name
        self.type = self.TYPE_TEMPLATE if template_name else self.TYPE_TEXT
        self.template_language = template_language
        self.template_head_parameters = MessageTemplateParameters(
            MessageTemplateParameters.COMPONENT_HEAD,
            template_head_parameters,
        )
        self.template_body_parameters = MessageTemplateParameters(
            MessageTemplateParameters.COMPONENT_BODY,
            template_body_parameters,
        )
        self.template_footer_parameters = MessageTemplateParameters(
            MessageTemplateParameters.COMPONENT_FOOTER,
            template_footer_parameters,
        )
        self.from_phone_number: WhatsAppPhoneNumber = from_phone_number or get_default_phone_number()

    def get_text_body(self) -> dict:
        return {
            'text': {
                'body': self.message,
            }
        }

    def get_template_body(self) -> dict:
        components = []
        for params in [self.template_head_parameters, self.template_body_parameters, self.template_footer_parameters]:
            if request_payload := params.get_request_payload():
                components.append(request_payload)

        return {
            'template': {
                'name': self.template_name,
                'language': {
                    'code': self.template_language,
                },
                'components': components,
            }
        }

    def get_request_payload(self):
        payload = {
            'messaging_product': 'whatsapp',
            'to': self.phone_number,
            'type': self.type,
        }
        if self.type == self.TYPE_TEMPLATE:
            payload.update(self.get_template_body())
        else:
            payload.update(self.get_text_body())

        return payload


class WhatsAppClient:
    api_version = 'v15.0'

    def send_request(self, method, http_method='GET', **kwargs):
        url = f'https://graph.facebook.com/{self.api_version}/{method}'
        kwargs['headers'] = {
            'Authorization': f'Bearer {settings.FACEBOOK_SERVER_USER_TOKEN}'
        }
        response = requests.request(http_method, url, **kwargs)
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            raise WhatsAppResponseError(str(e), e.response)

        return Dict(response.json())

    def build_business_account_url(self, path):
        # US 109918075336417
        # KG 100255872639316
        return f'{Config.get(Config.Type.whatsapp_business_account_id)}{path}'

    def send_message(self, receiver: WhatsAppMessageReceiver):
        if receiver.phone_number == 'invalid':
            raise WhatsAppError({'status': 'not sent'})

        return self.send_request(
            f'{receiver.from_phone_number.vendor_id}/messages',
            http_method='POST',
            json=receiver.get_request_payload()
        )

    def retrieve_all_paging_data(self, method, **kwargs):
        response: Dict = method(**kwargs)
        items: list = response.data
        if recursive_get(response, 'paging', 'next', default=None):
            kwargs['after'] = response.paging.cursors.after
            items.extend(self.retrieve_all_paging_data(method, **kwargs))
        return items

    def get_message_templates(self, **params):
        params.setdefault('limit', 100)
        return self.send_request(
            self.build_business_account_url('/message_templates'),
            http_method='GET',
            params=params,
        )

    def get_phone_numbers(self, **params):
        return self.send_request(
            self.build_business_account_url('/phone_numbers'),
            http_method='GET',
            params=params,
        )
