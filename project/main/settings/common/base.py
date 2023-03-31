"""
Django settings for project.

Generated by 'django-admin startproject' using Django 3.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

from main.settings.common.env import env

from utils.i18n import builtins_install

builtins_install()

COMPANY_NAME = env('COMPANY_NAME', default='Your company')

DOMAIN_NAMES = env.list('DOMAIN_NAMES', default=['example.org'])

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', default='secret_key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG')
BASE_URL_SCHEMA = env('BASE_URL_SCHEMA', default='http')
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['*'])
ADMINS = [('Stanislav', 'stas.kazancev54@gmail.com'), ]
SITE_ID = 1

ROOT_URLCONF = 'main.urls'


WSGI_APPLICATION = 'main.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

DYNAMIC_CHOICE_FIELD_OPTIONS_CACHE = env.int('DYNAMIC_CHOICE_FIELD_OPTIONS_CACHE', default=300)

AUTH_USER_MODEL = 'accounts.User'

X_FRAME_OPTIONS = 'SAMEORIGIN'

# CACHES
CACHES = {
    'default': env.cache()
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
