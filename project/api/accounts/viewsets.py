from django.db import transaction
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from rest_framework import status
from rest_framework.decorators import action

from api import messages
from api.permissions import AnonymousOnly
from api.viewsets import GenericViewSet, serializer
from . import serializers


@method_decorator(transaction.non_atomic_requests, 'dispatch')
class AccountsViewSet(GenericViewSet):
    @serializer(serializers.TokenSerializer, validator=serializers.LoginSerializer)
    @action(detail=False, methods=['post'], permission_classes=(AnonymousOnly,))
    def login(self, request, *args, **kwargs):
        validated = self.validate_request(request)

        return self.response(validated.save())

    @serializer(serializers.TokenSerializer, validator=serializers.SignUpSerializer)
    @action(detail=False, methods=['post'], permission_classes=(AnonymousOnly,))
    def signup(self, request, *args, **kwargs):
        validated = self.validate_request(request)

        return self.response(validated.save())

    @serializer(serializers.UserSerializer)
    @action(detail=False, methods=['get'])
    def me(self, request):
        return self.response(request.user)

    @serializer(serializers.UserSerializer)
    @action(detail=False, methods=['put'], url_path='update')
    def update_account(self, request, *args, **kwargs):
        validated = self.validate_request(request, instance=request.user)

        return self.response(validated.save())

    @serializer(serializers.PasswordChangeSerializer, swagger_schema={
        'responses': {
            200: openapi.Response(
                description='Change password',
                examples={'application/json': {'status': messages.STATUS_OK}}
            )
        }
    })
    @action(detail=False, methods=['post'], url_path='password/change',)
    def password_change(self, request, *args, **kwargs):
        validated = self.validate_request(request)
        validated.save()

        return self.response({"status": messages.STATUS_OK})

    @action(detail=False, url_path='password/reset', methods=['post'], permission_classes=(AnonymousOnly,))
    @serializer(serializers.PasswordResetSerializer)
    def password_reset(self, request, *args, **kwargs):
        validated = self.validate_request(request)
        validated.save()

        return self.response({'status': messages.STATUS_OK})

    @action(detail=False, url_path='password/reset/key', methods=['post'], permission_classes=(AnonymousOnly,))
    @serializer(serializers.PasswordResetConfirmSerializer)
    def password_reset_confirm(self, request, *args, **kwargs):
        validated = self.validate_request(request)
        validated.save()

        return self.response({'status': messages.STATUS_OK})

    @serializer(serializers.EmailConfirmSerializer, swagger_schema={
        'responses': {
            200: openapi.Response(
                description='Confirm email',
                examples={'application/json': {'status': messages.STATUS_OK}}
            )
        }
    })
    @action(detail=False, methods=['post'], url_path='email/confirm', permission_classes=(AnonymousOnly,))
    def email_confirm(self, request, *args, **kwargs):
        validated = self.validate_request(request)
        validated.save()

        return self.response({'status': messages.STATUS_OK})

    @action(detail=False, methods=['post'])
    def logout(self, request):
        return self.response(status=status.HTTP_204_NO_CONTENT)
