import pytest
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status

from ...factories import GroupFactory

GROUPS_URL = reverse("users:groups-list")


def get_group_details_url(name):
    return reverse("users:groups-detail", kwargs={"name": name})


@pytest.mark.django_db
def test_groups_url_GET(auth_drf_client):
    GroupFactory.create_batch(3)
    client, _ = auth_drf_client("auth.view_group")
    response = client.get(GROUPS_URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 3
    assert set(response.data["results"][0].keys()) == {"id", "name", "user_count", "permission_count"}


@pytest.mark.django_db
def test_groups_url_GET_with_name_filter(auth_drf_client):
    GroupFactory.create_batch(3)
    GroupFactory.create(name="target")
    client, _ = auth_drf_client("auth.view_group")
    response = client.get(f"{GROUPS_URL}?name__icontains=target")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1


def test_groups_url_POST(auth_drf_client):
    client, _ = auth_drf_client("auth.add_group")
    response = client.post(GROUPS_URL, data={"name": "new group"}, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert Group.objects.filter(name="new group").exists()


def test_groups_url_POST_invalid_data(auth_drf_client):
    client, _ = auth_drf_client("auth.add_group")
    response = client.post(GROUPS_URL, data={"name": ""}, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_groups_url_POST_duplicate(auth_drf_client):
    GroupFactory(name="existing")
    client, _ = auth_drf_client("auth.add_group")
    response = client.post(GROUPS_URL, data={"name": "existing"}, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_groups_url_PATCH(auth_drf_client):
    target = GroupFactory(name="target")
    client, _ = auth_drf_client("auth.change_group")
    response = client.patch(get_group_details_url(target.name), data={"name": "updated group"}, format="json")
    assert response.status_code == status.HTTP_200_OK
    target.refresh_from_db()
    assert target.name == "updated group"


def test_groups_url_DELETE(auth_drf_client):
    target = GroupFactory(name="target")
    client, _ = auth_drf_client("auth.delete_group")
    response = client.delete(get_group_details_url(name=target.name))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Group.objects.filter(name=target.name).exists() is False
