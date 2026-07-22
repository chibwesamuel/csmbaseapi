import uuid


def test_create_organization(client, authenticated_headers):

    unique = uuid.uuid4().hex[:8]

    payload = {
        "name": f"Organization {unique}",
        "slug": f"organization-{unique}",
        "description": "Test organization",
    }

    response = client.post(
        "/organizations/",
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
        "/organizations/",
        json=payload,
        headers=authenticated_headers,
    )

    response = client.post(
        "/organizations/",
        json=payload,
        headers=authenticated_headers,
    )

    assert response.status_code == 409


def test_list_organizations(client, admin_headers):

    response = client.get(
        "/organizations/",
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
        "/organizations/",
        json=payload,
        headers=authenticated_headers,
    )

    assert create.status_code == 201

    response = client.get(
        "/organizations/my",
        headers=authenticated_headers,
    )

    assert response.status_code == 200

    organizations = response.json()

    assert isinstance(organizations, list)

    assert any(
        org["slug"] == payload["slug"]
        for org in organizations
    )