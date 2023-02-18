# Application definition
INSTALLED_APPS = [
    'apps.AdminConfig',  # replaces 'django.contrib.admin'
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'django_json_widget',
    'rest_framework',
    'drf_yasg',
    'adminsortable',
    'django_celery_beat',
    'django_celery_results',
    'ckeditor',
    'ckeditor_uploader',
    'django_better_admin_arrayfield',
    'simple_history',
    'phonenumber_field',

    'api',
    'apps.core.apps.CoreConfig',
    'apps.webhooks.apps.WebhooksConfig',
    'apps.accounts.apps.AccountsConfig',
    'apps.communication.apps.CommunicationConfig',
    'apps.integrations.klaviyo.apps.KlaviyoConfig',
    'apps.integrations.whatsapp.apps.WhatsAppConfig',
]
