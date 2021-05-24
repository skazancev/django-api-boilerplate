import urllib.parse

from django.conf import settings
from django.contrib.sites.models import Site
from django.http import HttpResponseNotFound
from django.urls import reverse, path


app_name = 'public'


def http404_view(request, *args, **kwargs):  # pragma: no cover
    return HttpResponseNotFound()


def get_base_url():
    return f'{settings.BASE_URL_SCHEMA}://{Site.objects.get_current().domain}'


def make_url_absolute(url):
    return urllib.parse.urljoin(get_base_url(), url)


def build_public_url(url_name, **kwargs):
    return make_url_absolute(reverse(f'public:{url_name}', **kwargs))


def password_reset_by_token_url(*, uidb36, token):
    return build_public_url('password_reset_by_token_url', kwargs={
        'uidb36': uidb36,
        'token': token
    })


def account_email_confirm_url(*, uidb36, token):
    return build_public_url('account_email_confirm', kwargs={
        'uidb36': uidb36,
        'token': token
    })


urlpatterns = [
    path('password/reset/<slug:uidb36>-<slug:token>', http404_view, name='password_reset_by_token_url'),
    path('accounts/email/confirm/<slug:uidb36>-<slug:token>', http404_view, name='account_email_confirm'),
]
