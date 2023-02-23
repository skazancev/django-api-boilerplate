from django.core import validators
from django.forms import fields
from rest_framework import serializers


NUMERIC_FIELD_TYPES = (fields.IntegerField, fields.FloatField, fields.DecimalField, fields.DurationField)


def get_django_form_kwargs(field: fields.Field):
    validator_kwarg = list(field.validators)

    kwargs = {
        'read_only': field.disabled,
        'allow_blank': field.required,
        'allow_null': field.required,
        'label': field.label,
        'help_text': field.help_text,
        'initial': field.initial,
        'required': field.required,
    }

    if isinstance(field, fields.ChoiceField):
        kwargs['choices'] = field.choices

    else:
        max_digits = getattr(field, 'max_digits', None)
        if max_digits is not None:
            kwargs['max_digits'] = max_digits

        decimal_places = getattr(field, 'decimal_places', None)
        if decimal_places is not None:
            kwargs['decimal_places'] = decimal_places

        decimal_places = getattr(field, 'decimal_places', None)
        if decimal_places is not None:
            kwargs['decimal_places'] = decimal_places

        if isinstance(field, fields.SlugField):
            kwargs['allow_unicode'] = field.allow_unicode

        if isinstance(field, fields.FilePathField):
            kwargs['path'] = field.path

            if field.match is not None:
                kwargs['match'] = field.match

            if field.recursive is not False:
                kwargs['recursive'] = field.recursive

            if field.allow_files is not True:
                kwargs['allow_files'] = field.allow_files

            if field.allow_folders is not False:
                kwargs['allow_folders'] = field.allow_folders

        # Ensure that max_value is passed explicitly as a keyword arg,
        # rather than as a validator.
        max_value = next((
            validator.limit_value for validator in validator_kwarg
            if isinstance(validator, validators.MaxValueValidator)
        ), None)
        if max_value is not None and isinstance(field, NUMERIC_FIELD_TYPES):
            kwargs['max_value'] = max_value
            validator_kwarg = [
                validator for validator in validator_kwarg
                if not isinstance(validator, validators.MaxValueValidator)
            ]

        # Ensure that min_value is passed explicitly as a keyword arg,
        # rather than as a validator.
        min_value = next((
            validator.limit_value for validator in validator_kwarg
            if isinstance(validator, validators.MinValueValidator)
        ), None)
        if min_value is not None and isinstance(field, NUMERIC_FIELD_TYPES):
            kwargs['min_value'] = min_value
            validator_kwarg = [
                validator for validator in validator_kwarg
                if not isinstance(validator, validators.MinValueValidator)
            ]

        # URLField does not need to include the URLValidator argument,
        # as it is explicitly added in.
        if isinstance(field, fields.URLField):
            validator_kwarg = [
                validator for validator in validator_kwarg
                if not isinstance(validator, validators.URLValidator)
            ]

        # EmailField does not need to include the validate_email argument,
        # as it is explicitly added in.
        if isinstance(field, fields.EmailField):
            validator_kwarg = [
                validator for validator in validator_kwarg
                if validator is not validators.validate_email
            ]

        # SlugField do not need to include the 'validate_slug' argument,
        if isinstance(field, fields.SlugField):
            validator_kwarg = [
                validator for validator in validator_kwarg
                if validator is not validators.validate_slug
            ]

        # IPAddressField do not need to include the 'validate_ipv46_address' argument,
        if isinstance(field, fields.GenericIPAddressField):
            validator_kwarg = [
                validator for validator in validator_kwarg
                if validator is not validators.validate_ipv46_address
            ]

        # Our decimal validation is handled in the field code, not validator code.
        if isinstance(field, fields.DecimalField):
            validator_kwarg = [
                validator for validator in validator_kwarg
                if not isinstance(validator, validators.DecimalValidator)
            ]

        # Ensure that max_length is passed explicitly as a keyword arg,
        # rather than as a validator.
        max_length = getattr(field, 'max_length', None)
        if max_length is not None and (isinstance(field, (fields.CharField, fields.FileField))):
            kwargs['max_length'] = max_length
            validator_kwarg = [
                validator for validator in validator_kwarg
                if not isinstance(validator, validators.MaxLengthValidator)
            ]

    # Ensure that min_length is passed explicitly as a keyword arg,
    # rather than as a validator.
    min_length = next((
        validator.limit_value for validator in validator_kwarg
        if isinstance(validator, validators.MinLengthValidator)
    ), None)
    if min_length is not None and isinstance(field, fields.CharField):
        kwargs['min_length'] = min_length
        validator_kwarg = [
            validator for validator in validator_kwarg
            if not isinstance(validator, validators.MinLengthValidator)
        ]

    if validator_kwarg:
        kwargs['validators'] = validator_kwarg

    return kwargs


# unsupported fields
# 'ComboField',
# 'MultiValueField',
django_drf_fields_map = {
    fields.CharField: serializers.CharField,
    fields.BooleanField: serializers.BooleanField,
    fields.NullBooleanField: serializers.BooleanField,
    fields.ChoiceField: serializers.ChoiceField,
    fields.TypedChoiceField: serializers.ChoiceField,
    fields.MultipleChoiceField: serializers.MultipleChoiceField,
    fields.TypedMultipleChoiceField: serializers.MultipleChoiceField,
    fields.FileField: serializers.FileField,
    fields.ImageField: serializers.ImageField,
    fields.EmailField: serializers.EmailField,
    fields.URLField: serializers.URLField,
    fields.SlugField: serializers.SlugField,
    fields.UUIDField: serializers.UUIDField,
    fields.IntegerField: serializers.IntegerField,
    fields.FloatField: serializers.FloatField,
    fields.DecimalField: serializers.DecimalField,
    fields.DateTimeField: serializers.DateTimeField,
    fields.DateField: serializers.DateField,
    fields.TimeField: serializers.TimeField,
    fields.DurationField: serializers.DurationField,
    fields.GenericIPAddressField: serializers.IPAddressField,
    fields.RegexField: serializers.RegexField,
    fields.FilePathField: serializers.FilePathField,
    fields.JSONField: serializers.JSONField,
}
