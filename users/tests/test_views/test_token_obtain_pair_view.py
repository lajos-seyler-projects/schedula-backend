import pytest
from django.urls import reverse

from users.factories import UserFactory

TOKEN_URL = reverse("users:token_obtain_pair")


@pytest.mark.django_db
def test_token_obtain_pair_view(drf_client, user):
    new_user = UserFactory.create()
    new_user.set_password(user.password)
    new_user.is_active = True
    new_user.save()

    data = {"email": new_user.email, "password": user.password}

    response = drf_client.post(TOKEN_URL, data, format="json")

    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" not in response.data
    assert "refresh" in response.cookies


@pytest.mark.django_db
def test_token_obtain_pair_view_invalid_credentials(drf_client):
    data = {"email": "email", "password": "password123"}

    response = drf_client.post(TOKEN_URL, data, format="json")

    assert response.status_code == 401
    assert "access" not in response.data
    assert response.data["detail"] == "No active account found with the given credentials"
