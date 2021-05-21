from django.db import connection
from django.db.models.signals import pre_migrate
from django.dispatch import receiver


@receiver(pre_migrate)
def app_pre_migration(sender, app_config, **kwargs):
    cur = connection.cursor()
    cur.execute('CREATE EXTENSION IF NOT EXISTS citext;')
