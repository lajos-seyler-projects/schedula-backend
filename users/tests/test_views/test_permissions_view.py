from django.conf import settings
from django.urls import reverse
from rest_framework import status

from users.utils import get_filtered_permissions_by_exclusions

PERMISSIONS_URL = reverse("users:permissions-list")

permissions_excluding_content_types = get_filtered_permissions_by_exclusions()


def get_permission_details_url(id):
    return reverse("users:permissions-detail", kwargs={"pk": id})


def test_permissions_url_only_allows_GET(auth_drf_client):
    client, _ = auth_drf_client(
        "auth.add_permission", "auth.view_permission", "auth.change_permission", "auth.delete_permission"
    )

    assert client.get(PERMISSIONS_URL).status_code == status.HTTP_200_OK
    assert client.post(PERMISSIONS_URL).status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert client.put(PERMISSIONS_URL).status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert client.patch(PERMISSIONS_URL).status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert client.delete(PERMISSIONS_URL).status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_permissions_url_GET(auth_drf_client):
    client, _ = auth_drf_client("auth.view_permission")
    response = client.get(PERMISSIONS_URL)
    assert response.status_code == status.HTTP_200_OK
    permission_count = permissions_excluding_content_types.count()
    results = response.json()["results"]
    assert len(results) == min(permission_count, settings.REST_FRAMEWORK["PAGE_SIZE"])
    assert "user_count" in results[0]


def test_permissions_GET_with_name_filter(auth_drf_client):
    client, _ = auth_drf_client("auth.view_permission")
    response = client.get(f"{PERMISSIONS_URL}?name__icontains=add")
    assert response.status_code == status.HTTP_200_OK
    permissions_with_add_in_name = permissions_excluding_content_types.filter(name__icontains="add")
    assert response.json()["count"] == permissions_with_add_in_name.count()


def test_permissions_detail_url_only_allows_GET(auth_drf_client):
    client, _ = auth_drf_client(
        "auth.add_permission", "auth.view_permission", "auth.change_permission", "auth.delete_permission"
    )
    permission = permissions_excluding_content_types.first()
    permission_detail_url = get_permission_details_url(permission.id)
    assert client.get(permission_detail_url).status_code == status.HTTP_200_OK
    assert client.post(permission_detail_url).status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert client.put(permission_detail_url).status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert client.patch(permission_detail_url).status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert client.delete(permission_detail_url).status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_permissions_detail_url_GET(auth_drf_client):
    client, _ = auth_drf_client("auth.view_permission")
    permission = permissions_excluding_content_types.first()
    permission_detail_url = get_permission_details_url(permission.id)
    response = client.get(permission_detail_url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == permission.name
    assert "user_count" in response.data
