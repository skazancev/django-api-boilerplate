from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core import checks
from django.db import models
from django.db.models import BLANK_CHOICE_DASH
from django.db.models.fields.files import FieldFile
from django.urls import reverse

from utils.cache import custom_lru_cache
from utils.storages import PrivateFileSystemStorage
from utils.timezone import round_time


class OrderField(models.PositiveIntegerField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('default', 0)
        kwargs.setdefault('db_index', True)
        kwargs.setdefault('editable', False)
        super().__init__(*args, **kwargs)


class ActiveField(models.BooleanField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('default', True)
        kwargs.setdefault('verbose_name', _('Активный'))
        kwargs['db_index'] = True
        super().__init__(*args, **kwargs)


class SlugField(models.SlugField):
    def __init__(self, *args, **kwargs):
        self.target = kwargs.pop('target', None)
        super().__init__(*args, **kwargs)

    def check(self, **kwargs):
        errors = super().check(**kwargs)
        if not self.target:
            errors.append(checks.Error(
                "SlugField must define a 'target' attribute.",
                obj=self,
            ))
        elif not isinstance(self.target, str):
            errors.append(checks.Error(
                f"'target' must be str instead of {type(self.target)}.",
                obj=self,
            ))

        return errors


class DynamicChoiceField(models.CharField):
    def __init__(self, method=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.get_choices_method = method

    @custom_lru_cache(seconds=settings.DYNAMIC_CHOICE_FIELD_OPTIONS_CACHE)
    def get_choices(self, include_blank=True, blank_choice=BLANK_CHOICE_DASH, *args, **kwargs):
        choices = list(getattr(self.model, self.get_choices_method)())
        if include_blank:
            blank_defined = any(choice in ('', None) for choice, _ in self.flatchoices)
            if not blank_defined:
                choices = blank_choice + choices
        return choices

    @property
    def flatchoices(self):
        return self.get_choices(include_blank=False)

    def validate(self, value, model_instance):
        if value in dict(self.flatchoices):
            return

        return super().validate(value, model_instance)


class RoundedDateTimeField(models.DateTimeField):
    def to_python(self, value):
        return round_time(super().to_python(value))


class RoundedTimeField(models.TimeField):
    def to_python(self, value):
        return round_time(super().to_python(value))


class ChoiceField(models.CharField):
    def __init__(self, choices, *args, **kwargs):
        kwargs['max_length'] = max(len(value) for value, _ in choices)
        super().__init__(choices=choices, *args, **kwargs)

    @staticmethod
    def _is_FIELD_VALUE(name, value):
        @property
        def method(self):
            return getattr(self, name) == value

        return method

    def contribute_to_class(self, cls, name, *args, **kwargs):
        for code, label in self.choices:
            setattr(cls, f'is_{name}_{code}', self._is_FIELD_VALUE(name, code))
        super().contribute_to_class(cls, name, *args, **kwargs)


class PrivateFieldFile(FieldFile):
    @property
    def url(self):
        return reverse(
            'public:system:private_file',
            args=(
                ContentType.objects.get_for_model(self.instance).id,
                self.instance.pk,
                self.field.name,
                self.filename,
            )
        )

    @property
    def real_url(self):
        return super().url

    @property
    def filename(self):
        return self.name.rsplit('/', maxsplit=1)[-1]


class PrivateFileField(models.FileField):
    """
    nginx config example:
    location /media/private {
        internal;
        alias /path/to/media/private/;
        expires 7d;
    }
    """
    attr_class = PrivateFieldFile

    def __init__(self, storage=None, **kwargs):
        storage = PrivateFileSystemStorage()
        super().__init__(storage=storage, **kwargs)
