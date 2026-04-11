import pytest
from django.urls import reverse

from users.factories import UserFactory

TOKEN_URL = reverse("users:token_obtain_pair")
REFRESH_URL = reverse("users:token_refresh")


@pytest.mark.django_db
def test_token_refresh_view(drf_client, user):
    new_user = UserFactory.create(password=user.password)
    new_user.is_active = True
    new_user.save()

    data = {
        "email": new_user.email,
        "password": user.password,
    }

    response = drf_client.post(TOKEN_URL, data, format="json")
    assert response.status_code == 200

    refresh_token = response.cookies.get("refresh")
    assert refresh_token is not None

    drf_client.cookies["refresh"] = refresh_token

    response = drf_client.post(REFRESH_URL)

    assert response.status_code == 200
    assert "access" in response.data


@pytest.mark.django_db
def test_token_refresh_view_no_token(drf_client, user):
    response = drf_client.post(REFRESH_URL)

    assert response.status_code == 400
    assert response.data["refresh"][0] == "This field may not be null."
    assert "access" not in response.data


@pytest.mark.django_db
def test_token_refresh_view_with_invalid_token(drf_client):
    drf_client.cookies["refresh"] = "invalid_token"
    response = drf_client.post(REFRESH_URL)

    assert response.status_code == 401
    assert response.data["detail"] == "Token is invalid"
    assert "access" not in response.data
