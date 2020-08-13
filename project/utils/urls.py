from urllib.parse import urljoin

from django.conf import settings
from django.contrib.sites.models import Site
from django.urls import reverse


def get_base_url():
    return f'{settings.BASE_URL_SCHEMA}://{Site.objects.get_current().domain}'


def make_url_absolute(url):
    return urljoin(get_base_url(), url)


def build_public_url(url_name, **kwargs):
    return make_url_absolute(reverse(f'public:{url_name}', **kwargs))
