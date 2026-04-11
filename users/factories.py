import factory
from django.contrib.auth.hashers import make_password

from users.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    password = factory.LazyFunction(lambda: make_password("defaultpassword"))
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.get("password", None)
        user = super()._create(model_class, *args, **kwargs)

        if password:
            user.set_password(password)
            user.save()

        return user
