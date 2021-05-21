from django.db import models

from apps.bases.models import BaseModel


class FlowEvent(BaseModel):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title
