import uuid


def assert_status(response, expected):
    if response.status_code != expected:
        print("\nSTATUS:", response.status_code)
        print("BODY:", response.text)

    assert response.status_code == expected


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

    assert_status(response, 201)

    return response.json()


def create_test_project(client, headers, organization_id):
    unique = uuid.uuid4().hex[:8]

    response = client.post(
        f"/api/v1/organizations/{organization_id}/projects",
        json={
            "name": f"Project {unique}",
            "slug": f"project-{unique}",
        },
        headers=headers,
    )

    assert_status(response, 201)

    return response.json()


def add_project_member(
    client,
    headers,
    organization_id,
    project_id,
    user_id,
):
    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization_id}/projects/"
            f"{project_id}/members"
        ),
        json={
            "user_id": str(user_id),
            "role": "owner",
        },
        headers=headers,
    )

    assert_status(response, 201)


def create_test_task(
    client,
    headers,
    organization_id,
    project_id,
):
    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization_id}/projects/"
            f"{project_id}/tasks"
        ),
        json={
            "title": "Test Task",
        },
        headers=headers,
    )

    assert_status(response, 201)

    return response.json()


def create_attachment(
    client,
    headers,
    organization_id,
    project_id,
    task_id,
):
    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization_id}/projects/"
            f"{project_id}/tasks/"
            f"{task_id}/attachments"
        ),
        json={
            "file_name": "test.pdf",
            "file_path": "/uploads/test.pdf",
            "file_type": "application/pdf",
            "file_size": 1024,
        },
        headers=headers,
    )

    assert_status(response, 201)

    return response.json()


def setup_task(
    client,
    admin_headers,
    admin_user_id,
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

    add_project_member(
        client,
        admin_headers,
        organization["id"],
        project["id"],
        admin_user_id,
    )

    task = create_test_task(
        client,
        admin_headers,
        organization["id"],
        project["id"],
    )

    return organization, project, task


def test_create_task_attachment(
    client,
    admin_headers,
    admin_user_id,
):

    organization, project, task = setup_task(
        client,
        admin_headers,
        admin_user_id,
    )

    attachment = create_attachment(
        client,
        admin_headers,
        organization["id"],
        project["id"],
        task["id"],
    )

    assert attachment["file_name"] == "test.pdf"
    assert attachment["task_id"] == task["id"]


def test_list_task_attachments(
    client,
    admin_headers,
    admin_user_id,
):

    organization, project, task = setup_task(
        client,
        admin_headers,
        admin_user_id,
    )

    create_attachment(
        client,
        admin_headers,
        organization["id"],
        project["id"],
        task["id"],
    )

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/tasks/"
            f"{task['id']}/attachments"
        ),
        headers=admin_headers,
    )

    assert_status(response, 200)

    data = response.json()

    assert data["total"] == 1


def test_get_task_attachment(
    client,
    admin_headers,
    admin_user_id,
):

    organization, project, task = setup_task(
        client,
        admin_headers,
        admin_user_id,
    )

    attachment = create_attachment(
        client,
        admin_headers,
        organization["id"],
        project["id"],
        task["id"],
    )

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/tasks/"
            f"{task['id']}/attachments/"
            f"{attachment['id']}"
        ),
        headers=admin_headers,
    )

    assert_status(response, 200)

    assert response.json()["id"] == attachment["id"]


def test_delete_task_attachment(
    client,
    admin_headers,
    admin_user_id,
):

    organization, project, task = setup_task(
        client,
        admin_headers,
        admin_user_id,
    )

    attachment = create_attachment(
        client,
        admin_headers,
        organization["id"],
        project["id"],
        task["id"],
    )

    response = client.delete(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/tasks/"
            f"{task['id']}/attachments/"
            f"{attachment['id']}"
        ),
        headers=admin_headers,
    )

    assert_status(response, 200)