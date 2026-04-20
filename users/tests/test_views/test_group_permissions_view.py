from django.urls import reverse
from rest_framework import status

from ...factories import GroupFactory, PermissionFactory


def get_group_permissions(name):
    return reverse("users:group_permissions-list", kwargs={"name": name})


def test_group_permissions_list_GET(user, auth_drf_client):
    group = GroupFactory()
    permissions = PermissionFactory.create_batch(3)
    group.permissions.add(*permissions)
    client, _ = auth_drf_client(user=user)
    response = client.get(get_group_permissions(group.name))
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 3
    assert set(results[0].keys()) == {
        "id",
        "name",
        "codename",
        "content_type",
        "user_count",
    }


def test_group_permissions_POST_and_DELETE_requires_permission(user, user_drf_client):
    group = GroupFactory()
    target = PermissionFactory()
    response = user_drf_client.post(
        get_group_permissions(group.name),
        data={"permissions": [target.id]},
        format="json",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = user_drf_client.delete(
        get_group_permissions(group.name),
        data={"permissions": [target.id]},
        format="json",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_group_permissions_list_POST(user, auth_drf_client):
    group = GroupFactory()
    target = PermissionFactory()
    client, _ = auth_drf_client("users.manage_group_permissions", user=user)
    response = client.post(
        get_group_permissions(group.name),
        data={"permissions": [target.id]},
        format="json",
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert group.permissions.count() == 1
    assert group.permissions.filter(id=target.id).exists()


def test_group_permissions_list_DELETE(user, auth_drf_client):
    group = GroupFactory()
    target = PermissionFactory(name="target")
    other_permission = PermissionFactory(name="other")
    group.permissions.add(target, other_permission)
    assert group.permissions.count() == 2
    client, _ = auth_drf_client("users.manage_group_permissions", user=user)
    response = client.delete(
        get_group_permissions(group.name),
        data={"permissions": [target.id]},
        format="json",
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert group.permissions.count() == 1
    assert group.permissions.filter(id=target.id).exists() is False
    assert group.permissions.filter(id=other_permission.id).exists()
