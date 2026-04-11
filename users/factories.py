import factory
from django.contrib.auth.hashers import make_password

from users.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    password = factory.LazyFunction(lambda: make_password("defaultpassword"))
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
