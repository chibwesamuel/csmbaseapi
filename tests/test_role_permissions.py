import uuid

from app.models.permission import Permission

from app.models.role import Role

from fastapi import status


def test_assign_permission(
    client,
    admin_headers,
    test_role,
    test_permission,
):
    response = client.post(
        f"/api/v1/roles/{test_role.id}/permissions/{test_permission.id}",
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["name"] == "users.view"


def test_duplicate_permission_assignment(
    client,
    admin_headers,
    test_role,
    test_permission,
):
    client.post(
        f"/api/v1/roles/{test_role.id}/permissions/{test_permission.id}",
        headers=admin_headers,
    )

    response = client.post(
        f"/api/v1/roles/{test_role.id}/permissions/{test_permission.id}",
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_409_CONFLICT

    assert (
        "already assigned"
        in response.json()["message"]
    )


def test_list_role_permissions(
    client,
    admin_headers,
    test_role,
    test_permission,
):
    client.post(
        f"/api/v1/roles/{test_role.id}/permissions/{test_permission.id}",
        headers=admin_headers,
    )

    response = client.get(
        f"/api/v1/roles/{test_role.id}/permissions",
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert len(data) >= 1

    assert any(
        permission["name"] == "users.view"
        for permission in data
    )


def test_remove_permission(
    client,
    admin_headers,
    test_role,
    test_permission,
):
    client.post(
        f"/api/v1/roles/{test_role.id}/permissions/{test_permission.id}",
        headers=admin_headers,
    )

    response = client.delete(
        f"/api/v1/roles/{test_role.id}/permissions/{test_permission.id}",
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_200_OK

    assert (
        response.json()["message"]
        == "Permission removed from role successfully"
    )


def test_remove_unassigned_permission(
    client,
    admin_headers,
    test_role,
    test_permission,
):
    response = client.delete(
        f"/api/v1/roles/{test_role.id}/permissions/{test_permission.id}",
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_409_CONFLICT

    assert (
        "not assigned"
        in response.json()["message"]
    )


def test_normal_user_cannot_assign_permissions(
    client,
    authenticated_headers,
    test_role,
    test_permission,
):
    response = client.post(
        f"/api/v1/roles/{test_role.id}/permissions/{test_permission.id}",
        headers=authenticated_headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_normal_user_cannot_remove_permissions(
    client,
    authenticated_headers,
    admin_headers,
    test_role,
    test_permission,
):
    client.post(
        f"/api/v1/roles/{test_role.id}/permissions/{test_permission.id}",
        headers=admin_headers,
    )

    response = client.delete(
        f"/api/v1/roles/{test_role.id}/permissions/{test_permission.id}",
        headers=authenticated_headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_normal_user_cannot_list_role_permissions(
    client,
    authenticated_headers,
    test_role,
):
    response = client.get(
        f"/api/v1/roles/{test_role.id}/permissions",
        headers=authenticated_headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_non_superuser_cannot_modify_role_permissions(
    client,
    admin_headers,
    db,
):
    """
    A non-superuser with roles.update cannot modify
    permissions assigned to a role.
    """

    # ---------------------------------------------------------
    # Create a normal user.
    # ---------------------------------------------------------

    unique = uuid.uuid4().hex[:8]

    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": f"rbac{unique}@example.com",
            "username": f"rbac{unique}",
            "password": "password123",
            "first_name": "RBAC",
            "last_name": "Test",
        },
    )

    assert register_response.status_code == 201

    user = register_response.json()

    # ---------------------------------------------------------
    # Create a custom role.
    # ---------------------------------------------------------

    role_response = client.post(
        "/api/v1/roles/",
        json={
            "name": f"RBAC Role {unique}",
            "description": "RBAC permission security test",
        },
        headers=admin_headers,
    )

    assert role_response.status_code == 201

    role = role_response.json()

    # ---------------------------------------------------------
    # Retrieve the roles.update and roles.create permissions.
    # ---------------------------------------------------------

    roles_update = (
        db.query(Permission)
        .filter(
            Permission.name == "roles.update"
        )
        .first()
    )

    roles_create = (
        db.query(Permission)
        .filter(
            Permission.name == "roles.create"
        )
        .first()
    )

    assert roles_update is not None
    assert roles_create is not None

    # ---------------------------------------------------------
    # Give the custom role roles.update.
    # ---------------------------------------------------------

    permission_response = client.post(
        (
            f"/api/v1/roles/"
            f"{role['id']}/permissions/"
            f"{roles_update.id}"
        ),
        headers=admin_headers,
    )

    assert permission_response.status_code == 200

    # ---------------------------------------------------------
    # Give the user the custom role.
    # ---------------------------------------------------------

    assign_role_response = client.post(
        (
            f"/api/v1/users/"
            f"{user['id']}/roles/"
            f"{role['id']}"
        ),
        headers=admin_headers,
    )

    assert assign_role_response.status_code == 200

    # ---------------------------------------------------------
    # Login as the non-superuser.
    # ---------------------------------------------------------

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": user["email"],
            "password": "password123",
        },
    )

    assert login_response.status_code == 200

    user_headers = {
        "Authorization": (
            f"Bearer "
            f"{login_response.json()['access_token']}"
        )
    }

    # ---------------------------------------------------------
    # Attempt to grant the user's own role an additional
    # privilege.
    # ---------------------------------------------------------

    response = client.post(
        (
            f"/api/v1/roles/"
            f"{role['id']}/permissions/"
            f"{roles_create.id}"
        ),
        headers=user_headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    assert response.json()["message"] == (
        "Only a superuser can modify role permissions"
    )

    db.expire_all()

    updated_role = (
        db.query(Role)
        .filter(
            Role.id == role["id"]
        )
        .first()
    )

    assert updated_role is not None

    assert all(
        permission.name != "roles.create"
        for permission in updated_role.permissions
    )


def test_non_superuser_cannot_revoke_role_permissions(
    client,
    admin_headers,
    db,
):
    """
    A non-superuser with roles.update cannot revoke
    permissions assigned to a role.
    """

    # ---------------------------------------------------------
    # Create a normal user.
    # ---------------------------------------------------------

    unique = uuid.uuid4().hex[:8]

    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": f"rbac{unique}@example.com",
            "username": f"rbac{unique}",
            "password": "password123",
            "first_name": "RBAC",
            "last_name": "Test",
        },
    )

    assert register_response.status_code == 201

    user = register_response.json()

    # ---------------------------------------------------------
    # Create a custom role.
    # ---------------------------------------------------------

    role_response = client.post(
        "/api/v1/roles/",
        json={
            "name": f"RBAC Role {unique}",
            "description": "RBAC permission security test",
        },
        headers=admin_headers,
    )

    assert role_response.status_code == 201

    role = role_response.json()

    # ---------------------------------------------------------
    # Retrieve the roles.update and roles.create permissions.
    # ---------------------------------------------------------

    roles_update = (
        db.query(Permission)
        .filter(
            Permission.name == "roles.update"
        )
        .first()
    )

    roles_create = (
        db.query(Permission)
        .filter(
            Permission.name == "roles.create"
        )
        .first()
    )

    assert roles_update is not None
    assert roles_create is not None

    # ---------------------------------------------------------
    # Give the custom role both permissions.
    # ---------------------------------------------------------

    response = client.post(
        (
            f"/api/v1/roles/"
            f"{role['id']}/permissions/"
            f"{roles_update.id}"
        ),
        headers=admin_headers,
    )

    assert response.status_code == 200

    response = client.post(
        (
            f"/api/v1/roles/"
            f"{role['id']}/permissions/"
            f"{roles_create.id}"
        ),
        headers=admin_headers,
    )

    assert response.status_code == 200

    # ---------------------------------------------------------
    # Give the user the custom role.
    # ---------------------------------------------------------

    assign_role_response = client.post(
        (
            f"/api/v1/users/"
            f"{user['id']}/roles/"
            f"{role['id']}"
        ),
        headers=admin_headers,
    )

    assert assign_role_response.status_code == 200

    # ---------------------------------------------------------
    # Login as the non-superuser.
    # ---------------------------------------------------------

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": user["email"],
            "password": "password123",
        },
    )

    assert login_response.status_code == 200

    user_headers = {
        "Authorization": (
            f"Bearer "
            f"{login_response.json()['access_token']}"
        )
    }

    # ---------------------------------------------------------
    # Attempt to revoke the user's own role permission.
    # ---------------------------------------------------------

    response = client.delete(
        (
            f"/api/v1/roles/"
            f"{role['id']}/permissions/"
            f"{roles_create.id}"
        ),
        headers=user_headers,
    )

    assert response.status_code == (
        status.HTTP_403_FORBIDDEN
    )

    assert response.json()["message"] == (
        "Only a superuser can modify role permissions"
    )

    # ---------------------------------------------------------
    # Confirm the permission remains assigned.
    # ---------------------------------------------------------

    db.expire_all()

    updated_role = (
        db.query(Role)
        .filter(
            Role.id == role["id"]
        )
        .first()
    )

    assert updated_role is not None

    assert any(
        permission.name == "roles.create"
        for permission in updated_role.permissions
    )
