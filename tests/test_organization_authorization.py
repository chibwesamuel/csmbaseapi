import uuid


def create_organization(
    client,
    headers,
    name_prefix="Organization",
):
    """
    Helper to create an organization.
    """

    unique = uuid.uuid4().hex[:8]

    response = client.post(
        "/api/v1/organizations/",
        json={
            "name": f"{name_prefix} {unique}",
            "slug": f"{name_prefix.lower()}-{unique}",
            "description": "Authorization test organization",
        },
        headers=headers,
    )

    assert response.status_code == 201

    return response.json()



def create_user(client):
    """
    Helper to create a normal user.
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



def login_user(client, user):
    """
    Login helper to obtain access token.
    """

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": user["email"],
            "password": "Password123!",
        },
    )

    assert response.status_code == 200, response.json()

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }



def test_member_can_access_own_organization_members(
    client,
    admin_headers,
):
    """
    A user belonging to an organization can view members.
    """

    organization = create_organization(
        client,
        admin_headers,
    )

    response = client.get(
        f"/api/v1/organizations/{organization['id']}/members",
        headers=admin_headers,
    )

    assert response.status_code == 200



def test_user_from_another_organization_cannot_access_members(
    client,
    admin_headers,
):
    """
    Users must not access organizations they do not belong to.
    """

    organization_one = create_organization(
        client,
        admin_headers,
        "Organization One",
    )

    organization_two = create_organization(
        client,
        admin_headers,
        "Organization Two",
    )

    user = create_user(client)

    user_headers = login_user(
        client,
        user,
    )

    # User is not a member of either organization.

    response = client.get(
        f"/api/v1/organizations/{organization_one['id']}/members",
        headers=user_headers,
    )

    assert response.status_code == 403



def test_normal_member_cannot_add_members(
    client,
    admin_headers,
):
    """
    Regular organization members cannot manage membership.
    """

    organization = create_organization(
        client,
        admin_headers,
    )

    user = create_user(client)

    user_headers = login_user(
        client,
        user,
    )

    response = client.post(
        f"/api/v1/organizations/{organization['id']}/members",
        json={
            "user_id": user["id"],
            "role": "member",
        },
        headers=user_headers,
    )

    assert response.status_code == 403



def test_admin_can_manage_members(
    client,
    admin_headers,
):
    """
    Organization admins should be allowed to add members.
    
    This will initially fail until organization-scoped
    authorization is wired into the API.
    """

    organization = create_organization(
        client,
        admin_headers,
    )

    user = create_user(client)

    response = client.post(
        f"/api/v1/organizations/{organization['id']}/members",
        json={
            "user_id": user["id"],
            "role": "member",
        },
        headers=admin_headers,
    )

    assert response.status_code == 201



def test_owner_can_delete_organization(
    client,
    admin_headers,
):
    """
    Organization owners can delete organizations.
    """

    organization = create_organization(
        client,
        admin_headers,
    )

    response = client.delete(
        f"/api/v1/organizations/{organization['id']}",
        headers=admin_headers,
    )

    assert response.status_code == 200