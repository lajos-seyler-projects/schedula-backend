import factory
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from factory import fuzzy

from users.models import User, UserPreferences


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


class SuperUserFactory(UserFactory):
    is_staff = True
    is_superuser = True


class UserPreferencesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserPreferences

    date_format = fuzzy.FuzzyChoice(UserPreferences.DateFormatChoices)
    decimal_format = fuzzy.FuzzyChoice(UserPreferences.DecimalFormatChoices)
    time_format = fuzzy.FuzzyChoice(UserPreferences.TimeFormatChoices)
    fiori_theme = fuzzy.FuzzyChoice(UserPreferences.FioriThemeChoices)


class GroupFactory(factory.django.DjangoModelFactory):
    name = fuzzy.FuzzyText()

    class Meta:
        model = Group
