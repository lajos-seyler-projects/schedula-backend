import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from users.factories import UserFactory

User = get_user_model()

REGISTER_URL = reverse("users:register")


@pytest.mark.django_db
def test_user_activate_view(drf_client):
    user_data = UserFactory.build()

    data = {
        "username": user_data.username,
        "email": user_data.email,
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "password": user_data.password,
    }

    response = drf_client.post(REGISTER_URL, data, format="json")
    registered_user = User.objects.get(email=response.json()["email"])

    assert registered_user.is_active is False

    activate_url = reverse(
        "users:activate", kwargs={"uuid": registered_user.uuid, "token": registered_user.get_activation_token()}
    )
    response = drf_client.get(activate_url, follow=True)
    registered_user.refresh_from_db()

    assert response.status_code == 200
    assert response.data["message"] == "User activated successfully."
    assert registered_user.is_active is True


@pytest.mark.django_db
def test_user_activate_view_invalid_token(drf_client):
    user_data = UserFactory.build()

    data = {
        "username": user_data.username,
        "email": user_data.email,
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "password": user_data.password,
    }

    response = drf_client.post(REGISTER_URL, data, format="json")
    registered_user = User.objects.get(email=response.json()["email"])

    assert registered_user.is_active is False

    activate_url = reverse("users:activate", kwargs={"uuid": registered_user.uuid, "token": "invalid_token"})
    response = drf_client.get(activate_url, follow=True)
    registered_user.refresh_from_db()

    assert response.status_code == 400
    assert response.data["message"] == "Invalid or expired activation token."
    assert registered_user.is_active is False
