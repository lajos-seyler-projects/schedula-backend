import pytest
from django.urls import reverse

from users.constants import EMAIL_ERRORS, PASSWORD_ERRORS
from users.factories import UserFactory

pytestmark = pytest.mark.django_db

TOKEN_URL = reverse("users:token_obtain_pair")


def test_token_obtain_pair_view(drf_client, user):
    new_user = UserFactory.create()
    new_user.set_password(user.password)
    new_user.is_active = True
    new_user.save()

    data = {
        "email": new_user.email,
        "password": user.password,
    }

    response = drf_client.post(TOKEN_URL, data, format="json")

    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" not in response.data
    assert "refresh" in response.cookies


def test_token_obtain_pair_view_invalid_credentials(drf_client):
    data = {
        "email": "email@example.com",
        "password": "password123",
    }

    response = drf_client.post(TOKEN_URL, data, format="json")

    assert response.status_code == 401
    assert "access" not in response.data
    assert (
        response.data["detail"] == "No active account found with the given credentials"
    )


def test_token_obtain_pair_view_required_error_messages(drf_client):
    response = drf_client.post(TOKEN_URL)

    assert response.status_code == 400
    assert response.data["email"][0] == EMAIL_ERRORS["required"]
    assert response.data["password"][0] == PASSWORD_ERRORS["required"]


def test_token_obtain_pair_view_blank_error_messages(drf_client):
    data = {
        "email": "",
        "password": "",
    }

    response = drf_client.post(TOKEN_URL, data, format="json")

    assert response.status_code == 400
    assert response.data["email"][0] == EMAIL_ERRORS["blank"]
    assert response.data["password"][0] == PASSWORD_ERRORS["blank"]
