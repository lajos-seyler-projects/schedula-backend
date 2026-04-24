import factory
from factory.django import DjangoModelFactory

from users.factories import UserFactory

from . import models


class UserColumnPreferenceFactory(DjangoModelFactory):
    class Meta:
        model = models.UserColumnPreference

    user = factory.SubFactory(UserFactory)
    table_id = "users"
    key = factory.Sequence(lambda n: f"column_{n}")
    expression = factory.LazyAttribute(lambda obj: {"type": "field", "path": obj.key})
    label = factory.LazyAttribute(lambda obj: obj.key.replace("_", " ").title())
    is_visible = True
    order = factory.Sequence(lambda n: n)


class FilterDefinitionFactory(DjangoModelFactory):
    class Meta:
        model = models.FilterDefinition

    table_id = "users"
    name = factory.Sequence(lambda n: f"filter_{n}")
    label = factory.LazyAttribute(lambda obj: obj.name.replace("_", " ").title())
    query_parameter = factory.LazyAttribute(lambda obj: obj.name)
    required = False
    is_visible_by_default = True


class UserFilterPreferenceFactory(DjangoModelFactory):
    class Meta:
        model = models.UserFilterPreference

    user = factory.SubFactory(UserFactory)
    filter_definition = factory.SubFactory(FilterDefinitionFactory)
    is_visible = True


class FilterVariantFactory(DjangoModelFactory):
    class Meta:
        model = models.FilterVariant

    table_id = "users"
    name = factory.Sequence(lambda n: f"variant_{n}")
    filters = factory.Dict({})
    exclude_filters = factory.Dict({})
    is_public = False
    execute_on_selection = False
    created_by = factory.SubFactory(UserFactory)
