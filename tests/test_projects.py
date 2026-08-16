import uuid


def create_test_organization(client, headers):
    """
    Helper to create an organization.
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


def test_create_project(client, admin_headers):

    organization = create_test_organization(
        client,
        admin_headers,
    )

    response = client.post(
        f"/api/v1/organizations/{organization['id']}/projects",
        json={
            "name": "Test Project",
            "slug": "test-project",
            "description": "Project description",
        },
        headers=admin_headers,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Test Project"
    assert data["slug"] == "test-project"
    assert data["organization_id"] == organization["id"]


def test_duplicate_project_slug(client, admin_headers):

    organization = create_test_organization(
        client,
        admin_headers,
    )

    payload = {
        "name": "Project One",
        "slug": "project-one",
    }

    first = client.post(
        f"/api/v1/organizations/{organization['id']}/projects",
        json=payload,
        headers=admin_headers,
    )

    assert first.status_code == 201

    second = client.post(
        f"/api/v1/organizations/{organization['id']}/projects",
        json=payload,
        headers=admin_headers,
    )

    assert second.status_code == 400


def test_list_projects(client, admin_headers):

    organization = create_test_organization(
        client,
        admin_headers,
    )

    response = client.get(
        f"/api/v1/organizations/{organization['id']}/projects",
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert "projects" in data
    assert "total" in data


def test_get_project(client, admin_headers):

    organization = create_test_organization(
        client,
        admin_headers,
    )

    created = client.post(
        f"/api/v1/organizations/{organization['id']}/projects",
        json={
            "name": "Website",
            "slug": "website",
        },
        headers=admin_headers,
    )

    project = created.json()

    response = client.get(
        f"/api/v1/organizations/{organization['id']}/projects/{project['id']}",
        headers=admin_headers,
    )

    assert response.status_code == 200

    assert response.json()["id"] == project["id"]


def test_get_missing_project(client, admin_headers):

    organization = create_test_organization(
        client,
        admin_headers,
    )

    response = client.get(
        f"/api/v1/organizations/{organization['id']}/projects/{uuid.uuid4()}",
        headers=admin_headers,
    )

    assert response.status_code == 404


def test_update_project(client, admin_headers):

    organization = create_test_organization(
        client,
        admin_headers,
    )

    created = client.post(
        f"/api/v1/organizations/{organization['id']}/projects",
        json={
            "name": "Old Name",
            "slug": "old-name",
        },
        headers=admin_headers,
    )

    project = created.json()

    response = client.patch(
        f"/api/v1/organizations/{organization['id']}/projects/{project['id']}",
        json={
            "name": "New Name",
        },
        headers=admin_headers,
    )

    assert response.status_code == 200

    assert response.json()["name"] == "New Name"


def test_delete_project(client, admin_headers):

    organization = create_test_organization(
        client,
        admin_headers,
    )

    created = client.post(
        f"/api/v1/organizations/{organization['id']}/projects",
        json={
            "name": "Delete Me",
            "slug": "delete-me",
        },
        headers=admin_headers,
    )

    project = created.json()

    response = client.delete(
        f"/api/v1/organizations/{organization['id']}/projects/{project['id']}",
        headers=admin_headers,
    )

    assert response.status_code == 200

    assert response.json()["message"] == (
        "Project deleted successfully"
    )


def test_normal_user_cannot_create_project(
    client,
    authenticated_headers,
):

    organization = create_test_organization(
        client,
        authenticated_headers,
    )

    response = client.post(
        f"/api/v1/organizations/{organization['id']}/projects",
        json={
            "name": "Unauthorized Project",
            "slug": "unauthorized",
        },
        headers=authenticated_headers,
    )

    assert response.status_code == 403

def test_project_rejects_missing_organization(
    client,
    admin_headers,
):
    """
    A non-existent organization must return 404.
    """

    response = client.get(
        f"/api/v1/organizations/{uuid.uuid4()}/projects",
        headers=admin_headers,
    )

    assert response.status_code == 404

    assert response.json()["message"] == (
        "Organization not found"
    )


def test_project_rejects_project_from_another_organization(
    client,
    admin_headers,
):
    """
    A project belonging to another organization must
    not be accessible through the requested organization.
    """

    organization_one = create_test_organization(
        client,
        admin_headers,
    )

    organization_two = create_test_organization(
        client,
        admin_headers,
    )

    project_response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization_one['id']}/projects"
        ),
        json={
            "name": "Organization One Project",
            "slug": "organization-one-project",
        },
        headers=admin_headers,
    )

    assert project_response.status_code == 201

    project = project_response.json()

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization_two['id']}/projects/"
            f"{project['id']}"
        ),
        headers=admin_headers,
    )

    assert response.status_code == 404

    assert response.json()["message"] == (
        "Project not found"
    )

def test_get_missing_project(
    client,
    admin_headers,
):
    """
    A non-existent project must return 404.
    """

    organization = create_test_organization(
        client,
        admin_headers,
    )

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{uuid.uuid4()}"
        ),
        headers=admin_headers,
    )

    assert response.status_code == 404

    assert response.json()["message"] == (
        "Project not found"
    )