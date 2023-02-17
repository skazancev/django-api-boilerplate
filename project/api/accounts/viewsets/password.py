from drf_yasg import openapi
from rest_framework.decorators import action

from api import messages
from api.accounts import serializers
from api.permissions import AnonymousOnly
from api.viewsets import GenericViewSet, serializer


class PasswordAuthViewSet(GenericViewSet):
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

    @serializer(serializers.PasswordChangeSerializer, swagger_schema={
        'responses': {
            200: openapi.Response(
                description='Change password',
                examples={'application/json': {'status': messages.STATUS_OK}}
            )
        }
    })
    @action(detail=False, methods=['post'], url_path='change',)
    def password_change(self, request, *args, **kwargs):
        validated = self.validate_request(request)
        validated.save()

        return self.response({"status": messages.STATUS_OK})

    @serializer(serializers.PasswordResetSerializer)
    @action(detail=False, url_path='reset/send', methods=['post'], permission_classes=(AnonymousOnly,))
    def password_reset(self, request, *args, **kwargs):
        validated = self.validate_request(request)
        validated.save()

        return self.response({'status': messages.STATUS_OK})

    @serializer(serializers.TokenSerializer, validator=serializers.PasswordResetConfirmSerializer)
    @action(detail=False, url_path='reset/confirm', methods=['post'], permission_classes=(AnonymousOnly,))
    def password_reset_confirm(self, request, *args, **kwargs):
        validated = self.validate_request(request)
        validated.save()

        return self.response({'status': messages.STATUS_OK})
