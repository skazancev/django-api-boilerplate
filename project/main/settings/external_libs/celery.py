from kombu.utils.url import safequote

from main.settings.common.env import env
from main.settings.common.base import TIME_ZONE
from main.settings.external_libs.aws import AWS_IAM_SECRET_KEY, AWS_IAM_ACCESS_KEY


CELERY_USE_SQS = env.bool('CELERY_USE_SQS', default=False)

if CELERY_USE_SQS:
    CELERY_BROKER_URL = f'sqs://{safequote(AWS_IAM_ACCESS_KEY)}:{safequote(AWS_IAM_SECRET_KEY)}@'
else:
    CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='amqp://guest@rabbit:5672/')

CELERY_BROKER_TRANSPORT_OPTIONS = env.dict('BROKER_TRANSPORT_OPTIONS', default={})
CELERY_TASK_ALWAYS_EAGER = env.bool('CELERY_TASK_ALWAYS_EAGER', default=False)
CELERY_TASK_EAGER_PROPAGATES = env.bool('CELERY_TASK_EAGER_PROPAGATES', default=True)
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['customjson']
CELERY_TASK_SERIALIZER = 'customjson'
CELERY_RESULT_SERIALIZER = 'customjson'
