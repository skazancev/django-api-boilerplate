import hashlib
import logging
from typing import Optional

import requests
import xmltodict

from collections import OrderedDict

from urllib.parse import urljoin

from django.conf import settings
from django.urls import reverse
from django.utils.crypto import get_random_string

from project.apps.orders.models import Order, PayBoxPayment
from project.utils.urls import get_base_url, make_url_absolute, build_public_url

logger = logging.getLogger(__name__)


class PayBoxError(Exception):
    def __init__(self, msg, response=None):
        self.msg = msg
        self.response = response

    def __str__(self):
        return self.msg


class PayBoxClient:
    def get_redirect_url(self, order, status: str):
        return build_public_url('frontend_journey', args=(order.journey_id,))

    def send_request(self, method, http_method='POST', attempt=1, **kwargs):
        if http_method == 'POST' and 'pg_sig' not in kwargs.get('data', {}):
            kwargs['data'] = self.prepare_post_data(kwargs['data'], method)
        kwargs.setdefault('timeout', 20)

        response = None
        try:
            response = requests.request(http_method, urljoin(settings.PAYBOX_BASE_URL, method), **kwargs)
        except (requests.ConnectionError, requests.RequestException) as e:
            if attempt > 3:
                raise PayBoxError(f'Cannot send request: {e}')

        if response and response.status_code == 200:
            return xmltodict.parse(response.content)['response']

        if attempt <= 3:
            return self.send_request(method, http_method, attempt=attempt + 1, **kwargs)

        raise PayBoxError(f'Cannot send request: {response.content if response else "no response"}', response=response)

    def generate_signature(self, url, data: dict):
        payload = [
            url.rsplit('/', maxsplit=1)[-1],
            *[str(value) for _, value in sorted(data.items(), key=lambda i: i[0])],
            settings.PAYBOX_ACCEPTANCE_SECRET_KEY,
        ]

        return hashlib.md5(';'.join(payload).encode()).hexdigest()

    def prepare_post_data(self, data, method):
        if settings.PAYBOX_TESTING_MODE:
            data['pg_testing_mode'] = 1

        data['pg_salt'] = get_random_string(32)
        data['pg_sig'] = self.generate_signature(method, data)
        return data

    def init_payment(self, order: Order) -> Optional[PayBoxPayment]:
        data = OrderedDict({
            'pg_amount': order.line.amount,
            'pg_currency': order.line.plan.currency.code,
            'pg_description': order.line.target_object.title,
            'pg_merchant_id': settings.PAYBOX_MERCHANT_ID,
            'pg_order_id': order.uid,
            'pg_result_url': make_url_absolute(
                reverse('api:webhooks:webhooks-paybox', args=('payment',)),
                base_url=settings.WEBHOOKS_BASE_URL,
            ),
            'pg_user_contact_email': order.user.email,
            'pg_success_url': build_public_url('system:process-paybox-redirect', args=(order.journey_id,)),
            'pg_failure_url': build_public_url('system:process-paybox-redirect', args=(order.journey_id,)),
            'pg_success_url_method': 'POST',
            'pg_failure_url_method': 'POST',
            'pg_site_url': get_base_url(),
            'pg_payment_system': order.payment_method.paybox_code,
        })
        if order.user.phone and order.user.phone.is_valid():
            data['pg_user_phone'] = order.user.phone.as_e164

        defaults = dict(
            order=order,
            amount=data['pg_amount'],
            status=PayBoxPayment.Status.pending,
            pg_payment_system=data['pg_payment_system'],
        )
        if exist_payment := PayBoxPayment.objects.filter(**defaults).first():
            return exist_payment

        response = self.send_request('init_payment.php', data=data)
        if response['pg_status'] == 'ok':
            return PayBoxPayment.objects.create(
                **defaults,
                payment_id=response['pg_payment_id'],
                pg_redirect_url=response['pg_redirect_url'],
            )
        else:
            logger.warning(response)

    def cancel_pending_order(self, order: Order):
        data = OrderedDict({
            'pg_merchant_id': settings.PAYBOX_MERCHANT_ID,
            'pg_payment_id': order.paybox_payment_id,
        })
        return self.send_request('cancel.php', data=data)

    def get_payment_methods(self):
        response = self.send_request('ps_list.php', data={'pg_merchant_id': settings.PAYBOX_MERCHANT_ID})
        return response['pg_payment_system']

    def save_card(self, user_id, card_name, card_number, card_cvc, card_year, card_month):
        data = OrderedDict({
            'pg_merchant_id': settings.PAYBOX_MERCHANT_ID,
            'pg_user_id': user_id,
            'pg_card_name': card_name,
            'pg_card_pan': card_number,
            'pg_card_cvc': card_cvc,
            'pg_card_year': card_year,
            'pg_card_month': card_month,
        })
        return self.send_request('/g2g/cardstorage/add', data=data)
