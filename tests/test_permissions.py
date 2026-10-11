import uuid

from fastapi import status
from app.models.permission import Permission
from app.models.role import Role
from app.repositories.user_role import assign_role_to_user
from tests.seed import seed_permissions


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

    assert second.json()["message"] == (
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

    assert response.json()["message"] == (
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

    assert response.json()["message"] == (
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

    assert response.json()["message"] == (
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


def test_non_superuser_cannot_delete_system_permission(
    client,
    db,
    registered_user,
    unique_user,
):
    """
    A non-superuser with permissions.delete must not be
    able to delete a built-in system permission.
    """

    seed_permissions(db)

    permission = (
        db.query(Permission)
        .filter(
            Permission.name == "users.view"
        )
        .first()
    )

    assert permission is not None

    delete_permission = (
        db.query(Permission)
        .filter(
            Permission.name == "permissions.delete"
        )
        .first()
    )

    assert delete_permission is not None

    role = Role(
        name=f"Permission Deleter {uuid.uuid4().hex[:8]}",
        description="Role for permission deletion test",
    )

    db.add(role)
    db.flush()

    role.permissions.append(delete_permission)

    db.commit()
    db.refresh(role)

    assign_role_to_user(
        db,
        registered_user,
        role,
    )

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": registered_user.email,
            "password": unique_user["password"],
        },
    )

    assert login_response.status_code == 200

    headers = {
        "Authorization": (
            f"Bearer "
            f"{login_response.json()['access_token']}"
        )
    }

    response = client.delete(
        f"/api/v1/permissions/{permission.id}",
        headers=headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    assert response.json()["message"] == (
        "Only a superuser can delete system permissions"
    )


def test_non_superuser_cannot_rename_system_permission(
    client,
    db,
    registered_user,
    unique_user,
):
    """
    A non-superuser with permissions.update cannot rename
    a built-in system permission.
    """

    seed_permissions(db)

    permission = (
        db.query(Permission)
        .filter(
            Permission.name == "users.view"
        )
        .first()
    )

    update_permission = (
        db.query(Permission)
        .filter(
            Permission.name == "permissions.update"
        )
        .first()
    )

    assert permission is not None
    assert update_permission is not None

    role = Role(
        name=f"Permission Editor {uuid.uuid4().hex[:8]}",
        description="Role for permission update test",
    )

    db.add(role)
    db.flush()
    role.permissions.append(update_permission)
    db.commit()

    assign_role_to_user(
        db,
        registered_user,
        role,
    )

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": registered_user.email,
            "password": unique_user["password"],
        },
    )

    assert login_response.status_code == 200

    headers = {
        "Authorization": (
            f"Bearer "
            f"{login_response.json()['access_token']}"
        )
    }

    response = client.put(
        f"/api/v1/permissions/{permission.id}",
        json={
            "name": "users.view.renamed",
        },
        headers=headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["message"] == (
        "Only a superuser can modify system permissions"
    )

    db.refresh(permission)
    assert permission.name == "users.view"


def test_custom_permission_remains_editable_and_deletable(
    client,
    admin_headers,
    registered_user,
    unique_user,
    db,
):
    """
    Custom permissions remain manageable by users with
    the corresponding permission-specific privileges.
    """

    seed_permissions(db)

    custom_permission_response = client.post(
        "/api/v1/permissions/",
        json=create_permission_payload(),
        headers=admin_headers,
    )

    assert custom_permission_response.status_code == (
        status.HTTP_201_CREATED
    )

    custom_permission = custom_permission_response.json()

    update_permission = (
        db.query(Permission)
        .filter(
            Permission.name == "permissions.update"
        )
        .first()
    )
    delete_permission = (
        db.query(Permission)
        .filter(
            Permission.name == "permissions.delete"
        )
        .first()
    )

    assert update_permission is not None
    assert delete_permission is not None

    role = Role(
        name=f"Custom Permission Manager {uuid.uuid4().hex[:8]}",
        description="Role for custom permission management test",
    )

    db.add(role)
    db.flush()
    role.permissions.extend(
        [update_permission, delete_permission]
    )
    db.commit()

    assign_role_to_user(
        db,
        registered_user,
        role,
    )

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": registered_user.email,
            "password": unique_user["password"],
        },
    )

    assert login_response.status_code == 200

    headers = {
        "Authorization": (
            f"Bearer "
            f"{login_response.json()['access_token']}"
        )
    }

    permission_id = custom_permission["id"]

    update_response = client.put(
        f"/api/v1/permissions/{permission_id}",
        json={
            "description": "Updated custom permission",
        },
        headers=headers,
    )

    assert update_response.status_code == status.HTTP_200_OK
    assert update_response.json()["description"] == (
        "Updated custom permission"
    )

    delete_response = client.delete(
        f"/api/v1/permissions/{permission_id}",
        headers=headers,
    )

    assert delete_response.status_code == status.HTTP_200_OK
    assert delete_response.json()["message"] == (
        "Permission deleted successfully"
    )
