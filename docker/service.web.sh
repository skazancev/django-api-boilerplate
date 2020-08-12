#!/bin/bash

cd /code/

python manage.py migrate --no-input
python manage.py collectstatic --no-input

gunicorn main.wsgi:application -b 0.0.0.0:8000 --reload --worker-connections=1000 --workers=5 --threads=3
