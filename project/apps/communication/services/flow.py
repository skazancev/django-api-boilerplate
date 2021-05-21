import logging
from datetime import timedelta
from functools import cached_property

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.utils import timezone

from apps.communication.models import Flow
from utils.urls import get_base_url
from . import flow_event
from . import user_flow as user_flow_services
from ...bases.models import BaseModel, BaseQuerySet
from .. import model_serializers as serializers
logger = logging.getLogger(__name__)


class Context:
    def __init__(self, context):
        self.context = context

    @cached_property
    def serializers_map(self) -> dict:
        return {
            get_user_model(): serializers.UserSerializer,
        }

    def prepare_model_data(self, model, instance, *args, **kwargs):
        serializer_class = self.serializers_map.get(model, serializers.BaseInstanceSerializer)
        return serializer_class(instance, *args, **kwargs).data

    def perform(self):
        for key, value in self.context.items():
            if isinstance(value, BaseModel):
                self.context[key] = self.prepare_model_data(value.__class__, value)
            elif isinstance(value, BaseQuerySet):
                self.context[key] = self.prepare_model_data(value.model, value, many=True)

        site = Site.objects.get_current()
        return {
            **self.context,
            'website': {
                'name': site.name,
                'url': site.domain,
                'base_url': get_base_url(),
            },
        }


def trigger_flow_event(event, user, context=None, start_date=None, trigger_type=None, **metadata):
    flow = find_by_event(event)
    if not flow:
        return

    # if start_date is specified find last flow action and check if it still is actual to send
    is_active = not start_date or timezone.now() <= start_date + timedelta(
        seconds=flow.actions.last().delay_seconds,
    )
    if is_active:
        user_flow = user_flow_services.create(
            flow=flow,
            user=user,
            context=Context(context or {}).perform(),
            start_date=start_date,
            trigger_type=trigger_type,
            **metadata,
        )
        user_flow_services.trigger(user_flow)
        return user_flow


def find_by_event(event_name):
    event = flow_event.get_event(event_name)
    flow = Flow.objects.filter(event=event).first()
    if not flow:
        logger.warning(f'No flow found for event: {event_name}')

    return flow
