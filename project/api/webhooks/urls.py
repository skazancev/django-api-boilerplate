from rest_framework.routers import DefaultRouter

from .viewsets import WebhookViewSet

app_name = 'webhooks'

router = DefaultRouter()
router.register('', WebhookViewSet, 'webhooks')

urlpatterns = router.urls
