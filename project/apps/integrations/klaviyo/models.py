from django.contrib.postgres.fields import CICharField

from apps.bases.models import BaseModel


class KlaviyoEvent(BaseModel):
    name = CICharField(max_length=100, unique=True)

    def str(self):
        return self.name
