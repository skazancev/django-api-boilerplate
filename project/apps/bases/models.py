from typing import Tuple

from adminsortable.models import SortableMixin
from django.core.exceptions import ValidationError, FieldDoesNotExist, ObjectDoesNotExist
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from model_utils import FieldTracker
from model_utils.models import TimeStampedModel
from slugify import slugify

from utils.fields import OrderField, SlugField
from utils.signals import post_save_queryset
from utils.urls import make_url_absolute


class BaseQuerySet(models.QuerySet):
    def active(self):
        try:
            return self.filter(**{self.model._meta.get_field('is_active').name: True})
        except FieldDoesNotExist:
            return self

    def on_general(self):
        try:
            return self.active().filter(**{self.model._meta.get_field('on_general').name: True})
        except FieldDoesNotExist:
            return self

    def update(self, **kwargs):
        rows = super().update(**kwargs)
        post_save_queryset.send(sender=self.model, created=False,
                                queryset=self, update_fields=list(kwargs.keys()))

        return rows

    def bulk_create(self, *args, **kwargs):
        objs = super().bulk_create(*args, **kwargs)
        post_save_queryset.send(sender=self.model, created=True, queryset=objs)


class BaseModelMeta(models.base.ModelBase):
    @staticmethod
    def _find_order_field(attrs, bases):
        if order := attrs.get('order'):
            return order

        for base in bases:
            try:
                return base._meta.get_field('order')
            except FieldDoesNotExist:
                continue

        return None

    def __new__(mcs, name, bases: Tuple[models.Model], attrs, **kwargs):
        meta = attrs.get('Meta')
        if (not getattr(meta, 'abstract', False) and
                not getattr(meta, 'proxy', False)):
            attrs.setdefault('tracker', FieldTracker())

        apply_order = isinstance(mcs._find_order_field(attrs, bases), OrderField)
        if apply_order and SortableMixin not in bases:
            bases += (SortableMixin,)

        new_class = super().__new__(mcs, name, bases, attrs, **kwargs)

        if apply_order and not new_class._meta.ordering:
            new_class._meta.ordering = ('order',)

        for field in new_class._meta.fields:
            if isinstance(field, (models.ForeignKey, models.OneToOneField)):
                setattr(new_class, f'admin_{field.name}_link', mcs._admin_related_field_link(field))

        return new_class

    @staticmethod
    def _admin_related_field_link(field):

        def method(self):
            try:
                return getattr(self, field.name).admin_url_tag
            except ObjectDoesNotExist:
                return ''
        method.short_description = field.verbose_name

        return method


class BaseModel(TimeStampedModel, metaclass=BaseModelMeta):
    tracker: FieldTracker
    _created: bool
    _metadata: dict

    objects = BaseQuerySet.as_manager()

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._created = False
        self._metadata = {}

    def __str__(self):
        return ' '.join(filter(None, [f'{self._meta.verbose_name}#{self.pk}', str(self.str())]))

    def str(self):
        return ''

    def save_slug(self):
        try:
            field: SlugField = self._meta.get_field('slug')
            if not self.slug:
                self.slug = slugify(getattr(self, field.target))

            index = 1
            while self._meta.default_manager.filter(slug=self.slug).exclude(id=self.id).exists() and index <= 3:
                self.slug = slugify(getattr(self, field.target)) + f'-{index}'
                index += 1
            else:
                if index > 3:
                    raise ValidationError({
                        'slug': _(f'{self._meta.verbose_name} с таким слагом уже сущетсвует: {self.slug}')})

        except FieldDoesNotExist:
            pass

    def after_created(self):
        pass

    def save(self, *args, **kwargs):
        self._created = self._state.adding
        self.save_slug()

        super().save(*args, **kwargs)
        if self._created:
            self.after_created()

    @property
    def admin_url_title(self):
        return self.__str__()

    @property
    def admin_url(self):
        return reverse(f'admin:{self._meta.app_label}_{self._meta.model_name}_change', args=(self.id,))

    @property
    def admin_url_tag(self):
        return mark_safe(f'<a href="{self.admin_url}">{self.admin_url_title}</a>')

    @property
    def full_admin_url(self):
        return make_url_absolute(self.admin_url)

    @property
    def admin_slack_link(self):
        return f'<{self.full_admin_url}|{self.admin_url_title}>'

    def update_metadata(self, **metadata):
        self._metadata.update(**metadata)

    @property
    def _history_user(self):
        return self._metadata.get('user')

    @_history_user.setter
    def _history_user(self, value):
        self.update_metadata(user=value)

    @property
    def _change_reason(self):
        return self._metadata.get('history_change_reason')

    @_change_reason.setter
    def _change_reason(self, value):
        return self.update_metadata(history_change_reason=value)

    @property
    def lastmod(self):
        return self.modified

    @classmethod
    def get_seo_object(cls, **kwargs):
        return cls.objects.get(**kwargs)
