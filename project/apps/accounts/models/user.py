from urllib import parse

from django.contrib.auth import login as django_login
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin, Group as DjangoGroup
from django.contrib.postgres.fields import CIEmailField
from django.db import models
from django.utils.http import int_to_base36
from ipware import get_client_ip
from phonenumber_field.modelfields import PhoneNumberField
from simple_history.models import HistoricalRecords

from apps.accounts import signals
from apps.accounts.tokens import user_token_generator
from apps.bases.models import BaseModel
from utils.fields import ActiveField
from utils.urls import build_public_url


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

    def get_by_natural_key(self, email):
        return self.get(email=email)


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    email = CIEmailField(unique=True, verbose_name=_('Адрес эл. почты'))
    first_name = models.CharField(max_length=100, null=True, blank=True,  verbose_name=_('Имя'))
    last_name = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('Фамилия'))
    phone = PhoneNumberField(null=True, blank=False, verbose_name=_('Номер телефона'))

    is_active = ActiveField()
    is_email_verified = models.BooleanField(default=False, verbose_name=_('Подтвержденный адрес эл. почты?'))
    is_staff = models.BooleanField(default=False, verbose_name=_('Статус персонала'))

    objects = UserManager()
    history = HistoricalRecords()

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')

    def str(self):
        return self.email

    def clean(self):
        super().clean()

        self.email = self.__class__.objects.normalize_email(self.email)

    @property
    def name(self):
        if self.last_name and self.first_name:
            res = " ".join((self.first_name, self.last_name))
        else:
            res = self.first_name if self.first_name else self.last_name

        return res or ''

    @name.setter
    def name(self, value):
        sp_value = value.split(" ", 1)
        if len(sp_value) == 2:
            self.first_name, self.last_name = sp_value
        else:
            self.first_name = value

    @property
    def pretty_email(self):
        return f'{self.name} <{self.email}>'

    def login_from_request(self, request, created=False, is_endless=False):
        django_login(request, self)

        if created:
            signal = signals.user_signed_up
        else:
            signal = signals.user_logged_in

        signal.send(sender=self.__class__, request=request, user=self)

        ip_address = get_client_ip(request)[0]
        user_agent = request.META['HTTP_USER_AGENT']

        return self.create_login_token(is_endless, ip_address, user_agent)

    def create_login_token(self, is_endless=False, ip_address='', user_agent=''):
        from apps.accounts.models import Token

        return Token.create(self, is_endless=is_endless, ip_address=ip_address, user_agent=user_agent)

    def change_password(self, password):
        self.set_password(password)
        self.save()

        signals.password_changed.send(sender=self.__class__, user=self)

    def get_reset_url(self, next_url='', **kwargs):
        from public_urls import password_reset_by_token_url
        from apps.accounts.tokens import user_token_generator

        reset_url_kwargs = {
            'uidb36': int_to_base36(self.id),
            'token': user_token_generator.make_token(self),
        }
        if next_url:
            kwargs['next'] = next_url

        password_reset_url = password_reset_by_token_url(**reset_url_kwargs)
        if kwargs:
            password_reset_url += f'?{parse.urlencode(kwargs)}'

        return password_reset_url

    def get_magic_link(self, next_url='/', one_off=True, **kwargs):
        magic_link_url = build_public_url('magic_link', kwargs={
            'token': f'{int_to_base36(self.id)}-{user_token_generator.make_token(self, one_off=one_off)}'
        })
        if next_url:
            kwargs['next'] = next_url

        return magic_link_url + f'?{parse.urlencode(kwargs)}'


class Group(DjangoGroup):
    class Meta:
        proxy = True
