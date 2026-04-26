import pytest
from django.urls import reverse

from users.factories import PermissionFactory

pytestmark = pytest.mark.django_db

ME_URL = reverse("users:me")


def test_me_view_requires_authentication(drf_client):
    unauthenticated_response = drf_client.get(ME_URL)
    assert unauthenticated_response.status_code == 401


def test_me_view_GET(auth_drf_client):
    permissions = PermissionFactory.create_batch(3)
    client, user = auth_drf_client()
    user.user_permissions.set(permissions)
    response = client.get(ME_URL)

    assert response.status_code == 200
    assert set(response.data.keys()) == {"username", "email", "first_name", "last_name", "is_superuser", "permissions"}
    assert response.data["username"] == user.username
    assert response.data["email"] == user.email
    assert response.data["first_name"] == user.first_name
    assert response.data["last_name"] == user.last_name
    assert len(response.data["permissions"]) == 3


@pytest.mark.parametrize(
    "updated_field, updated_value",
    [
        ("username", "updated_username"),
        ("email", "updated_email@example.com"),
        ("first_name", "updated_first_name"),
        ("last_name", "updated_last_name"),
        ("password", "updated_password"),
    ],
)
def test_me_view_PATCH(user_drf_client, user, updated_field, updated_value):
    original_values = {
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
    }

    response = user_drf_client.patch(ME_URL, {updated_field: updated_value}, format="json")
    assert response.status_code == 200

    user.refresh_from_db()

    for field, original in original_values.items():
        if field == updated_field:
            assert getattr(user, field) == updated_value
        else:
            assert getattr(user, field) == original

    if updated_field == "password":
        assert user.check_password(updated_value)
