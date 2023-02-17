from drf_yasg import openapi
from rest_framework import status
from rest_framework.decorators import action

from api import messages
from api.accounts import serializers
from api.permissions import AnonymousOnly
from api.viewsets import GenericViewSet, serializer


class AuthViewSet(GenericViewSet):
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
