import time

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny

from api.viewsets import GenericViewSet
from api.serializers import Serializer


class UtilsViewSet(GenericViewSet):
    permission_classes = (AllowAny,)
    serializer_class = Serializer

    @action(detail=False)
    @swagger_auto_schema(responses={200: openapi.Response('Server health', examples={
        'application/json': {
            'status': 'ok',
            'timestamp': 1586978220,
        }
    })})
    def health(self, request):
        return self.response({
            'status': 'ok',
            'timestamp': int(time.time())
        })

    @action(detail=False)
    @swagger_auto_schema(responses={200: openapi.Response('Ping server', examples={
        'application/json': 'pong'
    })})
    def ping(self, request):
        return self.response('pong')
