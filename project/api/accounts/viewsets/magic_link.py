from django.http import HttpResponseRedirect
from rest_framework.decorators import action

from api import messages
from api.accounts import serializers
from api.permissions import AnonymousOnly
from api.viewsets import GenericViewSet, serializer


class MagicLinkAuthViewSet(GenericViewSet):
    @serializer(serializers.MagicLinkSerializer, swagger_schema={
        'methods': ['post', 'get']
    })
    @action(detail=False, methods=['post', 'get'], permission_classes=(AnonymousOnly,))
    def login(self, request):
        validated = self.validate_request(request)
        validated.save()

        return HttpResponseRedirect(request.GET.get('next', '/'))

    @serializer(serializers.MagicLinkSendSerializer)
    @action(detail=False, methods=['post'], permission_classes=(AnonymousOnly,))
    def send(self, request):
        validated = self.validate_request(request)
        validated.save()

        return self.response({'status': messages.STATUS_OK, 'email': validated.user.email})
