import pytest
from django.urls import reverse
from rest_framework import status

from ui_preferences.factories import FilterDefinitionFactory

pytestmark = pytest.mark.django_db

FILTER_DEFINITIONS_URL = reverse("ui_preferences:filter-definitions-list")


def test_filter_definitions_GET_missing_table_id_param(user_drf_client):
    response = user_drf_client.get(FILTER_DEFINITIONS_URL)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_filter_definitions_GET(user_drf_client):
    FilterDefinitionFactory.create_batch(3, table_id="users")
    response = user_drf_client.get(f"{FILTER_DEFINITIONS_URL}?table_id=users")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 3
    assert set(response.data[0].keys()) == {
        "id",
        "name",
        "label",
        "query_parameter",
        "required",
        "is_visible",
    }
