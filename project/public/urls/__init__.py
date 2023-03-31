from django.http import HttpResponseNotFound
from django.urls import path, include

from utils.urls import build_public_url
from . import system


app_name = 'public'


def http404_view(request, *args, **kwargs):  # pragma: no cover
    return HttpResponseNotFound()


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
    path('s/', include('public.urls.system', namespace='system')),
]
