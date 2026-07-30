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
        in response.json()["detail"]
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
        in response.json()["detail"]
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