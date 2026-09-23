import uuid

from fastapi import status
from app.models.user import User
from app.models.permission import Permission
from app.models.role import Role


def test_assign_role(client, admin_headers, db, admin_role):

    unique = uuid.uuid4().hex[:8]

    user = client.post(
        "/api/v1/auth/register",
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
        f"/api/v1/users/{user_id}/roles/{admin_role.id}",
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
        "/api/v1/auth/register",
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
        f"/api/v1/users/{user_id}/roles/{admin_role.id}",
        headers=admin_headers,
    )

    second = client.post(
        f"/api/v1/users/{user_id}/roles/{admin_role.id}",
        headers=admin_headers,
    )

    assert second.status_code == 409
    assert "already assigned" in second.json()["message"]


def test_list_user_roles(
    client,
    admin_headers,
    db,
    admin_role,
):

    unique = uuid.uuid4().hex[:8]

    user = client.post(
        "/api/v1/auth/register",
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
        f"/api/v1/users/{user_id}/roles/{admin_role.id}",
        headers=admin_headers,
    )

    response = client.get(
        f"/api/v1/users/{user_id}/roles",
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
        "/api/v1/auth/register",
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
        f"/api/v1/users/{user_id}/roles/{admin_role.id}",
        headers=admin_headers,
    )

    response = client.delete(
        f"/api/v1/users/{user_id}/roles/{admin_role.id}",
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
        "/api/v1/auth/register",
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
        f"/api/v1/users/{user_id}/roles/{admin_role.id}",
        headers=admin_headers,
    )

    assert response.status_code == 409
    assert "not assigned" in response.json()["message"]


def test_normal_user_cannot_assign_roles(
    client,
    authenticated_headers,
    admin_role,
):
    unique = uuid.uuid4().hex[:8]

    user = client.post(
        "/api/v1/auth/register",
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
        f"/api/v1/users/{user_id}/roles/{admin_role.id}",
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
        "/api/v1/auth/register",
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
        f"/api/v1/users/{user_id}/roles/{admin_role.id}",
        headers=admin_headers,
    )

    assert assign.status_code == status.HTTP_200_OK

    # Attempt to remove it as a normal user
    response = client.delete(
        f"/api/v1/users/{user_id}/roles/{admin_role.id}",
        headers=authenticated_headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_normal_user_cannot_list_user_roles(
    client,
    authenticated_headers,
):
    unique = uuid.uuid4().hex[:8]

    user = client.post(
        "/api/v1/auth/register",
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
        f"/api/v1/users/{user_id}/roles",
        headers=authenticated_headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_non_superuser_cannot_assign_admin_role(
    client,
    db,
    admin_role,
):
    """
    A non-superuser with users.update must not be able
    to assign the global Admin role.
    """

    unique = uuid.uuid4().hex[:8]

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": f"escalate_{unique}@example.com",
            "username": f"escalate_{unique}",
            "password": "Password123!",
            "first_name": "Escalation",
            "last_name": "Test",
        },
    )

    assert response.status_code == 201

    user_id = response.json()["id"]

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    assert user is not None

    permission = (
        db.query(Permission)
        .filter(
            Permission.name == "users.update"
        )
        .first()
    )

    assert permission is not None

    role = Role(
        name=f"user-updater-{unique}",
        description="Test users.update role",
    )

    role.permissions.append(permission)

    db.add(role)
    db.commit()
    db.refresh(role)

    user.roles.append(role)

    db.commit()
    db.refresh(user)

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": user.email,
            "password": "Password123!",
        },
    )

    assert login_response.status_code == 200

    headers = {
        "Authorization": (
            f"Bearer "
            f"{login_response.json()['access_token']}"
        )
    }

    response = client.post(
        (
            f"/api/v1/users/"
            f"{user_id}/roles/"
            f"{admin_role.id}"
        ),
        headers=headers,
    )

    assert response.status_code == 403

    assert response.json()["message"] == (
        "Only a superuser can assign the Admin role"
    )

    db.refresh(user)

    assert admin_role not in user.roles
