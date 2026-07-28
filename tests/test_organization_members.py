import uuid


def create_test_organization(client, headers):
    """
    Helper function to create an organization.
    """

    unique = uuid.uuid4().hex[:8]

    response = client.post(
        "/organizations/",
        json={
            "name": f"Org {unique}",
            "slug": f"org-{unique}",
            "description": "Testing organization",
        },
        headers=headers,
    )

    assert response.status_code == 201

    return response.json()


def create_test_user(client):
    """
    Helper function to create a user.
    """

    unique = uuid.uuid4().hex[:8]

    response = client.post(
        "/auth/register",
        json={
            "email": f"user_{unique}@example.com",
            "username": f"user_{unique}",
            "password": "Password123!",
            "first_name": "John",
            "last_name": "Doe",
        },
    )

    assert response.status_code == 201

    return response.json()


def test_add_member(client, admin_headers):
    """
    Admin creates an organization then adds another user.
    """

    organization = create_test_organization(
        client,
        admin_headers,
    )

    user = create_test_user(client)

    response = client.post(
        f"/organizations/{organization['id']}/members",
        json={
            "user_id": user["id"],
            "role": "member",
        },
        headers=admin_headers,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["user_id"] == user["id"]
    assert data["role"] == "member"


def test_duplicate_member(client, admin_headers):

    organization = create_test_organization(
        client,
        admin_headers,
    )

    user = create_test_user(client)

    payload = {
        "user_id": user["id"],
        "role": "member",
    }

    first = client.post(
        f"/organizations/{organization['id']}/members",
        json=payload,
        headers=admin_headers,
    )

    assert first.status_code == 201

    second = client.post(
        f"/organizations/{organization['id']}/members",
        json=payload,
        headers=admin_headers,
    )

    assert second.status_code == 409

    assert second.json()["detail"] == (
        "User is already a member of this organization"
    )


def test_add_member_organization_not_found(
    client,
    admin_headers,
):

    user = create_test_user(client)

    response = client.post(
        f"/organizations/{uuid.uuid4()}/members",
        json={
            "user_id": user["id"],
            "role": "member",
        },
        headers=admin_headers,
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Organization not found"
    )


def test_add_member_user_not_found(
    client,
    admin_headers,
):

    organization = create_test_organization(
        client,
        admin_headers,
    )

    response = client.post(
        f"/organizations/{organization['id']}/members",
        json={
            "user_id": str(uuid.uuid4()),
            "role": "member",
        },
        headers=admin_headers,
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "User not found"
    )


def test_list_members(client, admin_headers):

    organization = create_test_organization(
        client,
        admin_headers,
    )

    response = client.get(
        f"/organizations/{organization['id']}/members",
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert "members" in data
    assert "total" in data


def test_update_member_role(client, admin_headers):

    organization = create_test_organization(
        client,
        admin_headers,
    )

    user = create_test_user(client)

    client.post(
        f"/organizations/{organization['id']}/members",
        json={
            "user_id": user["id"],
            "role": "member",
        },
        headers=admin_headers,
    )

    response = client.patch(
        f"/organizations/{organization['id']}/members/{user['id']}",
        json={
            "role": "admin",
        },
        headers=admin_headers,
    )

    assert response.status_code == 200

    assert response.json()["role"] == "admin"


def test_update_missing_membership(
    client,
    admin_headers,
):

    organization = create_test_organization(
        client,
        admin_headers,
    )

    response = client.patch(
        f"/organizations/{organization['id']}/members/{uuid.uuid4()}",
        json={
            "role": "admin",
        },
        headers=admin_headers,
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Membership not found"
    )


def test_remove_member(client, admin_headers):

    organization = create_test_organization(
        client,
        admin_headers,
    )

    user = create_test_user(client)

    client.post(
        f"/organizations/{organization['id']}/members",
        json={
            "user_id": user["id"],
            "role": "member",
        },
        headers=admin_headers,
    )

    response = client.delete(
        f"/organizations/{organization['id']}/members/{user['id']}",
        headers=admin_headers,
    )

    assert response.status_code == 200

    assert response.json()["message"] == (
        "Member removed successfully"
    )


def test_remove_missing_member(
    client,
    admin_headers,
):

    organization = create_test_organization(
        client,
        admin_headers,
    )

    response = client.delete(
        f"/organizations/{organization['id']}/members/{uuid.uuid4()}",
        headers=admin_headers,
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Membership not found"
    )


def test_cannot_remove_last_owner(
    client,
    admin_headers,
):

    organization = create_test_organization(
        client,
        admin_headers,
    )

    members = client.get(
        f"/organizations/{organization['id']}/members",
        headers=admin_headers,
    )

    assert members.status_code == 200

    owner_id = members.json()["members"][0]["user_id"]

    response = client.delete(
        f"/organizations/{organization['id']}/members/{owner_id}",
        headers=admin_headers,
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Cannot remove the last owner of an organization"
    )


def test_cannot_change_last_owner_role(
    client,
    admin_headers,
):

    organization = create_test_organization(
        client,
        admin_headers,
    )

    members = client.get(
        f"/organizations/{organization['id']}/members",
        headers=admin_headers,
    )

    assert members.status_code == 200

    owner_id = members.json()["members"][0]["user_id"]

    response = client.patch(
        f"/organizations/{organization['id']}/members/{owner_id}",
        json={
            "role": "admin",
        },
        headers=admin_headers,
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "An organization must have at least one owner"
    )

def test_normal_user_cannot_list_members(
    client,
    authenticated_headers,
):
    organization = create_test_organization(
        client,
        authenticated_headers,
    )

    response = client.get(
        f"/organizations/{organization['id']}/members",
        headers=authenticated_headers,
    )

    assert response.status_code == 403

def test_normal_user_cannot_add_member(
    client,
    authenticated_headers,
):
    organization = create_test_organization(
        client,
        authenticated_headers,
    )

    user = create_test_user(client)

    response = client.post(
        f"/organizations/{organization['id']}/members",
        json={
            "user_id": user["id"],
            "role": "member",
        },
        headers=authenticated_headers,
    )

    assert response.status_code == 403

def test_normal_user_cannot_update_member_role(
    client,
    authenticated_headers,
    admin_headers,
):
    organization = create_test_organization(
        client,
        admin_headers,
    )

    user = create_test_user(client)

    client.post(
        f"/organizations/{organization['id']}/members",
        json={
            "user_id": user["id"],
            "role": "member",
        },
        headers=admin_headers,
    )

    response = client.patch(
        f"/organizations/{organization['id']}/members/{user['id']}",
        json={
            "role": "admin",
        },
        headers=authenticated_headers,
    )

    assert response.status_code == 403

def test_normal_user_cannot_remove_member(
    client,
    authenticated_headers,
    admin_headers,
):
    organization = create_test_organization(
        client,
        admin_headers,
    )

    user = create_test_user(client)

    client.post(
        f"/organizations/{organization['id']}/members",
        json={
            "user_id": user["id"],
            "role": "member",
        },
        headers=admin_headers,
    )

    response = client.delete(
        f"/organizations/{organization['id']}/members/{user['id']}",
        headers=authenticated_headers,
    )

    assert response.status_code == 403