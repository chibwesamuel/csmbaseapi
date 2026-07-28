import uuid

from fastapi import status


def test_assign_role(client, admin_headers, db, admin_role):

    unique = uuid.uuid4().hex[:8]

    user = client.post(
        "/auth/register",
        json={
            "email": f"user_{unique}@example.com",
            "username": f"user_{unique}",
            "password": "Password123!",
            "first_name": "John",
            "last_name": "Doe",
        },
    )

    assert user.status_code == 201

    user_id = user.json()["id"]

    response = client.post(
        f"/users/{user_id}/roles/{admin_role.id}",
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Admin"


def test_duplicate_role_assignment(
    client,
    admin_headers,
    db,
    admin_role,
):

    unique = uuid.uuid4().hex[:8]

    user = client.post(
        "/auth/register",
        json={
            "email": f"user_{unique}@example.com",
            "username": f"user_{unique}",
            "password": "Password123!",
            "first_name": "John",
            "last_name": "Doe",
        },
    )

    user_id = user.json()["id"]

    client.post(
        f"/users/{user_id}/roles/{admin_role.id}",
        headers=admin_headers,
    )

    second = client.post(
        f"/users/{user_id}/roles/{admin_role.id}",
        headers=admin_headers,
    )

    assert second.status_code == 409
    assert "already assigned" in second.json()["detail"]


def test_list_user_roles(
    client,
    admin_headers,
    db,
    admin_role,
):

    unique = uuid.uuid4().hex[:8]

    user = client.post(
        "/auth/register",
        json={
            "email": f"user_{unique}@example.com",
            "username": f"user_{unique}",
            "password": "Password123!",
            "first_name": "John",
            "last_name": "Doe",
        },
    )

    user_id = user.json()["id"]

    client.post(
        f"/users/{user_id}/roles/{admin_role.id}",
        headers=admin_headers,
    )

    response = client.get(
        f"/users/{user_id}/roles",
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) >= 1
    assert any(role["name"] == "Admin" for role in data)


def test_remove_role(
    client,
    admin_headers,
    db,
    admin_role,
):

    unique = uuid.uuid4().hex[:8]

    user = client.post(
        "/auth/register",
        json={
            "email": f"user_{unique}@example.com",
            "username": f"user_{unique}",
            "password": "Password123!",
            "first_name": "John",
            "last_name": "Doe",
        },
    )

    user_id = user.json()["id"]

    client.post(
        f"/users/{user_id}/roles/{admin_role.id}",
        headers=admin_headers,
    )

    response = client.delete(
        f"/users/{user_id}/roles/{admin_role.id}",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["message"] == (
        "Role removed from user successfully"
    )


def test_remove_unassigned_role(
    client,
    admin_headers,
    db,
    admin_role,
):

    unique = uuid.uuid4().hex[:8]

    user = client.post(
        "/auth/register",
        json={
            "email": f"user_{unique}@example.com",
            "username": f"user_{unique}",
            "password": "Password123!",
            "first_name": "John",
            "last_name": "Doe",
        },
    )

    user_id = user.json()["id"]

    response = client.delete(
        f"/users/{user_id}/roles/{admin_role.id}",
        headers=admin_headers,
    )

    assert response.status_code == 409
    assert "not assigned" in response.json()["detail"]


def test_normal_user_cannot_assign_roles(
    client,
    authenticated_headers,
    admin_role,
):
    unique = uuid.uuid4().hex[:8]

    user = client.post(
        "/auth/register",
        json={
            "email": f"user_{unique}@example.com",
            "username": f"user_{unique}",
            "password": "Password123!",
            "first_name": "John",
            "last_name": "Doe",
        },
    )

    assert user.status_code == status.HTTP_201_CREATED

    user_id = user.json()["id"]

    response = client.post(
        f"/users/{user_id}/roles/{admin_role.id}",
        headers=authenticated_headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_normal_user_cannot_remove_roles(
    client,
    authenticated_headers,
    admin_headers,
    admin_role,
):
    unique = uuid.uuid4().hex[:8]

    user = client.post(
        "/auth/register",
        json={
            "email": f"user_{unique}@example.com",
            "username": f"user_{unique}",
            "password": "Password123!",
            "first_name": "John",
            "last_name": "Doe",
        },
    )

    assert user.status_code == status.HTTP_201_CREATED

    user_id = user.json()["id"]

    # Assign the role as an admin first
    assign = client.post(
        f"/users/{user_id}/roles/{admin_role.id}",
        headers=admin_headers,
    )

    assert assign.status_code == status.HTTP_200_OK

    # Attempt to remove it as a normal user
    response = client.delete(
        f"/users/{user_id}/roles/{admin_role.id}",
        headers=authenticated_headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_normal_user_cannot_list_user_roles(
    client,
    authenticated_headers,
):
    unique = uuid.uuid4().hex[:8]

    user = client.post(
        "/auth/register",
        json={
            "email": f"user_{unique}@example.com",
            "username": f"user_{unique}",
            "password": "Password123!",
            "first_name": "John",
            "last_name": "Doe",
        },
    )

    assert user.status_code == status.HTTP_201_CREATED

    user_id = user.json()["id"]

    response = client.get(
        f"/users/{user_id}/roles",
        headers=authenticated_headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN