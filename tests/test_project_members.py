import uuid

from app.models.organization_member import OrganizationMember
from app.models.role import Role


def create_test_organization(client, headers):
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


def create_test_project(
    client,
    headers,
    organization_id,
):
    unique = uuid.uuid4().hex[:8]

    response = client.post(
        f"/api/v1/organizations/{organization_id}/projects",
        json={
            "name": f"Project {unique}",
            "slug": f"project-{unique}",
        },
        headers=headers,
    )

    assert response.status_code == 201

    return response.json()


def create_test_user(client):
    unique = uuid.uuid4().hex[:8]

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": f"user{unique}@example.com",
            "username": f"user{unique}",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User",
        },
    )

    assert response.status_code == 201

    return response.json()


def create_test_project_context(
    client,
    admin_headers,
):
    organization = create_test_organization(
        client,
        admin_headers,
    )

    project = create_test_project(
        client,
        admin_headers,
        organization["id"],
    )

    return organization, project


def project_members_url(
    organization_id,
    project_id,
):
    return (
        f"/api/v1/organizations/"
        f"{organization_id}/projects/"
        f"{project_id}/members"
    )


def create_project_member(
    client,
    admin_headers,
    organization_id,
    project_id,
    user_id,
    role="contributor",
):
    url = project_members_url(
        organization_id,
        project_id,
    )

    response = client.post(
        url,
        json={
            "user_id": user_id,
            "role": role,
        },
        headers=admin_headers,
    )

    assert response.status_code == 201

    return response.json()


def add_user_to_organization(
    db,
    organization_id,
    user_id,
):
    organization_role = (
        db.query(Role)
        .filter(
            Role.name == "Admin"
        )
        .first()
    )

    assert organization_role is not None

    organization_member = OrganizationMember(
        organization_id=organization_id,
        user_id=user_id,
        role_id=organization_role.id,
    )

    db.add(organization_member)
    db.commit()
    db.refresh(organization_member)

    return organization_member


def test_add_project_member(
    client,
    admin_headers,
    db,
):
    organization, project = create_test_project_context(
        client,
        admin_headers,
    )

    user = create_test_user(client)

    add_user_to_organization(
        db,
        organization["id"],
        user["id"],
    )

    data = create_project_member(
        client,
        admin_headers,
        organization["id"],
        project["id"],
        user["id"],
    )

    assert data["project_id"] == project["id"]
    assert data["user_id"] == user["id"]
    assert data["role"] == "contributor"


def test_cannot_add_user_from_another_organization_to_project(
    client,
    admin_headers,
    db,
):
    """
    A user belonging to another organization must not be
    added to a project in this organization.
    """

    organization_one, project = (
        create_test_project_context(
            client,
            admin_headers,
        )
    )

    organization_two = create_test_organization(
        client,
        admin_headers,
    )

    user = create_test_user(client)

    add_user_to_organization(
        db,
        organization_two["id"],
        user["id"],
    )

    url = project_members_url(
        organization_one["id"],
        project["id"],
    )

    response = client.post(
        url,
        json={
            "user_id": user["id"],
            "role": "contributor",
        },
        headers=admin_headers,
    )

    assert response.status_code == 400

    assert response.json()["message"] == (
        "User does not belong to the project organization"
    )


def test_duplicate_project_member(
    client,
    admin_headers,
    db,
):
    organization, project = create_test_project_context(
        client,
        admin_headers,
    )

    user = create_test_user(client)

    add_user_to_organization(
        db,
        organization["id"],
        user["id"],
    )

    create_project_member(
        client,
        admin_headers,
        organization["id"],
        project["id"],
        user["id"],
    )

    url = project_members_url(
        organization["id"],
        project["id"],
    )

    response = client.post(
        url,
        json={
            "user_id": user["id"],
            "role": "contributor",
        },
        headers=admin_headers,
    )

    assert response.status_code == 400


def test_list_project_members(
    client,
    admin_headers,
    db,
):
    organization, project = create_test_project_context(
        client,
        admin_headers,
    )

    url = project_members_url(
        organization["id"],
        project["id"],
    )

    response = client.get(
        url,
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert "members" in data
    assert "total" in data


def test_get_missing_project_member(
    client,
    admin_headers,
    db,
):
    organization, project = create_test_project_context(
        client,
        admin_headers,
    )

    url = project_members_url(
        organization["id"],
        project["id"],
    )

    response = client.get(
        f"{url}/{uuid.uuid4()}",
        headers=admin_headers,
    )

    assert response.status_code == 404


def test_get_project_member(
    client,
    admin_headers,
    db,
):
    """
    Test retrieving a specific project member.
    """

    organization, project = create_test_project_context(
        client,
        admin_headers,
    )

    user = create_test_user(client)

    add_user_to_organization(
        db,
        organization["id"],
        user["id"],
    )

    create_project_member(
        client,
        admin_headers,
        organization["id"],
        project["id"],
        user["id"],
    )

    url = project_members_url(
        organization["id"],
        project["id"],
    )

    response = client.get(
        f"{url}/{user['id']}",
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["user_id"] == user["id"]
    assert data["role"] == "contributor"


def test_update_project_member_role(
    client,
    admin_headers,
    db,
):
    """
    Test changing a project member role.
    """

    organization, project = create_test_project_context(
        client,
        admin_headers,
    )

    user = create_test_user(client)

    add_user_to_organization(
        db,
        organization["id"],
        user["id"],
    )

    create_project_member(
        client,
        admin_headers,
        organization["id"],
        project["id"],
        user["id"],
    )

    url = project_members_url(
        organization["id"],
        project["id"],
    )

    response = client.patch(
        f"{url}/{user['id']}",
        json={
            "role": "admin",
        },
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["user_id"] == user["id"]
    assert data["role"] == "admin"


def test_remove_project_member(
    client,
    admin_headers,
    db,
):
    """
    Test removing a project member.
    """

    organization, project = create_test_project_context(
        client,
        admin_headers,
    )

    user = create_test_user(client)

    add_user_to_organization(
        db,
        organization["id"],
        user["id"],
    )

    create_project_member(
        client,
        admin_headers,
        organization["id"],
        project["id"],
        user["id"],
    )

    url = project_members_url(
        organization["id"],
        project["id"],
    )

    response = client.delete(
        f"{url}/{user['id']}",
        headers=admin_headers,
    )

    assert response.status_code == 200

    assert response.json()["message"] == (
        "Project member removed successfully"
    )


def test_cannot_remove_last_project_owner(
    client,
    admin_headers,
    db,
):
    """
    Ensure the last project owner cannot be removed.
    """

    organization, project = create_test_project_context(
        client,
        admin_headers,
    )

    # The project creator is automatically assigned
    # as the project owner.
    #
    # admin_headers belong to the project creator,
    # so we need to obtain that user's ID.
    response = client.get(
        "/api/v1/auth/me",
        headers=admin_headers,
    )

    assert response.status_code == 200

    current_user = response.json()

    url = project_members_url(
        organization["id"],
        project["id"],
    )

    response = client.delete(
        f"{url}/{current_user['id']}",
        headers=admin_headers,
    )

    assert response.status_code == 400

    assert "last owner" in response.json()["message"]


def test_project_members_reject_project_from_another_organization(
    client,
    admin_headers,
    db,
):
    """
    A project belonging to another organization must
    not be accessible through the requested organization.
    """

    organization_one, project = (
        create_test_project_context(
            client,
            admin_headers,
        )
    )

    organization_two = create_test_organization(
        client,
        admin_headers,
    )

    url = project_members_url(
        organization_two["id"],
        project["id"],
    )

    response = client.get(
        url,
        headers=admin_headers,
    )

    assert response.status_code == 404

    assert response.json()["message"] == (
        "Project not found"
    )


def test_project_members_reject_missing_project(
    client,
    admin_headers,
    db,
):
    """
    A non-existent project must return 404.
    """

    organization = create_test_organization(
        client,
        admin_headers,
    )

    url = project_members_url(
        organization["id"],
        uuid.uuid4(),
    )

    response = client.get(
        url,
        headers=admin_headers,
    )

    assert response.status_code == 404

    assert response.json()["message"] == (
        "Project not found"
    )


def test_project_creator_is_automatically_project_owner(
    client,
    admin_headers,
    db,
):
    organization, project = create_test_project_context(
        client,
        admin_headers,
    )

    url = project_members_url(
        organization["id"],
        project["id"],
    )

    response = client.get(
        url,
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1

    owner = data["members"][0]

    assert owner["user_id"] == project["created_by"]
    assert owner["role"] == "owner"
