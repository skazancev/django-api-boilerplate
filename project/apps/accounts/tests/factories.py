from django.contrib.auth import get_user_model
import factory


class UserFactory(factory.django.DjangoModelFactory):
    email = factory.Faker('email')

    class Meta:
        model = get_user_model()
        django_get_or_create = ['email']
