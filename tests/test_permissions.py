import uuid

from fastapi import status


def create_permission_payload():
    unique = uuid.uuid4().hex[:8]

    return {
        "name": f"permission.{unique}",
        "description": "Test permission",
    }


def test_create_permission(client, admin_headers):
    payload = create_permission_payload()

    response = client.post(
        "/api/v1/permissions/",
        json=payload,
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert data["name"] == payload["name"]
    assert data["description"] == payload["description"]


def test_duplicate_permission(
    client,
    admin_headers,
):
    payload = create_permission_payload()

    first = client.post(
        "/api/v1/permissions/",
        json=payload,
        headers=admin_headers,
    )

    assert first.status_code == status.HTTP_201_CREATED

    second = client.post(
        "/api/v1/permissions/",
        json=payload,
        headers=admin_headers,
    )

    assert second.status_code == status.HTTP_409_CONFLICT

    assert second.json()["detail"] == (
        "Permission already exists"
    )


def test_list_permissions(
    client,
    admin_headers,
):

    response = client.get(
        "/api/v1/permissions/",
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert "permissions" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data


def test_get_permission(
    client,
    admin_headers,
    test_permission,
):

    response = client.get(
        f"/api/v1/permissions/{test_permission.id}",
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["name"] == test_permission.name


def test_get_missing_permission(
    client,
    admin_headers,
):

    response = client.get(
        f"/api/v1/permissions/{uuid.uuid4()}",
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert response.json()["detail"] == (
        "Permission not found"
    )


def test_update_permission(
    client,
    admin_headers,
    test_permission,
):

    response = client.put(
        f"/api/v1/permissions/{test_permission.id}",
        json={
            "description": "Updated description",
        },
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["description"] == (
        "Updated description"
    )


def test_update_missing_permission(
    client,
    admin_headers,
):

    response = client.put(
        f"/api/v1/permissions/{uuid.uuid4()}",
        json={
            "description": "Updated",
        },
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert response.json()["detail"] == (
        "Permission not found"
    )


def test_delete_permission(
    client,
    admin_headers,
):

    payload = create_permission_payload()

    created = client.post(
        "/api/v1/permissions/",
        json=payload,
        headers=admin_headers,
    )

    permission_id = created.json()["id"]

    response = client.delete(
        f"/api/v1/permissions/{permission_id}",
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.json()["message"] == (
        "Permission deleted successfully"
    )


def test_delete_missing_permission(
    client,
    admin_headers,
):

    response = client.delete(
        f"/api/v1/permissions/{uuid.uuid4()}",
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert response.json()["detail"] == (
        "Permission not found"
    )


def test_normal_user_cannot_access_permissions(
    client,
    authenticated_headers,
):

    response = client.get(
        "/api/v1/permissions/",
        headers=authenticated_headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN