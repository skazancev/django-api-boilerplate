import json
from collections import abc
from datetime import date
from decimal import Decimal
from typing import Any

from django.db import models
from django.db.models import Model, QuerySet
from phonenumber_field.phonenumber import PhoneNumber


class JSONEncoder(json.JSONEncoder):
    def __init__(self, *args, date_prefix=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.date_prefix = date_prefix

    def default(self, obj: Any) -> Any:
        if isinstance(obj, Model):
            return [str(obj._meta.label_lower), obj.pk]
        if isinstance(obj, QuerySet):
            return [str(obj.model._meta.label_lower), list(obj.values_list('pk', flat=True))]
        if isinstance(obj, abc.KeysView):
            return list(obj)
        if isinstance(obj, date):
            if self.date_prefix:
                return f'_date-{obj.isoformat()}'
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, PhoneNumber):
            return obj.as_e164 if obj.is_valid() else str(obj)

        return super().default(obj)


class DurationCountSubquery(models.Subquery):
    template = "(SELECT COALESCE(SUM(duration), 0) FROM (%(subquery)s) _count)"
    output_field = models.IntegerField()


class SQCount(models.Subquery):
    template = "(SELECT count(*) FROM (%(subquery)s) _count)"
    output_field = models.IntegerField()


class SQSum(models.Subquery):
    template = "(SELECT COALESCE(SUM(%(field)s), 0) FROM (%(subquery)s) _sum)"
    output_field = models.IntegerField()
