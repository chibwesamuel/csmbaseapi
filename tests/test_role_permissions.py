import uuid


def test_assign_permission(
    client,
    admin_headers,
    test_role,
    test_permission,
):

    response = client.post(
        f"/roles/{test_role.id}/permissions/{test_permission.id}",
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "users.view"



def test_duplicate_permission_assignment(
    client,
    admin_headers,
    test_role,
    test_permission,
):

    client.post(
        f"/roles/{test_role.id}/permissions/{test_permission.id}",
        headers=admin_headers,
    )

    response = client.post(
        f"/roles/{test_role.id}/permissions/{test_permission.id}",
        headers=admin_headers,
    )

    assert response.status_code == 409

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
        f"/roles/{test_role.id}/permissions/{test_permission.id}",
        headers=admin_headers,
    )

    response = client.get(
        f"/roles/{test_role.id}/permissions",
        headers=admin_headers,
    )

    assert response.status_code == 200

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
        f"/roles/{test_role.id}/permissions/{test_permission.id}",
        headers=admin_headers,
    )

    response = client.delete(
        f"/roles/{test_role.id}/permissions/{test_permission.id}",
        headers=admin_headers,
    )

    assert response.status_code == 200

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
        f"/roles/{test_role.id}/permissions/{test_permission.id}",
        headers=admin_headers,
    )

    assert response.status_code == 409

    assert (
        "not assigned"
        in response.json()["detail"]
    )