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