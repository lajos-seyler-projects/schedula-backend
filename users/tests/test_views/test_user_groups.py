from django.urls import reverse
from rest_framework import status

from ...factories import GroupFactory


def get_user_groups_url(uuid):
    return reverse("users:user_groups-list", kwargs={"uuid": uuid})


def test_user_groups_list_GET(user, auth_drf_client):
    groups = GroupFactory.create_batch(3)
    user.groups.add(*groups)
    client, _ = auth_drf_client(user=user)
    response = client.get(get_user_groups_url(user.uuid))
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 3
    assert set(results[0].keys()) == {"id", "name", "user_count", "permission_count"}


def test_user_groups_POST_and_DELETE_requires_permission(user, user_drf_client):
    target = GroupFactory()
    response = user_drf_client.post(
        get_user_groups_url(user.uuid), data={"groups": [target.id]}, format="json"
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = user_drf_client.delete(
        get_user_groups_url(user.uuid), data={"groups": [target.id]}, format="json"
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_user_groups_list_POST(user, auth_drf_client):
    target = GroupFactory()
    client, _ = auth_drf_client("users.manage_user_groups", user=user)
    response = client.post(
        get_user_groups_url(user.uuid), data={"groups": [target.id]}, format="json"
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert user.groups.count() == 1
    assert user.groups.filter(id=target.id).exists()


def test_user_groups_list_DELETE(user, auth_drf_client):
    target = GroupFactory(name="target")
    other_group = GroupFactory(name="other")
    user.groups.add(target, other_group)
    assert user.groups.count() == 2
    client, _ = auth_drf_client("users.manage_user_groups", user=user)
    response = client.delete(
        get_user_groups_url(user.uuid), data={"groups": [target.id]}, format="json"
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert user.groups.count() == 1
    assert user.groups.filter(id=target.id).exists() is False
    assert user.groups.filter(id=other_group.id).exists()
