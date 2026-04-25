import pytest
from django.urls import reverse
from rest_framework import status

from ui_preferences.factories import UserColumnPreferenceFactory
from ui_preferences.models import UserColumnPreference
from users.factories import UserFactory

pytestmark = pytest.mark.django_db

USER_COLUMN_PREFERENCES_URL = reverse("ui_preferences:user-column-preferences-list")


def test_user_column_preferences_GET_missing_table_id_param(user_drf_client):
    response = user_drf_client.get(USER_COLUMN_PREFERENCES_URL)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_user_column_preferences_GET(auth_drf_client):
    client, user = auth_drf_client()
    preferences = UserColumnPreferenceFactory.create_batch(3, user=user)
    other_user = UserFactory()
    UserColumnPreferenceFactory.create_batch(2, user=other_user)

    response = client.get(f"{USER_COLUMN_PREFERENCES_URL}?table_id=users")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 3
    assert set(i["key"] for i in response.data) == set(preference.key for preference in preferences)


def test_user_column_preferences_POST_missing_data(user_drf_client):
    response = user_drf_client.post(USER_COLUMN_PREFERENCES_URL)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert set(response.data.keys()) == {"table_id", "column_preferences"}
    assert response.data["table_id"] == ["This field is required."]
    assert response.data["column_preferences"] == ["This field is required."]


def test_user_column_preferences_POST_invalid_columns(user_drf_client):
    request_data = {
        "table_id": "users",
        "column_preferences": [{"key": "invalid1", "label": "Invalid1"}, {"key": "invalid2", "label": "Invalid2"}],
    }
    response = user_drf_client.post(USER_COLUMN_PREFERENCES_URL, data=request_data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "detail" in response.data
    assert response.data["detail"] == "Invalid column preferences: invalid1, invalid2"


def test_user_column_preferences_POST(auth_drf_client):
    client, user = auth_drf_client()
    request_data = {
        "table_id": "users",
        "column_preferences": [
            {"key": "username", "label": "Username", "is_visible": False},
            {"key": "first_name", "label": "First Name", "is_visible": True},
            {"key": "last_name", "label": "Last Name", "is_visible": True},
        ],
    }
    response = client.post(USER_COLUMN_PREFERENCES_URL, data=request_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    created_preferences = UserColumnPreference.objects.filter(user=user)
    assert created_preferences.count() == 3
    assert set(created_preferences.values_list("key", flat=True)) == {"username", "first_name", "last_name"}
    assert UserColumnPreference.objects.get(key="username").is_visible is False
    assert UserColumnPreference.objects.get(key="first_name").is_visible is True
