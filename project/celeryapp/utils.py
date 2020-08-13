import json
from collections import abc
from datetime import date
from decimal import Decimal
from typing import Any

from django.db.models import Model, QuerySet
from kombu.serialization import register


class JSONEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, Model):
            return [str(obj._meta.label_lower), obj.pk]
        if isinstance(obj, QuerySet):
            return [str(obj.model._meta.label_lower), list(obj.values_list('pk', flat=True))]
        if isinstance(obj, abc.KeysView):
            return list(obj)
        if isinstance(obj, date):
            return f'_date-{obj.isoformat()}'
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, bytes):
            return obj.decode()

        return super().default(obj)


def json_dumps(obj):
    try:
        return json.dumps(obj, cls=JSONEncoder)
    except Exception as e:
        raise e


register(
    'junejson',
    json_dumps,
    json.loads,
    content_type='application/x-junejson',
    content_encoding='utf-8',
)
