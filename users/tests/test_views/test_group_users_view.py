from django.urls import reverse
from rest_framework import status

from ...factories import GroupFactory, UserFactory


def get_group_users(name):
    return reverse("users:group_users-list", kwargs={"name": name})


def test_group_users_list_GET(user, auth_drf_client):
    group = GroupFactory()
    users = UserFactory.create_batch(3)
    group.user_set.add(*users)
    client, _ = auth_drf_client(user=user)
    response = client.get(get_group_users(group.name))
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 3
    assert set(results[0].keys()) == {
        "uuid",
        "username",
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_superuser",
    }


def test_group_users_POST_and_DELETE_requires_permission(user, user_drf_client):
    group = GroupFactory()
    target = UserFactory()
    response = user_drf_client.post(get_group_users(group.name), data={"users": [target.uuid]}, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = user_drf_client.delete(get_group_users(group.name), data={"users": [target.uuid]}, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_group_users_list_POST(user, auth_drf_client):
    group = GroupFactory()
    target = UserFactory()
    client, _ = auth_drf_client("users.manage_user_groups", user=user)
    response = client.post(get_group_users(group.name), data={"users": [target.uuid]}, format="json")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert group.user_set.count() == 1
    assert group.user_set.filter(id=target.id).exists()


def test_group_users_list_DELETE(user, auth_drf_client):
    group = GroupFactory()
    target = UserFactory(username="target")
    other_user = UserFactory(username="other")
    group.user_set.add(target, other_user)
    assert group.user_set.count() == 2
    client, _ = auth_drf_client("users.manage_user_groups", user=user)
    response = client.delete(get_group_users(group.name), data={"users": [target.uuid]}, format="json")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert group.user_set.count() == 1
    assert group.user_set.filter(id=target.id).exists() is False
    assert group.user_set.filter(id=other_user.id).exists()
