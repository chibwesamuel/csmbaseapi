import uuid


def test_add_member(client, admin_headers):
    """
    Admin creates an organization then adds another user.
    """

    unique = uuid.uuid4().hex[:8]

    # Create organization
    organization = client.post(
        "/organizations/",
        json={
            "name": f"Org {unique}",
            "slug": f"org-{unique}",
            "description": "Testing",
        },
        headers=admin_headers,
    )

    assert organization.status_code == 201

    organization_id = organization.json()["id"]

    # Create user
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
        f"/organizations/{organization_id}/members",
        json={
            "user_id": user_id,
            "role": "member",
        },
        headers=admin_headers,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["user_id"] == user_id
    assert data["role"] == "member"


def test_duplicate_member(client, admin_headers):

    unique = uuid.uuid4().hex[:8]

    organization = client.post(
        "/organizations/",
        json={
            "name": f"Org {unique}",
            "slug": f"org-{unique}",
        },
        headers=admin_headers,
    )

    organization_id = organization.json()["id"]

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

    payload = {
        "user_id": user_id,
        "role": "member",
    }

    first = client.post(
        f"/organizations/{organization_id}/members",
        json=payload,
        headers=admin_headers,
    )

    assert first.status_code == 201

    second = client.post(
        f"/organizations/{organization_id}/members",
        json=payload,
        headers=admin_headers,
    )

    assert second.status_code == 409
    assert second.json()["detail"] == (
        "User is already a member of this organization"
    )


def test_list_members(client, admin_headers):

    unique = uuid.uuid4().hex[:8]

    organization = client.post(
        "/organizations/",
        json={
            "name": f"Org {unique}",
            "slug": f"org-{unique}",
        },
        headers=admin_headers,
    )

    organization_id = organization.json()["id"]

    response = client.get(
        f"/organizations/{organization_id}/members",
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert "members" in data
    assert "total" in data


def test_update_member_role(client, admin_headers):

    unique = uuid.uuid4().hex[:8]

    organization = client.post(
        "/organizations/",
        json={
            "name": f"Org {unique}",
            "slug": f"org-{unique}",
        },
        headers=admin_headers,
    )

    organization_id = organization.json()["id"]

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
        f"/organizations/{organization_id}/members",
        json={
            "user_id": user_id,
            "role": "member",
        },
        headers=admin_headers,
    )

    response = client.patch(
        f"/organizations/{organization_id}/members/{user_id}",
        json={
            "role": "admin",
        },
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["role"] == "admin"


def test_remove_member(client, admin_headers):

    unique = uuid.uuid4().hex[:8]

    organization = client.post(
        "/organizations/",
        json={
            "name": f"Org {unique}",
            "slug": f"org-{unique}",
        },
        headers=admin_headers,
    )

    organization_id = organization.json()["id"]

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
        f"/organizations/{organization_id}/members",
        json={
            "user_id": user_id,
            "role": "member",
        },
        headers=admin_headers,
    )

    response = client.delete(
        f"/organizations/{organization_id}/members/{user_id}",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Member removed successfully"