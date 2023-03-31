from urllib import parse

from django.urls import reverse
from django.utils.http import int_to_base36

from public.urls import password_reset_by_token_url
from apps.accounts.tokens import user_token_generator
from utils.urls import make_url_absolute


def get_reset_url(user, next_url='', **kwargs):
    reset_url_kwargs = {
        'uidb36': int_to_base36(user.id),
        'token': user_token_generator.make_token(user),
    }
    if next_url:
        kwargs['next'] = next_url

    password_reset_url = password_reset_by_token_url(**reset_url_kwargs)
    if kwargs:
        password_reset_url += f'?{parse.urlencode(kwargs)}'

    return password_reset_url


def get_magic_link(user, next_url='/', one_off=True, **kwargs):
    magic_link_url = make_url_absolute(
        reverse('api:accounts:password_magic_link-login')
        + f'?token={int_to_base36(user.id)}-{user_token_generator.make_token(user, one_off=one_off)}'
    )
    if next_url:
        kwargs['next'] = next_url

    return magic_link_url + f'?{parse.urlencode(kwargs)}'
