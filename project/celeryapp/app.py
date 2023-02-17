import json
import os

from celery import Celery
from kombu.serialization import register

from utils.json import JSONEncoder

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

app = Celery('project')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


def json_dumps(obj):
    try:
        return json.dumps(obj, cls=JSONEncoder)
    except Exception as e:
        raise e


register(
    'customjson',
    json_dumps,
    json.loads,
    content_type='application/x-customjson',
    content_encoding='utf-8',
)
