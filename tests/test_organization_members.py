import uuid


def create_test_organization(client, headers):
    """
    Helper function to create an organization.
    """

    unique = uuid.uuid4().hex[:8]

    response = client.post(
        "/api/v1/organizations/",
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
        "/api/v1/auth/register",
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

    organization = create_test_organization(
        client,
        admin_headers,
    )

    user = create_test_user(client)

    response = client.post(
        f"/api/v1/organizations/{organization['id']}/members",
        json={
            "user_id": user["id"],
            "role": "member",
        },
        headers=admin_headers,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["user_id"] == user["id"]
    assert data["role"]["name"] == "member"


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
        f"/api/v1/organizations/{organization['id']}/members",
        json=payload,
        headers=admin_headers,
    )

    assert first.status_code == 201

    second = client.post(
        f"/api/v1/organizations/{organization['id']}/members",
        json=payload,
        headers=admin_headers,
    )

    assert second.status_code == 409

    assert second.json()["message"] == (
        "User is already a member of this organization"
    )


def test_add_member_organization_not_found(
    client,
    admin_headers,
):

    user = create_test_user(client)

    response = client.post(
        f"/api/v1/organizations/{uuid.uuid4()}/members",
        json={
            "user_id": user["id"],
            "role": "member",
        },
        headers=admin_headers,
    )

    assert response.status_code == 404

    assert response.json()["message"] == (
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
        f"/api/v1/organizations/{organization['id']}/members",
        json={
            "user_id": str(uuid.uuid4()),
            "role": "member",
        },
        headers=admin_headers,
    )

    assert response.status_code == 404

    assert response.json()["message"] == (
        "User not found"
    )


def test_list_members(client, admin_headers):

    organization = create_test_organization(
        client,
        admin_headers,
    )

    response = client.get(
        f"/api/v1/organizations/{organization['id']}/members",
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
        f"/api/v1/organizations/{organization['id']}/members",
        json={
            "user_id": user["id"],
            "role": "member",
        },
        headers=admin_headers,
    )

    response = client.patch(
        f"/api/v1/organizations/{organization['id']}/members/{user['id']}",
        json={
            "role": "admin",
        },
        headers=admin_headers,
    )

    assert response.status_code == 200

    assert response.json()["role"]["name"] == "admin"


def test_update_missing_membership(
    client,
    admin_headers,
):

    organization = create_test_organization(
        client,
        admin_headers,
    )

    response = client.patch(
        f"/api/v1/organizations/{organization['id']}/members/{uuid.uuid4()}",
        json={
            "role": "admin",
        },
        headers=admin_headers,
    )

    assert response.status_code == 404

    assert response.json()["message"] == (
        "Membership not found"
    )


def test_remove_member(client, admin_headers):

    organization = create_test_organization(
        client,
        admin_headers,
    )

    user = create_test_user(client)

    client.post(
        f"/api/v1/organizations/{organization['id']}/members",
        json={
            "user_id": user["id"],
            "role": "member",
        },
        headers=admin_headers,
    )

    response = client.delete(
        f"/api/v1/organizations/{organization['id']}/members/{user['id']}",
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
        f"/api/v1/organizations/{organization['id']}/members/{uuid.uuid4()}",
        headers=admin_headers,
    )

    assert response.status_code == 404

    assert response.json()["message"] == (
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
        f"/api/v1/organizations/{organization['id']}/members",
        headers=admin_headers,
    )

    assert members.status_code == 200

    owner_id = members.json()["members"][0]["user_id"]

    response = client.delete(
        f"/api/v1/organizations/{organization['id']}/members/{owner_id}",
        headers=admin_headers,
    )

    assert response.status_code == 400

    assert response.json()["message"] == (
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
        f"/api/v1/organizations/{organization['id']}/members",
        headers=admin_headers,
    )

    assert members.status_code == 200

    owner_id = members.json()["members"][0]["user_id"]

    response = client.patch(
        f"/api/v1/organizations/{organization['id']}/members/{owner_id}",
        json={
            "role": "admin",
        },
        headers=admin_headers,
    )

    assert response.status_code == 400

    assert response.json()["message"] == (
        "An organization must have at least one owner"
    )


def test_normal_user_cannot_list_members(
    client,
    admin_headers,
    authenticated_headers,
):

    organization = create_test_organization(
        client,
        admin_headers,
    )

    response = client.get(
        f"/api/v1/organizations/{organization['id']}/members",
        headers=authenticated_headers,
    )

    assert response.status_code == 403


def test_normal_user_cannot_add_member(
    client,
    admin_headers,
    authenticated_headers,
):

    organization = create_test_organization(
        client,
        admin_headers,
    )

    user = create_test_user(client)

    response = client.post(
        f"/api/v1/organizations/{organization['id']}/members",
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
        f"/api/v1/organizations/{organization['id']}/members",
        json={
            "user_id": user["id"],
            "role": "member",
        },
        headers=admin_headers,
    )

    response = client.patch(
        f"/api/v1/organizations/{organization['id']}/members/{user['id']}",
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
        f"/api/v1/organizations/{organization['id']}/members",
        json={
            "user_id": user["id"],
            "role": "member",
        },
        headers=admin_headers,
    )

    response = client.delete(
        f"/api/v1/organizations/{organization['id']}/members/{user['id']}",
        headers=authenticated_headers,
    )

    assert response.status_code == 403

def test_organization_member_can_list_members(
    client,
    organization_context,
):
    context = organization_context
    organization_id = context["organization"]["id"]

    response = client.get(
        f"/api/v1/organizations/{organization_id}/members",
        headers=context["member_headers"],
    )

    assert response.status_code == 200


def test_non_member_cannot_list_members(
    client,
    organization_context,
):
    context = organization_context
    organization_id = context["organization"]["id"]

    response = client.get(
        f"/api/v1/organizations/{organization_id}/members",
        headers=context["outsider_headers"],
    )

    assert response.status_code == 403


def test_organization_member_cannot_add_member(
    client,
    organization_context,
):
    context = organization_context
    organization_id = context["organization"]["id"]

    user = create_test_user(client)

    response = client.post(
        f"/api/v1/organizations/{organization_id}/members",
        json={
            "user_id": user["id"],
            "role": "member",
        },
        headers=context["member_headers"],
    )

    assert response.status_code == 403


def test_organization_admin_can_add_member(
    client,
    organization_context,
):
    context = organization_context
    organization_id = context["organization"]["id"]

    user = create_test_user(client)

    response = client.post(
        f"/api/v1/organizations/{organization_id}/members",
        json={
            "user_id": user["id"],
            "role": "member",
        },
        headers=context["admin_headers"],
    )

    assert response.status_code == 201


def test_organization_member_cannot_change_role(
    client,
    organization_context,
):
    context = organization_context
    organization_id = context["organization"]["id"]

    response = client.patch(
        f"/api/v1/organizations/{organization_id}/members/{context['member'].id}",
        json={
            "role": "admin",
        },
        headers=context["member_headers"],
    )

    assert response.status_code == 403


def test_organization_admin_can_change_role(
    client,
    organization_context,
):
    context = organization_context
    organization_id = context["organization"]["id"]

    response = client.patch(
        f"/api/v1/organizations/{organization_id}/members/{context['member'].id}",
        json={
            "role": "admin",
        },
        headers=context["admin_headers"],
    )

    assert response.status_code == 200
    assert response.json()["role"]["name"] == "admin"


def test_organization_member_cannot_remove_member(
    client,
    organization_context,
):
    context = organization_context
    organization_id = context["organization"]["id"]

    response = client.delete(
        f"/api/v1/organizations/{organization_id}/members/{context['member'].id}",
        headers=context["member_headers"],
    )

    assert response.status_code == 403


def test_organization_admin_can_remove_member(
    client,
    organization_context,
):
    context = organization_context
    organization_id = context["organization"]["id"]

    response = client.delete(
        f"/api/v1/organizations/{organization_id}/members/{context['member'].id}",
        headers=context["admin_headers"],
    )

    assert response.status_code == 200