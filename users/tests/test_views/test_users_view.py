import uuid

import pytest
from django.urls import reverse
from rest_framework import status

from users.factories import UserFactory
from users.models import User

USERS_URL = reverse("users:users-list")

pytestmark = pytest.mark.django_db


def get_user_detail_url(uuid):
    return reverse("users:users-detail", kwargs={"uuid": uuid})


@pytest.mark.django_db
class TestUnauthenticatedAccess:
    def test_users_list_requires_authentication(self, drf_client):
        assert drf_client.get(USERS_URL).status_code == status.HTTP_401_UNAUTHORIZED

    def test_users_retrieve_requires_authentication(self, user, drf_client):
        detail_url = get_user_detail_url(user.uuid)
        assert drf_client.get(detail_url).status_code == status.HTTP_401_UNAUTHORIZED

    def test_users_create_requires_authentication(self, drf_client):
        assert (
            drf_client.post(USERS_URL, {"username": "new"}).status_code
            == status.HTTP_401_UNAUTHORIZED
        )

    def test_users_update_requires_authentication(self, user, drf_client):
        detail_url = get_user_detail_url(user.uuid)
        assert (
            drf_client.put(detail_url, {"username": "changed"}).status_code
            == status.HTTP_401_UNAUTHORIZED
        )

    def test_users_partial_update_requires_authentication(self, user, drf_client):
        detail_url = get_user_detail_url(user.uuid)
        assert (
            drf_client.patch(detail_url, {"first_name": "X"}).status_code
            == status.HTTP_401_UNAUTHORIZED
        )

    def test_users_destroy_requires_authentication(self, user, drf_client):
        detail_url = get_user_detail_url(user.uuid)
        assert drf_client.delete(detail_url).status_code == status.HTTP_401_UNAUTHORIZED


class TestPermissionEnforcement:
    def test_users_list_allowed_without_view_permission(self, user_drf_client):
        assert user_drf_client.get(USERS_URL).status_code == status.HTTP_200_OK

    def test_users_retrieve_allowed_without_view_permission(
        self, user, user_drf_client
    ):
        detail_url = get_user_detail_url(user.uuid)
        assert user_drf_client.get(detail_url).status_code == status.HTTP_200_OK

    def test_users_create_forbidden_without_add_permission(self, user_drf_client):
        response = user_drf_client.post(USERS_URL, {"username": "shouldfail"})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_users_update_forbidden_without_change_permission(
        self, user, user_drf_client
    ):
        detail_url = get_user_detail_url(user.uuid)
        response = user_drf_client.patch(detail_url, {"first_name": "Test"})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_users_destroy_forbidden_without_delete_permission(
        self, user, user_drf_client
    ):
        detail_url = get_user_detail_url(user.uuid)
        response = user_drf_client.delete(detail_url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestListEndpoint:
    def test_users_uses_slim_serializer_fields(self, user_drf_client):
        response = user_drf_client.get(USERS_URL)
        assert set(response.data["results"][0].keys()) == {
            "uuid",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_superuser",
        }

    def test_users_includes_all_users(self, user, user_drf_client):
        extra1 = UserFactory()
        extra2 = UserFactory()
        response = user_drf_client.get(USERS_URL)
        usernames = {u["username"] for u in response.data["results"]}
        assert user.username in usernames
        assert extra1.username in usernames
        assert extra2.username in usernames


class TestRetrieveEndpoint:
    def test_users_details_serializer_fields(self, user, user_drf_client):
        url = get_user_detail_url(user.uuid)
        response = user_drf_client.get(url)
        expected_fields = {
            "uuid",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_superuser",
            "date_joined",
            "last_login",
        }
        assert set(response.data.keys()) == expected_fields

    def test_users_details_returns_correct_user(self, user, user_drf_client):
        extra = UserFactory()
        url = get_user_detail_url(uuid=extra.uuid)
        response = user_drf_client.get(url)
        assert response.data["username"] == extra.username
        assert response.data["email"] == extra.email

    def test_users_details_returns_404_for_nonexistent_uuid(self, user_drf_client):
        url = get_user_detail_url(uuid=uuid.uuid4())
        assert user_drf_client.get(url).status_code == status.HTTP_404_NOT_FOUND


class TestCreateEndpoint:
    def test_users_create_new_user(self, auth_drf_client):
        client, _ = auth_drf_client("users.add_user")
        response = client.post(
            USERS_URL,
            {
                "username": "newUser",
                "email": "newUser@example.com",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(username="newUser").exists()
        assert set(response.data.keys()) == {
            "uuid",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_superuser",
        }

    def test_users_create_returns_400_on_duplicate_username(self, auth_drf_client):
        client, _ = auth_drf_client("users.add_user")
        existing = UserFactory()
        response = client.post(
            USERS_URL, {"username": existing.username, "email": "newUser@example.com"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_users_create_returns_400_on_duplicate_email(self, auth_drf_client):
        client, _ = auth_drf_client("users.add_user")
        existing = UserFactory()
        response = client.post(
            USERS_URL, {"username": "newUser", "email": existing.email}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_users_create_returns_400_on_missing_username(self, auth_drf_client):
        client, _ = auth_drf_client("users.add_user")
        response = client.post(USERS_URL, {"email": "newUser@example.com"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_users_create_returns_400_on_missing_email(self, auth_drf_client):
        client, _ = auth_drf_client("users.add_user")
        response = client.post(USERS_URL, {"username": "newuser"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestUpdateEndpoint:
    def test_users_partial_update(self, auth_drf_client):
        client, _ = auth_drf_client("users.change_user")
        target_user = UserFactory()
        url = get_user_detail_url(target_user.uuid)
        response = client.patch(url, {"first_name": "Updated"})
        assert response.status_code == status.HTTP_200_OK
        assert set(response.data.keys()) == {
            "uuid",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_superuser",
        }
        target_user.refresh_from_db()
        assert target_user.first_name == "Updated"

    def test_users_full_update(self, auth_drf_client):
        client, _ = auth_drf_client("users.change_user")
        target_user = UserFactory()
        url = get_user_detail_url(target_user.uuid)
        response = client.patch(
            url,
            {
                "username": "Updated",
                "email": "updated@example.com",
                "first_name": "Updated",
                "last_name": "Name",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        assert set(response.data.keys()) == {
            "uuid",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_superuser",
        }
        assert response.data["username"] == "Updated"
        assert response.data["email"] == "updated@example.com"
        assert response.data["first_name"] == "Updated"
        assert response.data["last_name"] == "Name"

    def test_users_update_returns_404_for_nonexistent_uuid(self, auth_drf_client):
        client, _ = auth_drf_client("users.change_user")
        url = get_user_detail_url(uuid=uuid.uuid4())
        assert (
            client.patch(url, {"first_name": "Updated"}).status_code
            == status.HTTP_404_NOT_FOUND
        )


class TestDeleteEndpoint:
    def test_users_delete(self, auth_drf_client):
        client, _ = auth_drf_client("users.delete_user")
        deletable = UserFactory()
        uid = deletable.uuid
        url = get_user_detail_url(uuid=deletable.uuid)
        assert client.delete(url).status_code == status.HTTP_204_NO_CONTENT
        assert not User.objects.filter(uuid=uid).exists()

    def test_users_delete_returns_404_for_nonexistent_uuid(self, auth_drf_client):
        client, _ = auth_drf_client("users.delete_user")
        url = get_user_detail_url(uuid=uuid.uuid4())
        assert client.delete(url).status_code == status.HTTP_404_NOT_FOUND
