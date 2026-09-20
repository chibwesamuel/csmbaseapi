import uuid

from app.models.organization_member import OrganizationMember
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User


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


def create_project_permission_user(
    client,
    db,
    organization_id,
    permission_name,
):
    """
    Create an active, verified organization member with
    exactly the requested project permission.
    """

    unique = uuid.uuid4().hex[:8]
    password = "Password123!"

    payload = {
        "email": f"project_test_{unique}@example.com",
        "username": f"project_test_{unique}",
        "password": password,
        "first_name": "Project",
        "last_name": "Tester",
    }

    response = client.post(
        "/api/v1/auth/register",
        json=payload,
    )

    assert response.status_code == 201

    user_data = response.json()

    user = (
        db.query(User)
        .filter(
            User.id == user_data["id"]
        )
        .first()
    )

    assert user is not None

    user.is_active = True
    user.is_verified = True

    permission = (
        db.query(Permission)
        .filter(
            Permission.name == permission_name
        )
        .first()
    )

    assert permission is not None

    role = Role(
        name=f"Project Tester {unique}",
        description="Project authorization test role",
    )

    role.permissions.append(permission)

    db.add(role)
    db.commit()
    db.refresh(role)

    user.roles.append(role)
    db.commit()
    db.refresh(user)

    organization_role = (
        db.query(Role)
        .filter(
            Role.name == "member"
        )
        .first()
    )

    assert organization_role is not None

    membership = OrganizationMember(
        organization_id=organization_id,
        user_id=user.id,
        role_id=organization_role.id,
    )

    db.add(membership)
    db.commit()

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": payload["email"],
            "password": password,
        },
    )

    assert login_response.status_code == 200

    return {
        "user": user,
        "headers": {
            "Authorization": (
                f"Bearer "
                f"{login_response.json()['access_token']}"
            )
        },
    }


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


def test_project_list_requires_view_permission(
    client,
    db,
    admin_headers,
):
    """
    Listing projects requires projects.view.
    """

    organization = create_test_organization(
        client,
        admin_headers,
    )

    tester = create_project_permission_user(
        client,
        db,
        organization["id"],
        "projects.create",
    )

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects"
        ),
        headers=tester["headers"],
    )

    assert response.status_code == 403

    assert response.json()["message"] == (
        "Permission 'projects.view' required"
    )


def test_project_get_requires_view_permission(
    client,
    db,
    admin_headers,
):
    """
    Retrieving a project requires projects.view.
    """

    organization = create_test_organization(
        client,
        admin_headers,
    )

    project_response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects"
        ),
        json={
            "name": "Protected Project",
            "slug": "protected-project",
        },
        headers=admin_headers,
    )

    assert project_response.status_code == 201

    project = project_response.json()

    tester = create_project_permission_user(
        client,
        db,
        organization["id"],
        "projects.create",
    )

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}"
        ),
        headers=tester["headers"],
    )

    assert response.status_code == 403

    assert response.json()["message"] == (
        "Permission 'projects.view' required"
    )


def test_project_update_requires_update_permission(
    client,
    db,
    admin_headers,
):
    """
    Updating a project requires projects.update.
    """

    organization = create_test_organization(
        client,
        admin_headers,
    )

    project_response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects"
        ),
        json={
            "name": "Protected Project",
            "slug": "protected-project",
        },
        headers=admin_headers,
    )

    assert project_response.status_code == 201

    project = project_response.json()

    tester = create_project_permission_user(
        client,
        db,
        organization["id"],
        "projects.view",
    )

    response = client.patch(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}"
        ),
        json={
            "name": "Unauthorized Update",
        },
        headers=tester["headers"],
    )

    assert response.status_code == 403

    assert response.json()["message"] == (
        "Permission 'projects.update' required"
    )


def test_project_delete_requires_delete_permission(
    client,
    db,
    admin_headers,
):
    """
    Deleting a project requires projects.delete.
    """

    organization = create_test_organization(
        client,
        admin_headers,
    )

    project_response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects"
        ),
        json={
            "name": "Protected Project",
            "slug": "protected-project",
        },
        headers=admin_headers,
    )

    assert project_response.status_code == 201

    project = project_response.json()

    tester = create_project_permission_user(
        client,
        db,
        organization["id"],
        "projects.view",
    )

    response = client.delete(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}"
        ),
        headers=tester["headers"],
    )

    assert response.status_code == 403

    assert response.json()["message"] == (
        "Permission 'projects.delete' required"
    )


def test_project_update_rejects_project_from_another_organization(
    client,
    admin_headers,
):
    """
    A project belonging to another organization must not be
    accessible through the requested organization.
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

    response = client.patch(
        (
            f"/api/v1/organizations/"
            f"{organization_two['id']}/projects/"
            f"{project['id']}"
        ),
        json={
            "name": "Unauthorized Cross-Tenant Update",
        },
        headers=admin_headers,
    )

    assert response.status_code == 404

    assert response.json()["message"] == (
        "Project not found"
    )


def test_project_delete_rejects_project_from_another_organization(
    client,
    admin_headers,
):
    """
    A project belonging to another organization must not be
    deleted through another organization's endpoint.
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

    response = client.delete(
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

    # Confirm the project still exists under its real organization.
    verify_response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization_one['id']}/projects/"
            f"{project['id']}"
        ),
        headers=admin_headers,
    )

    assert verify_response.status_code == 200


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

def test_update_project_slug(
    client,
    admin_headers,
):

    organization = create_test_organization(
        client,
        admin_headers,
    )

    created = client.post(
        f"/api/v1/organizations/{organization['id']}/projects",
        json={
            "name": "Slug Project",
            "slug": "old-slug",
        },
        headers=admin_headers,
    )

    assert created.status_code == 201

    project = created.json()

    response = client.patch(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}"
        ),
        json={
            "slug": "new-slug",
        },
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["slug"] == "new-slug"


def test_update_project_duplicate_slug(
    client,
    admin_headers,
):

    organization = create_test_organization(
        client,
        admin_headers,
    )

    first = client.post(
        f"/api/v1/organizations/{organization['id']}/projects",
        json={
            "name": "First Project",
            "slug": "first-project",
        },
        headers=admin_headers,
    )

    assert first.status_code == 201

    second = client.post(
        f"/api/v1/organizations/{organization['id']}/projects",
        json={
            "name": "Second Project",
            "slug": "second-project",
        },
        headers=admin_headers,
    )

    assert second.status_code == 201

    project = second.json()

    response = client.patch(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}"
        ),
        json={
            "slug": "first-project",
        },
        headers=admin_headers,
    )

    assert response.status_code == 400


def test_project_invalid_pagination(
    client,
    admin_headers,
):

    organization = create_test_organization(
        client,
        admin_headers,
    )

    negative_skip = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects"
            "?skip=-1"
        ),
        headers=admin_headers,
    )

    assert negative_skip.status_code == 422

    zero_limit = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects"
            "?limit=0"
        ),
        headers=admin_headers,
    )

    assert zero_limit.status_code == 422

    excessive_limit = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects"
            "?limit=101"
        ),
        headers=admin_headers,
    )

    assert excessive_limit.status_code == 422
