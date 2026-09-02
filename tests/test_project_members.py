import uuid



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



def test_add_project_member(
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

    user = create_test_user(
        client,
    )


    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/members"
        ),
        json={
            "user_id": user["id"],
            "role": "contributor",
        },
        headers=admin_headers,
    )


    assert response.status_code == 201

    data = response.json()

    assert data["project_id"] == project["id"]
    assert data["user_id"] == user["id"]
    assert data["role"] == "contributor"



def test_duplicate_project_member(
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

    user = create_test_user(
        client,
    )


    url = (
        f"/api/v1/organizations/"
        f"{organization['id']}/projects/"
        f"{project['id']}/members"
    )


    payload = {
        "user_id": user["id"],
        "role": "contributor",
    }


    first = client.post(
        url,
        json=payload,
        headers=admin_headers,
    )

    assert first.status_code == 201


    second = client.post(
        url,
        json=payload,
        headers=admin_headers,
    )

    assert second.status_code == 400



def test_list_project_members(
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


    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/members"
        ),
        headers=admin_headers,
    )


    assert response.status_code == 200

    data = response.json()

    assert "members" in data
    assert "total" in data



def test_get_missing_project_member(
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


    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/members/{uuid.uuid4()}"
        ),
        headers=admin_headers,
    )


    assert response.status_code == 404

def test_get_project_member(
    client,
    admin_headers,
):
    """
    Test retrieving a specific project member.
    """

    organization = create_test_organization(
        client,
        admin_headers,
    )

    project = create_test_project(
        client,
        admin_headers,
        organization["id"],
    )

    user = create_test_user(
        client,
    )

    url = (
        f"/api/v1/organizations/"
        f"{organization['id']}/projects/"
        f"{project['id']}/members"
    )

    create_response = client.post(
        url,
        json={
            "user_id": user["id"],
            "role": "contributor",
        },
        headers=admin_headers,
    )

    assert create_response.status_code == 201

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
):
    """
    Test changing a project member role.
    """

    organization = create_test_organization(
        client,
        admin_headers,
    )

    project = create_test_project(
        client,
        admin_headers,
        organization["id"],
    )

    user = create_test_user(
        client,
    )

    url = (
        f"/api/v1/organizations/"
        f"{organization['id']}/projects/"
        f"{project['id']}/members"
    )

    create_response = client.post(
        url,
        json={
            "user_id": user["id"],
            "role": "contributor",
        },
        headers=admin_headers,
    )

    assert create_response.status_code == 201

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
):
    """
    Test removing a project member.
    """

    organization = create_test_organization(
        client,
        admin_headers,
    )

    project = create_test_project(
        client,
        admin_headers,
        organization["id"],
    )

    user = create_test_user(
        client,
    )

    url = (
        f"/api/v1/organizations/"
        f"{organization['id']}/projects/"
        f"{project['id']}/members"
    )

    create_response = client.post(
        url,
        json={
            "user_id": user["id"],
            "role": "contributor",
        },
        headers=admin_headers,
    )

    assert create_response.status_code == 201

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
):
    """
    Ensure the last project owner cannot be removed.
    """

    organization = create_test_organization(
        client,
        admin_headers,
    )

    project = create_test_project(
        client,
        admin_headers,
        organization["id"],
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

    url = (
        f"/api/v1/organizations/"
        f"{organization['id']}/projects/"
        f"{project['id']}/members"
    )

    response = client.delete(
        f"{url}/{current_user['id']}",
        headers=admin_headers,
    )

    assert response.status_code == 400

    assert (
        "last owner"
        in response.json()["message"]
    )

def test_project_members_reject_project_from_another_organization(
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

    project = create_test_project(
        client,
        admin_headers,
        organization_one["id"],
    )

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization_two['id']}/projects/"
            f"{project['id']}/members"
        ),
        headers=admin_headers,
    )

    assert response.status_code == 404

    assert response.json()["message"] == (
        "Project not found"
    )


def test_project_members_reject_missing_project(
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
            f"{uuid.uuid4()}/members"
        ),
        headers=admin_headers,
    )

    assert response.status_code == 404

    assert response.json()["message"] == (
        "Project not found"
    )

def test_project_creator_is_automatically_project_owner(
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

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/members"
        ),
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1

    owner = data["members"][0]

    assert owner["user_id"] == project["created_by"]
    assert owner["role"] == "owner"
