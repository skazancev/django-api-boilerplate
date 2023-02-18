import json

from django.db import transaction
from django.utils.decorators import method_decorator
from ipware import get_client_ip

from rest_framework.decorators import action as rest_action
from rest_framework.parsers import FormParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.webhooks import clients
from apps.webhooks.models import WebhookData
from project.api.utils.viewsets import GenericViewSet


@method_decorator(transaction.non_atomic_requests, name='dispatch')
class WebhookViewSet(GenericViewSet):
    permission_classes = (AllowAny,)

    def save_webhook(self, source, payload=None):
        return WebhookData.objects.create(
            source=source,
            content=payload or self.request.data,
            remote_ip=get_client_ip(self.request)[0]
        )

    @rest_action(detail=False, methods=['POST'], parser_classes=(FormParser,))
    def slack(self, request):
        response_data = clients.SlackBotClient(
            self.save_webhook(WebhookData.Sources.slack, json.loads(request.data['payload']))
        ).process()
        return self.response(response_data)

    @rest_action(detail=False, methods=['POST', 'GET'], url_path='facebook/whatsapp')
    def facebook_whatsapp(self, request):
        if request.method == 'GET':
            data = request.GET.dict()
        else:
            data = request.data
        response = clients.WhatsappClient(
            self.save_webhook(WebhookData.Sources.facebook_whatsapp, payload=data)
        ).process()
        return Response(response)
