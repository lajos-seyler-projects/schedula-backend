import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db

DEFAULT_COLUMN_PREFERENCES_URL = reverse("ui_preferences:default-column-preferences")


def test_default_column_preferences_GET_missing_table_id(user_drf_client):
    response = user_drf_client.get(DEFAULT_COLUMN_PREFERENCES_URL)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_default_column_preferences_GET_invalid_table_id(user_drf_client):
    response = user_drf_client.get(
        f"{DEFAULT_COLUMN_PREFERENCES_URL}?table_id=invalidtableid"
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_default_column_preferences_GET(user_drf_client):
    response = user_drf_client.get(f"{DEFAULT_COLUMN_PREFERENCES_URL}?table_id=users")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, list)
    assert set(response.data[0].keys()) == {
        "table_id",
        "key",
        "expression",
        "label",
        "is_visible",
    }
