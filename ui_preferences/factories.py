import factory
from factory.django import DjangoModelFactory

from users.factories import UserFactory

from .models import UserColumnPreference


class UserColumnPreferenceFactory(DjangoModelFactory):
    class Meta:
        model = UserColumnPreference

    user = factory.SubFactory(UserFactory)
    table_id = "users"
    key = factory.Sequence(lambda n: f"column_{n}")
    expression = factory.LazyAttribute(lambda obj: {"type": "field", "path": obj.key})
    label = factory.LazyAttribute(lambda obj: obj.key.replace("_", " ").title())
    is_visible = True
    order = factory.Sequence(lambda n: n)
