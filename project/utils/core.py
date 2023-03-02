from contextlib import contextmanager

import functools
from typing import Any

from django.db.models import Model, ForeignKey, OneToOneField, Empty


sensitive_fields = [
    'magic_link',
    'new_password'
]


def rgetattr(obj, attr, default=None, ignore_errors=True):
    # noinspection PyShadowingNames
    def _getattr(obj, attr):
        if isinstance(obj, Model) and (field := obj._meta._forward_fields_map.get(attr, None)):
            # try to get fk or o2o id field value to prevent unnecessary database request
            if isinstance(field, (ForeignKey, OneToOneField)) and not getattr(obj, field.attname):
                return default

        try:
            return getattr(obj, attr)
        except Exception as e:
            if ignore_errors:
                return default

            raise e

    return functools.reduce(_getattr, [obj] + attr.split('.'))


def recursive_get(d, *keys, default=None):
    try:
        return functools.reduce(lambda c, k: c.get(k, {}), keys, d) or default
    except AttributeError:
        return default


@contextmanager
def override_attribute(obj, attr_name, value, apply=True):
    old_value = getattr(obj, attr_name, Empty())

    if apply:
        setattr(obj, attr_name, value)

    yield

    if isinstance(old_value, Empty):
        delattr(obj, attr_name)
    else:
        setattr(obj, attr_name, old_value)


class Dict(dict):
    @classmethod
    def convert(cls, data):
        if isinstance(data, dict):
            return cls(data)
        elif isinstance(data, list):
            return [cls.convert(i) for i in data]
        return data

    def get(self, item, default=None):
        value = super().get(item, default)
        return self.convert(value)

    def __getattr__(self, item):
        value = self.get(item)
        return self.convert(value)

    def __setattr__(self, key, value):
        self[key] = value


def clean_data(data: Any, remove_fields: list = None, replace_with=None):
    remove_fields = remove_fields or sensitive_fields
    recursion = functools.partial(clean_data, remove_fields=remove_fields, replace_with=replace_with)
    if isinstance(data, dict):
        for key, value in data.items():
            if remove_fields and key in remove_fields:
                value = replace_with

            data[key] = recursion(value)

    elif isinstance(data, (list, tuple, set)):
        data = [recursion(item) for item in data]
    else:
        data = str(data)

    return data
