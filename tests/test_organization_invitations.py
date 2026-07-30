import uuid


def create_test_organization(
    client,
    authenticated_headers,
):
    unique = uuid.uuid4().hex[:8]

    payload = {
        "name": f"Invitation Org {unique}",
        "slug": f"invitation-org-{unique}",
        "description": "Organization invitation tests",
    }

    response = client.post(
        "/api/v1/organizations/",
        json=payload,
        headers=authenticated_headers,
    )

    assert response.status_code == 201

    return response.json()


def test_list_organization_invitations_empty(
    client,
    authenticated_headers,
):

    organization = create_test_organization(
        client,
        authenticated_headers,
    )

    response = client.get(
        f"/api/v1/organizations/{organization['id']}/invitations",
        headers=authenticated_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert "total" in data
    assert "invitations" in data
    assert data["total"] == 0


def test_create_invitation_organization_not_found(
    client,
    admin_headers,
    test_role,
):

    response = client.post(
        f"/api/v1/organizations/{uuid.uuid4()}/invitations",
        json={
            "email": "invite@example.com",
            "role_id": str(test_role.id),
        },
        headers=admin_headers,
    )

    assert response.status_code == 404


def test_get_invitation_invalid_token(
    client,
):

    response = client.get(
        "/api/v1/organizations/invitations/invalid-token",
    )

    assert response.status_code == 404


def test_accept_invalid_invitation(
    client,
    authenticated_headers,
):

    response = client.post(
        "/api/v1/organizations/invitations/accept",
        json={
            "token": "invalid-token",
        },
        headers=authenticated_headers,
    )

    assert response.status_code == 400


def test_cancel_unknown_invitation(
    client,
    authenticated_headers,
):

    organization = create_test_organization(
        client,
        authenticated_headers,
    )

    response = client.delete(
        f"/api/v1/organizations/{organization['id']}/invitations/{uuid.uuid4()}",
        headers=authenticated_headers,
    )

    assert response.status_code == 400