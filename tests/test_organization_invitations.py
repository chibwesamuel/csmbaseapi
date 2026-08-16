import uuid

from datetime import datetime, timedelta, timezone

from app.models.organization_invitation import (
    InvitationStatus,
    OrganizationInvitation,
)

from app.models.organization_member import (
    OrganizationMember,
)


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


def create_test_user(
    client,
):
    unique = uuid.uuid4().hex[:8]

    payload = {
        "email": f"invitee{unique}@example.com",
        "username": f"invitee{unique}",
        "password": "Password123!",
        "first_name": "Invitation",
        "last_name": "User",
    }

    response = client.post(
        "/api/v1/auth/register",
        json=payload,
    )

    assert response.status_code == 201

    return payload


def login_user(
    client,
    email,
    password,
):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 200

    return {
        "Authorization": (
            f"Bearer {response.json()['access_token']}"
        )
    }


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


def test_create_invitation_success(
    client,
    authenticated_headers,
    test_role,
):

    organization = create_test_organization(
        client,
        authenticated_headers,
    )

    email = (
        f"invite{uuid.uuid4().hex[:8]}"
        "@example.com"
    )

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/invitations"
        ),
        json={
            "email": email,
            "role_id": str(test_role.id),
        },
        headers=authenticated_headers,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["organization_id"] == organization["id"]
    assert data["email"] == email
    assert data["status"] == "pending"
    assert data["role_id"] == str(test_role.id)
    assert data["token"]


def test_create_duplicate_pending_invitation(
    client,
    authenticated_headers,
    test_role,
):

    organization = create_test_organization(
        client,
        authenticated_headers,
    )

    email = (
        f"duplicate{uuid.uuid4().hex[:8]}"
        "@example.com"
    )

    payload = {
        "email": email,
        "role_id": str(test_role.id),
    }

    first_response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/invitations"
        ),
        json=payload,
        headers=authenticated_headers,
    )

    assert first_response.status_code == 201

    second_response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/invitations"
        ),
        json=payload,
        headers=authenticated_headers,
    )

    assert second_response.status_code == 409

    assert second_response.json()["message"] == (
        "A pending invitation already exists for this email"
    )


def test_get_invitation_invalid_token(
    client,
):

    response = client.get(
        "/api/v1/organizations/invitations/invalid-token",
    )

    assert response.status_code == 404


def test_get_invitation_success(
    client,
    authenticated_headers,
    test_role,
):

    organization = create_test_organization(
        client,
        authenticated_headers,
    )

    email = (
        f"retrieve{uuid.uuid4().hex[:8]}"
        "@example.com"
    )

    create_response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/invitations"
        ),
        json={
            "email": email,
            "role_id": str(test_role.id),
        },
        headers=authenticated_headers,
    )

    assert create_response.status_code == 201

    invitation = create_response.json()

    response = client.get(
        (
            "/api/v1/organizations/invitations/"
            f"{invitation['token']}"
        ),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == invitation["id"]
    assert data["organization_id"] == organization["id"]
    assert data["email"] == email
    assert data["status"] == "pending"


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


def test_accept_invitation_success(
    client,
    authenticated_headers,
    test_role,
    db,
):

    organization = create_test_organization(
        client,
        authenticated_headers,
    )

    invitee = create_test_user(client)

    invitation_response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/invitations"
        ),
        json={
            "email": invitee["email"],
            "role_id": str(test_role.id),
        },
        headers=authenticated_headers,
    )

    assert invitation_response.status_code == 201

    invitation = invitation_response.json()

    invitee_headers = login_user(
        client,
        invitee["email"],
        invitee["password"],
    )

    response = client.post(
        "/api/v1/organizations/invitations/accept",
        json={
            "token": invitation["token"],
        },
        headers=invitee_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == (
        "Invitation accepted successfully"
    )

    assert data["organization_id"] == organization["id"]

    membership = (
        db.query(OrganizationMember)
        .filter(
            OrganizationMember.organization_id
            == organization["id"],
        )
        .join(
            OrganizationMember.user
        )
        .filter(
            OrganizationMember.user_id
            != invitation["invited_by"],
        )
        .first()
    )

    assert membership is not None
    assert membership.user_id is not None
    assert membership.role_id == test_role.id

    accepted_invitation = (
        db.query(OrganizationInvitation)
        .filter(
            OrganizationInvitation.id
            == invitation["id"],
        )
        .first()
    )

    assert accepted_invitation is not None
    assert accepted_invitation.status == (
        InvitationStatus.ACCEPTED
    )
    assert accepted_invitation.accepted_at is not None


def test_accept_invitation_already_member(
    client,
    authenticated_headers,
    test_role,
):

    organization = create_test_organization(
        client,
        authenticated_headers,
    )

    invitation_response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/invitations"
        ),
        json={
            "email": f"member{uuid.uuid4().hex[:8]}@example.com",
            "role_id": str(test_role.id),
        },
        headers=authenticated_headers,
    )

    assert invitation_response.status_code == 201

    invitation = invitation_response.json()

    response = client.post(
        "/api/v1/organizations/invitations/accept",
        json={
            "token": invitation["token"],
        },
        headers=authenticated_headers,
    )

    assert response.status_code == 400

    assert response.json()["message"] == (
        "User is already a member of this organization"
    )


def test_accept_expired_invitation(
    client,
    authenticated_headers,
    test_role,
    db,
):

    organization = create_test_organization(
        client,
        authenticated_headers,
    )

    invitee = create_test_user(client)

    invitation_response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/invitations"
        ),
        json={
            "email": invitee["email"],
            "role_id": str(test_role.id),
        },
        headers=authenticated_headers,
    )

    assert invitation_response.status_code == 201

    invitation = invitation_response.json()

    invitation_model = (
        db.query(OrganizationInvitation)
        .filter(
            OrganizationInvitation.id
            == invitation["id"],
        )
        .first()
    )

    assert invitation_model is not None

    invitation_model.expires_at = (
        datetime.now(timezone.utc)
        - timedelta(days=1)
    )

    db.commit()

    invitee_headers = login_user(
        client,
        invitee["email"],
        invitee["password"],
    )

    response = client.post(
        "/api/v1/organizations/invitations/accept",
        json={
            "token": invitation["token"],
        },
        headers=invitee_headers,
    )

    assert response.status_code == 400

    assert response.json()["message"] == (
        "Invitation has expired"
    )

    db.refresh(invitation_model)

    assert invitation_model.status == (
        InvitationStatus.EXPIRED
    )


def test_cancel_unknown_invitation(
    client,
    authenticated_headers,
):

    organization = create_test_organization(
        client,
        authenticated_headers,
    )

    response = client.delete(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/invitations/"
            f"{uuid.uuid4()}"
        ),
        headers=authenticated_headers,
    )

    assert response.status_code == 400


def test_cancel_invitation_success(
    client,
    authenticated_headers,
    test_role,
    db,
):

    organization = create_test_organization(
        client,
        authenticated_headers,
    )

    invitation_response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/invitations"
        ),
        json={
            "email": (
                f"cancel{uuid.uuid4().hex[:8]}"
                "@example.com"
            ),
            "role_id": str(test_role.id),
        },
        headers=authenticated_headers,
    )

    assert invitation_response.status_code == 201

    invitation = invitation_response.json()

    response = client.delete(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/invitations/"
            f"{invitation['id']}"
        ),
        headers=authenticated_headers,
    )

    assert response.status_code == 200

    assert response.json()["message"] == (
        "Invitation cancelled successfully"
    )

    invitation_model = (
        db.query(OrganizationInvitation)
        .filter(
            OrganizationInvitation.id
            == invitation["id"],
        )
        .first()
    )

    assert invitation_model is not None
    assert invitation_model.status == (
        InvitationStatus.CANCELLED
    )