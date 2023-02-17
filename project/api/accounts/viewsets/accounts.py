from django.db import transaction
from django.utils.decorators import method_decorator
from rest_framework.decorators import action

from api.viewsets import GenericViewSet, serializer
from .. import serializers


@method_decorator(transaction.non_atomic_requests, 'dispatch')
class AccountsViewSet(GenericViewSet):
    @serializer(serializers.UserSerializer)
    @action(detail=False, methods=['get'])
    def me(self, request):
        return self.response(request.user)

    @serializer(serializers.UserSerializer)
    @action(detail=False, methods=['put'], url_path='update')
    def update_account(self, request, *args, **kwargs):
        validated = self.validate_request(request, instance=request.user)

        return self.response(validated.save())
