import copy
import json
from datetime import datetime

from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site

from apps.communication.models import Template, CommunicationHistory
from utils.core import clean_data
from utils.urls import get_base_url
from .. import model_serializers as serializers

User = get_user_model()


def get_serializers_map() -> dict:
    return {
        User: serializers.UserSerializer,
    }


def perform_context(context):
    for key, value in context.items():
        try:
            if isinstance(value, (list, set, tuple)) and len(value) == 2 and (model := apps.get_model(value[0])):
                if isinstance(value[1], (str, int)):
                    id_list = [value[1]]
                else:
                    id_list = value[1]
                if queryset := model.objects.filter(id__in=id_list):
                    if serializer_class := get_serializers_map().get(model):
                        many = isinstance(value[1], (list, set, tuple))
                        if not many:
                            queryset = queryset.last()
                        context[key] = serializer_class(queryset, many=many).data
                    else:
                        context[key] = queryset
                else:
                    context[key] = value

            if isinstance(value, str) and value.startswith('_date-'):
                value = datetime.fromisoformat(value[6:])
                value_time = value.time()
                if not any([value_time.hour, value_time.minute, value_time.second]):
                    value = value.date()

                context[key] = value

        except (ValueError, LookupError):
            pass

    if 'website' not in context:
        site = Site.objects.get_current()
        context['website'] = {
            'name': site.name,
            'url': site.domain,
            'base_url': get_base_url(),
        }

    return context


def generate(*,
             communication_user_id,
             template: Template = None,
             context=None,
             communication_type=CommunicationHistory.Type.automatic,
             communication_agent_id=None,
             **meta,
             ):
    if not (user := User.objects.filter(id=communication_user_id).first()):
        return

    context = perform_context(context or dict())

    if communication := CommunicationHistory.generate(
            user=user,
            type=communication_type,
            target=template.helper.target,
            agent_id=communication_agent_id,
            template_type=template.type,
            template_vendor=template.vendor,
            meta={
                'template_id': template.id,
                'vendor_template_id': template.helper.get_id(user),
                **meta,
            },
            context=context,
    ):
        communication.save()
        return communication


def generate_hash(data: dict, remove_fields=None):
    return json.dumps(clean_data(copy.deepcopy(data), remove_fields=remove_fields, replace_with='-'))
