import uuid


def assert_status(response, expected):
    """
    Assert response status and print API errors when failing.
    """

    if response.status_code != expected:
        print("\nSTATUS CODE:", response.status_code)
        print("RESPONSE BODY:", response.text)

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

    assert_status(response, 201)

    return response.json()


def add_admin_to_project(
    client,
    headers,
    organization_id,
    project_id,
    admin_user,
):

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization_id}/projects/"
            f"{project_id}/members"
        ),
        json={
            "user_id": str(admin_user.id),
            "role": "owner",
        },
        headers=headers,
    )

    assert_status(response, 201)

    return response.json()


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


def create_test_comment(
    client,
    headers,
    organization_id,
    project_id,
    task_id,
    content,
):

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization_id}/projects/"
            f"{project_id}/tasks/"
            f"{task_id}/comments"
        ),
        json={
            "content": content,
        },
        headers=headers,
    )

    assert_status(response, 201)

    return response.json()


def test_create_task_comment(
    client,
    admin_headers,
    admin_user,
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

    add_admin_to_project(
        client,
        admin_headers,
        organization["id"],
        project["id"],
        admin_user,
    )

    task = create_test_task(
        client,
        admin_headers,
        organization["id"],
        project["id"],
    )

    comment = create_test_comment(
        client,
        admin_headers,
        organization["id"],
        project["id"],
        task["id"],
        "This is a test comment",
    )

    assert comment["content"] == "This is a test comment"
    assert comment["task_id"] == task["id"]


def test_list_task_comments(
    client,
    admin_headers,
    admin_user,
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

    add_admin_to_project(
        client,
        admin_headers,
        organization["id"],
        project["id"],
        admin_user,
    )

    task = create_test_task(
        client,
        admin_headers,
        organization["id"],
        project["id"],
    )

    create_test_comment(
        client,
        admin_headers,
        organization["id"],
        project["id"],
        task["id"],
        "First comment",
    )

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/tasks/"
            f"{task['id']}/comments"
        ),
        headers=admin_headers,
    )

    assert_status(response, 200)

    data = response.json()

    assert data["total"] == 1
    assert data["comments"][0]["content"] == "First comment"


def test_update_task_comment(
    client,
    admin_headers,
    admin_user,
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

    add_admin_to_project(
        client,
        admin_headers,
        organization["id"],
        project["id"],
        admin_user,
    )

    task = create_test_task(
        client,
        admin_headers,
        organization["id"],
        project["id"],
    )

    comment = create_test_comment(
        client,
        admin_headers,
        organization["id"],
        project["id"],
        task["id"],
        "Old comment",
    )

    response = client.patch(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/tasks/"
            f"{task['id']}/comments/"
            f"{comment['id']}"
        ),
        json={
            "content": "Updated comment",
        },
        headers=admin_headers,
    )

    assert_status(response, 200)

    assert response.json()["content"] == "Updated comment"


def test_delete_task_comment(
    client,
    admin_headers,
    admin_user,
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

    add_admin_to_project(
        client,
        admin_headers,
        organization["id"],
        project["id"],
        admin_user,
    )

    task = create_test_task(
        client,
        admin_headers,
        organization["id"],
        project["id"],
    )

    comment = create_test_comment(
        client,
        admin_headers,
        organization["id"],
        project["id"],
        task["id"],
        "Delete this",
    )

    response = client.delete(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/tasks/"
            f"{task['id']}/comments/"
            f"{comment['id']}"
        ),
        headers=admin_headers,
    )

    assert_status(response, 200)


def test_missing_task_comment(
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

    task = create_test_task(
        client,
        admin_headers,
        organization["id"],
        project["id"],
    )

    response = client.delete(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/tasks/"
            f"{task['id']}/comments/"
            f"{uuid.uuid4()}"
        ),
        headers=admin_headers,
    )

    assert_status(response, 404)