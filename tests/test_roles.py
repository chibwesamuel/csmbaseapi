import uuid

from fastapi import status


def create_role_payload():
    unique = uuid.uuid4().hex[:8]

    return {
        "name": f"Role {unique}",
        "description": "Test role",
    }


def test_create_role(
    client,
    admin_headers,
):
    payload = create_role_payload()

    response = client.post(
        "/roles/",
        json=payload,
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert data["name"] == payload["name"]
    assert data["description"] == payload["description"]


def test_duplicate_role(
    client,
    admin_headers,
):
    payload = create_role_payload()

    first = client.post(
        "/roles/",
        json=payload,
        headers=admin_headers,
    )

    assert first.status_code == status.HTTP_201_CREATED

    second = client.post(
        "/roles/",
        json=payload,
        headers=admin_headers,
    )

    assert second.status_code == status.HTTP_409_CONFLICT

    assert second.json()["detail"] == (
        "Role already exists"
    )


def test_list_roles(
    client,
    admin_headers,
):
    response = client.get(
        "/roles/",
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert "roles" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data
    assert "has_next" in data
    assert "has_previous" in data


def test_get_role(
    client,
    admin_headers,
):
    payload = create_role_payload()

    created = client.post(
        "/roles/",
        json=payload,
        headers=admin_headers,
    )

    assert created.status_code == status.HTTP_201_CREATED

    role_id = created.json()["id"]

    response = client.get(
        f"/roles/{role_id}",
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["name"] == payload["name"]


def test_get_missing_role(
    client,
    admin_headers,
):
    response = client.get(
        f"/roles/{uuid.uuid4()}",
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert response.json()["detail"] == (
        "Role not found"
    )


def test_update_role(
    client,
    admin_headers,
):
    payload = create_role_payload()

    created = client.post(
        "/roles/",
        json=payload,
        headers=admin_headers,
    )

    role_id = created.json()["id"]

    response = client.put(
        f"/roles/{role_id}",
        json={
            "description": "Updated role description",
        },
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["description"] == (
        "Updated role description"
    )


def test_update_missing_role(
    client,
    admin_headers,
):
    response = client.put(
        f"/roles/{uuid.uuid4()}",
        json={
            "description": "Updated",
        },
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert response.json()["detail"] == (
        "Role not found"
    )


def test_delete_role(
    client,
    admin_headers,
):
    payload = create_role_payload()

    created = client.post(
        "/roles/",
        json=payload,
        headers=admin_headers,
    )

    assert created.status_code == status.HTTP_201_CREATED

    role_id = created.json()["id"]

    response = client.delete(
        f"/roles/{role_id}",
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.json()["message"] == (
        "Role deleted successfully"
    )


def test_delete_missing_role(
    client,
    admin_headers,
):
    response = client.delete(
        f"/roles/{uuid.uuid4()}",
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert response.json()["detail"] == (
        "Role not found"
    )


def test_normal_user_cannot_access_roles(
    client,
    authenticated_headers,
):
    response = client.get(
        "/roles/",
        headers=authenticated_headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN