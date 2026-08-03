import uuid


def test_create_organization(client, authenticated_headers):

    unique = uuid.uuid4().hex[:8]

    payload = {
        "name": f"Organization {unique}",
        "slug": f"organization-{unique}",
        "description": "Test organization",
    }

    response = client.post(
        "/api/v1/organizations/",
        json=payload,
        headers=authenticated_headers,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == payload["name"]
    assert data["slug"] == payload["slug"]


def test_duplicate_slug(client, authenticated_headers):

    unique = uuid.uuid4().hex[:8]

    payload = {
        "name": "Organization",
        "slug": f"duplicate-{unique}",
        "description": "Duplicate slug test",
    }

    client.post(
        "/api/v1/organizations/",
        json=payload,
        headers=authenticated_headers,
    )

    response = client.post(
        "/api/v1/organizations/",
        json=payload,
        headers=authenticated_headers,
    )

    assert response.status_code == 409


def test_duplicate_email(client, authenticated_headers):

    unique = uuid.uuid4().hex[:8]

    payload = {
        "name": f"Email Org {unique}",
        "slug": f"email-org-{unique}",
        "email": f"org_{unique}@example.com",
        "description": "Duplicate email test",
    }

    first_response = client.post(
        "/api/v1/organizations/",
        json=payload,
        headers=authenticated_headers,
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/api/v1/organizations/",
        json=payload,
        headers=authenticated_headers,
    )

    assert second_response.status_code == 409


def test_list_organizations(client, admin_headers):

    response = client.get(
        "/api/v1/organizations/",
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert "organizations" in data
    assert "total" in data


def test_get_my_organizations(client, authenticated_headers):

    unique = uuid.uuid4().hex[:8]

    payload = {
        "name": f"My Org {unique}",
        "slug": f"my-org-{unique}",
        "description": "Owned organization",
    }

    create = client.post(
        "/api/v1/organizations/",
        json=payload,
        headers=authenticated_headers,
    )

    assert create.status_code == 201

    response = client.get(
        "/api/v1/organizations/my",
        headers=authenticated_headers,
    )

    assert response.status_code == 200

    organizations = response.json()

    assert isinstance(organizations, list)

    assert any(
        org["slug"] == payload["slug"]
        for org in organizations
    )


def test_get_organization(client, admin_headers, authenticated_headers):

    unique = uuid.uuid4().hex[:8]

    payload = {
        "name": f"Get Org {unique}",
        "slug": f"get-org-{unique}",
        "description": "Get organization test",
    }

    create_response = client.post(
        "/api/v1/organizations/",
        json=payload,
        headers=authenticated_headers,
    )

    assert create_response.status_code == 201

    organization_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/organizations/{organization_id}",
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == organization_id
    assert data["slug"] == payload["slug"]


def test_update_organization(client, admin_headers, authenticated_headers):

    unique = uuid.uuid4().hex[:8]

    payload = {
        "name": f"Update Org {unique}",
        "slug": f"update-org-{unique}",
        "description": "Before update",
    }

    create_response = client.post(
        "/api/v1/organizations/",
        json=payload,
        headers=authenticated_headers,
    )

    assert create_response.status_code == 201

    organization_id = create_response.json()["id"]

    update_payload = {
        "name": "Updated Organization",
        "description": "Updated description",
    }

    response = client.put(
        f"/api/v1/organizations/{organization_id}",
        json=update_payload,
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == update_payload["name"]
    assert data["description"] == update_payload["description"]


def test_delete_organization(client, admin_headers, authenticated_headers):

    unique = uuid.uuid4().hex[:8]

    payload = {
        "name": f"Delete Org {unique}",
        "slug": f"delete-org-{unique}",
        "description": "Delete organization test",
    }

    create_response = client.post(
        "/api/v1/organizations/",
        json=payload,
        headers=authenticated_headers,
    )

    assert create_response.status_code == 201

    organization_id = create_response.json()["id"]

    response = client.delete(
        f"/api/v1/organizations/{organization_id}",
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Organization deleted successfully"


def test_get_organization_not_found(client, admin_headers):

    fake_id = uuid.uuid4()

    response = client.get(
        f"/api/v1/organizations/{fake_id}",
        headers=admin_headers,
    )

    assert response.status_code == 404

    assert response.json()["detail"] == "Organization not found"


def test_update_organization_not_found(client, admin_headers):

    fake_id = uuid.uuid4()

    payload = {
        "name": "Updated Name",
    }

    response = client.put(
        f"/api/v1/organizations/{fake_id}",
        json=payload,
        headers=admin_headers,
    )

    assert response.status_code == 404

    assert response.json()["detail"] == "Organization not found"


def test_delete_organization_not_found(client, admin_headers):

    fake_id = uuid.uuid4()

    response = client.delete(
        f"/api/v1/organizations/{fake_id}",
        headers=admin_headers,
    )

    assert response.status_code == 404

    assert response.json()["detail"] == "Organization not found"

def test_creator_becomes_organization_owner(
    client,
    authenticated_headers,
    db,
):

    unique = uuid.uuid4().hex[:8]

    payload = {
        "name": f"Owner Org {unique}",
        "slug": f"owner-org-{unique}",
    }

    response = client.post(
        "/api/v1/organizations/",
        json=payload,
        headers=authenticated_headers,
    )

    assert response.status_code == 201

    organization_id = response.json()["id"]

    from app.models.organization_member import OrganizationMember

    membership = (
        db.query(OrganizationMember)
        .filter(
            OrganizationMember.organization_id
            == organization_id
        )
        .first()
    )

    assert membership is not None
    assert membership.role.name == "owner"

def test_normal_user_cannot_list_organizations(
    client,
    authenticated_headers,
):

    response = client.get(
        "/api/v1/organizations/",
        headers=authenticated_headers,
    )

    assert response.status_code == 403

def test_normal_user_cannot_update_organization(
    client,
    authenticated_headers,
):

    response = client.put(
        f"/api/v1/organizations/{uuid.uuid4()}",
        json={
            "name": "Blocked Update",
        },
        headers=authenticated_headers,
    )

    assert response.status_code == 403

def test_normal_user_cannot_delete_organization(
    client,
    authenticated_headers,
):

    response = client.delete(
        f"/api/v1/organizations/{uuid.uuid4()}",
        headers=authenticated_headers,
    )

    assert response.status_code == 403

def test_invalid_organization_uuid(
    client,
    admin_headers,
):

    response = client.get(
        "/api/v1/organizations/not-a-uuid",
        headers=admin_headers,
    )

    assert response.status_code == 422