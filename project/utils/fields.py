from django.db import models


class OrderField(models.PositiveIntegerField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('default', 0)
        kwargs.setdefault('db_index', True)
        kwargs.setdefault('editable', False)
        super().__init__(*args, **kwargs)
