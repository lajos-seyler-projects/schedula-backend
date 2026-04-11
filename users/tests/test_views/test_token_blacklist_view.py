import pytest
from django.urls import reverse

from users.factories import UserFactory

TOKEN_URL = reverse("users:token_obtain_pair")
REFRESH_URL = reverse("users:token_refresh")
BLACKLIST_URL = reverse("users:token_blacklist")


@pytest.mark.django_db
def test_token_blacklist_view(drf_client, user):
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

    response = drf_client.post(BLACKLIST_URL, format="json")
    assert response.status_code == 200

    # Check if cookie is deleted in response
    response = drf_client.post(REFRESH_URL)
    assert response.status_code == 400
    assert response.data["refresh"][0] == "This field may not be blank."

    # Check if re-using the same refresh token is not possible
    drf_client.cookies["refresh"] = refresh_token
    response = drf_client.post(REFRESH_URL)
    assert response.status_code == 401
    assert response.data["detail"] == "Token is blacklisted"


@pytest.mark.django_db
def test_token_blacklist_view_with_invalid_token(drf_client):
    drf_client.cookies["refresh"] = "invalid_token"

    response = drf_client.post(BLACKLIST_URL, format="json")
    assert response.status_code == 401
    assert response.data["detail"] == "Token is invalid"
