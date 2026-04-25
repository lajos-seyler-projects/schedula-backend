import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse

from users.factories import UserFactory

pytestmark = pytest.mark.django_db

User = get_user_model()

REGISTER_URL = reverse("users:register")


def test_user_registration_view_method_not_allowed(drf_client):
    response = drf_client.get(REGISTER_URL)

    assert response.status_code == 405
    assert response.data == {"detail": 'Method "GET" not allowed.'}
    assert response["Allow"] == "POST, OPTIONS"


def test_user_registration_view(drf_client):
    mail.outbox = []

    user_data = UserFactory.build()

    data = {
        "username": user_data.username,
        "email": user_data.email,
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "password": user_data.password,
    }

    response = drf_client.post(REGISTER_URL, data, format="json")

    assert response.status_code == 201
    assert response.data["username"] == data["username"]
    assert response.data["email"] == data["email"]
    assert response.data["first_name"] == data["first_name"]
    assert response.data["last_name"] == data["last_name"]
    assert "password" not in response.data

    registered_user = User.objects.get(email=response.json()["email"])
    registered_user.refresh_from_db()

    assert registered_user.is_active is False

    email_sent = mail.outbox[0]
    assert "Verify your email" in email_sent.subject
    assert data["email"] in email_sent.to


def test_user_registration_view_invalid_data(drf_client):
    data = {"username": "", "email": "", "first_name": "", "last_name": "", "password": ""}

    response = drf_client.post(REGISTER_URL, data, format="json")

    assert response.status_code == 400
    assert "username" in response.data
    assert "email" in response.data
    assert "password" in response.data
