import pytest
from django.urls import reverse
from rest_framework import status

from ui_preferences.factories import FilterDefinitionFactory
from ui_preferences.models import UserFilterPreference

pytestmark = pytest.mark.django_db

USER_FILTER_PREFERENCES_URL = reverse("ui_preferences:update-user-filter-preferences")


def test_user_filter_preferences_only_allows_PUT(user_drf_client):
    response = user_drf_client.get(USER_FILTER_PREFERENCES_URL)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    response = user_drf_client.post(USER_FILTER_PREFERENCES_URL)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    response = user_drf_client.patch(USER_FILTER_PREFERENCES_URL)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    response = user_drf_client.delete(USER_FILTER_PREFERENCES_URL)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_user_filter_preferences_PUT_missing_data(user_drf_client):
    response = user_drf_client.put(USER_FILTER_PREFERENCES_URL)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert set(response.data.keys()) == {"table_id", "filter_preferences"}
    assert response.data["table_id"] == ["This field is required."]
    assert response.data["filter_preferences"] == ["This field is required."]


def test_user_filter_preferences_PUT_missing_filters(user_drf_client):
    request_data = {
        "table_id": "users",
        "filter_preferences": [{"name": "invalid1", "is_visible": False}, {"name": "invalid2", "is_visible": True}],
    }
    response = user_drf_client.put(USER_FILTER_PREFERENCES_URL, data=request_data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "detail" in response.data
    assert response.data["detail"] == "Missing filter definitions: users:invalid1, users:invalid2"


def test_user_filter_preferences_PUT(auth_drf_client):
    FilterDefinitionFactory(table_id="users", name="username")
    FilterDefinitionFactory(table_id="users", name="is_superuser")
    client, user = auth_drf_client()
    request_data = {
        "table_id": "users",
        "filter_preferences": [{"name": "username", "is_visible": True}, {"name": "is_superuser", "is_visible": False}],
    }
    response = client.put(USER_FILTER_PREFERENCES_URL, data=request_data, format="json")
    assert response.status_code == status.HTTP_200_OK
    created_user_filter_preferences = UserFilterPreference.objects.filter(user=user)
    assert created_user_filter_preferences.count() == 2
    assert created_user_filter_preferences.get(filter_definition__name="username").is_visible is True
    assert created_user_filter_preferences.get(filter_definition__name="is_superuser").is_visible is False
