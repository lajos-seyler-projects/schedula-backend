import pytest
from django.urls import reverse
from rest_framework import status

from users.factories import UserFactory, UserPreferencesFactory

pytestmark = pytest.mark.django_db

PREFERENCES_URL = reverse("users:me-preferences")


def test_preferences_only_allow_GET_and_PATCH(user_drf_client):
    response = user_drf_client.get(PREFERENCES_URL)
    assert response.status_code == status.HTTP_200_OK

    response = user_drf_client.patch(PREFERENCES_URL, {"time_format": "12"}, format="json")
    assert response.status_code == status.HTTP_200_OK

    response = user_drf_client.delete(PREFERENCES_URL)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_preferences_returns_request_users_data(auth_drf_client):
    user1 = UserFactory(is_active=True)
    user2 = UserFactory(is_active=True)
    user3 = UserFactory(is_active=True)

    UserPreferencesFactory(user=user1, time_format="12")
    UserPreferencesFactory(user=user2, time_format="24")
    UserPreferencesFactory(user=user3, time_format="12")

    client, user = auth_drf_client(user=user2)

    response = client.get(PREFERENCES_URL)

    assert response.status_code == 200
    assert isinstance(response.data, dict)
    assert response.data["time_format"] == "24"


def test_preferences_response(user, auth_drf_client):
    UserPreferencesFactory(
        user=user, date_format="ed", decimal_format="eu", time_format="12", fiori_theme="sap_fiori_3_dark"
    )

    client, _ = auth_drf_client(user=user)

    response = client.get(PREFERENCES_URL)

    assert response.status_code == 200
    assert isinstance(response.data, dict)
    assert response.data["date_format"] == "ed"
    assert response.data["date_format_display"] == "DD.MM.YYYY"
    assert response.data["decimal_format"] == "eu"
    assert response.data["decimal_format_display"] == "1 234 567,8"
    assert response.data["time_format"] == "12"
    assert response.data["time_format_display"] == "12-hour"
    assert response.data["fiori_theme"] == "sap_fiori_3_dark"
    assert response.data["fiori_theme_display"] == "Quartz Dark"


def test_preferences_PATCH(user, auth_drf_client):
    preferences = UserPreferencesFactory(user=user, date_format="ed", fiori_theme="sap_horizon")
    client, user = auth_drf_client(user=user)
    response = client.patch(PREFERENCES_URL, {"date_format": "es", "fiori_theme": "sap_horizon_dark"}, format="json")
    assert response.status_code == 200
    preferences.refresh_from_db()
    assert preferences.date_format == "es"
    assert preferences.fiori_theme == "sap_horizon_dark"


def test_preferences_PATCH_modifying_user_field_is_not_possible(user, auth_drf_client):
    preferences = UserPreferencesFactory(user=user, date_format="ed", fiori_theme="sap_horizon")
    client, user = auth_drf_client(user=user)
    other_user = UserFactory()
    response = client.patch(PREFERENCES_URL, {"user": other_user.id}, format="json")
    assert response.status_code == 200
    preferences.refresh_from_db()
    assert preferences.user == user
