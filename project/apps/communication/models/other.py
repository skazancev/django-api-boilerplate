from ckeditor.fields import RichTextField
from django.db import models
from simple_history.models import HistoricalRecords

from apps.bases.models import BaseModel
from utils.fields import ActiveField, SlugField, OrderField


class FAQ(BaseModel):
    is_active = ActiveField()
    question = models.TextField()
    teaser = models.TextField()
    answer = RichTextField()
    slug = SlugField(target='question')
    on_general = models.BooleanField(default=False)
    order = OrderField()

    history = HistoricalRecords()

    def str(self):
        return self.question
