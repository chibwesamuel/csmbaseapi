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


def create_test_project(
    client,
    headers,
    organization_id,
):
    """
    Helper to create a project.
    """

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


def test_create_task(
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

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/tasks"
        ),
        json={
            "title": "Setup database",
            "description": "Create initial schema",
            "status": "todo",
            "priority": "high",
        },
        headers=admin_headers,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Setup database"
    assert data["project_id"] == project["id"]


def test_duplicate_task_title(
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

    payload = {
        "title": "Duplicate Task",
    }

    first = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/tasks"
        ),
        json=payload,
        headers=admin_headers,
    )

    assert first.status_code == 201

    second = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/tasks"
        ),
        json=payload,
        headers=admin_headers,
    )

    assert second.status_code == 400


def test_list_tasks(
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
            f"{project['id']}/tasks"
        ),
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert "tasks" in data
    assert "total" in data


def test_get_task(
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

    created = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/tasks"
        ),
        json={
            "title": "Frontend Work",
        },
        headers=admin_headers,
    )

    task = created.json()

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/tasks/"
            f"{task['id']}"
        ),
        headers=admin_headers,
    )

    assert response.status_code == 200

    assert response.json()["id"] == task["id"]


def test_get_missing_task(
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
            f"{project['id']}/tasks/"
            f"{uuid.uuid4()}"
        ),
        headers=admin_headers,
    )

    assert response.status_code == 404


def test_update_task(
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

    created = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/tasks"
        ),
        json={
            "title": "Old Task",
        },
        headers=admin_headers,
    )

    task = created.json()

    response = client.patch(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/tasks/"
            f"{task['id']}"
        ),
        json={
            "title": "New Task",
            "status": "in_progress",
        },
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "New Task"
    assert data["status"] == "in_progress"


def test_delete_task(
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

    created = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/tasks"
        ),
        json={
            "title": "Delete Me",
        },
        headers=admin_headers,
    )

    task = created.json()

    response = client.delete(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/tasks/"
            f"{task['id']}"
        ),
        headers=admin_headers,
    )

    assert response.status_code == 200

    assert response.json()["message"] == (
        "Task deleted successfully"
    )


def test_normal_user_cannot_create_task(
    client,
    admin_headers,
    authenticated_headers,
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

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/tasks"
        ),
        json={
            "title": "Unauthorized Task",
        },
        headers=authenticated_headers,
    )

    assert response.status_code == 403

def test_filter_tasks_by_status(
    client,
    admin_headers,
):
    """
    Test filtering tasks by status.
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

    client.post(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/tasks"
        ),
        json={
            "title": "Completed Task",
            "status": "completed",
        },
        headers=admin_headers,
    )

    client.post(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/tasks"
        ),
        json={
            "title": "Pending Task",
            "status": "todo",
        },
        headers=admin_headers,
    )

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/tasks"
        ),
        params={
            "status": "completed",
        },
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["tasks"][0]["title"] == "Completed Task"


def test_filter_tasks_by_priority(
    client,
    admin_headers,
):
    """
    Test filtering tasks by priority.
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

    client.post(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/tasks"
        ),
        json={
            "title": "High Priority Task",
            "priority": "high",
        },
        headers=admin_headers,
    )

    client.post(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/tasks"
        ),
        json={
            "title": "Low Priority Task",
            "priority": "low",
        },
        headers=admin_headers,
    )

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/tasks"
        ),
        params={
            "priority": "high",
        },
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["tasks"][0]["title"] == "High Priority Task"


def test_filter_tasks_by_assignee(
    client,
    admin_headers,
):
    """
    Test filtering tasks by assigned user.
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

    # Get current admin user
    user_response = client.get(
        "/api/v1/users/me",
        headers=admin_headers,
    )

    assert user_response.status_code == 200

    user = user_response.json()

    # Add user as project member first
    member_response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/members"
        ),
        json={
            "user_id": user["id"],
        },
        headers=admin_headers,
    )

    assert member_response.status_code in [200, 201]

    # Create an unassigned task
    unassigned_response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/tasks"
        ),
        json={
            "title": "Unassigned Task",
        },
        headers=admin_headers,
    )

    assert unassigned_response.status_code == 201

    # Create an assigned task
    assigned_response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/tasks"
        ),
        json={
            "title": "Assigned Task",
            "assigned_to": user["id"],
        },
        headers=admin_headers,
    )

    assert assigned_response.status_code == 201

    assigned_task = assigned_response.json()

    assert assigned_task["assigned_to"] == user["id"]

    # Filter tasks by assignee
    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/tasks"
        ),
        params={
            "assigned_to": user["id"],
        },
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["tasks"][0]["title"] == "Assigned Task"

def test_task_pagination(
    client,
    admin_headers,
):
    """
    Test task pagination using skip and limit.
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

    # Create 5 tasks
    for index in range(5):
        response = client.post(
            (
                f"/api/v1/organizations/"
                f"{organization['id']}/projects/"
                f"{project['id']}/tasks"
            ),
            json={
                "title": f"Task {index}",
            },
            headers=admin_headers,
        )

        assert response.status_code == 201

    # Request first 2 tasks
    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/tasks"
        ),
        params={
            "skip": 0,
            "limit": 2,
        },
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 5
    assert len(data["tasks"]) == 2


def test_task_pagination_skip(
    client,
    admin_headers,
):
    """
    Test skipping tasks.
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

    titles = []

    for index in range(5):

        title = f"Task {index}"
        titles.append(title)

        response = client.post(
            (
                f"/api/v1/organizations/"
                f"{organization['id']}/projects/"
                f"{project['id']}/tasks"
            ),
            json={
                "title": title,
            },
            headers=admin_headers,
        )

        assert response.status_code == 201


    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/tasks"
        ),
        params={
            "skip": 2,
            "limit": 10,
        },
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 5
    assert len(data["tasks"]) == 3

def test_user_cannot_access_other_project_tasks(
    client,
    admin_headers,
    authenticated_headers,
):
    """
    Users should not access tasks from projects they don't belong to.
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

    task_response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/tasks"
        ),
        json={
            "title": "Private Task",
        },
        headers=admin_headers,
    )

    assert task_response.status_code == 201

    task = task_response.json()

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/tasks/"
            f"{task['id']}"
        ),
        headers=authenticated_headers,
    )

    assert response.status_code == 403

def test_create_task_with_non_member_assignee(
    client,
    admin_headers,
):
    """
    Cannot assign a task to someone who is not a project member.
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

    user_response = client.get(
        "/api/v1/users/me",
        headers=admin_headers,
    )

    assert user_response.status_code == 200

    user = user_response.json()

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/tasks"
        ),
        json={
            "title": "Invalid Assignment",
            "assigned_to": user["id"],
        },
        headers=admin_headers,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Assigned user is not a project member"
    )

def test_create_task_with_invalid_assignee(
    client,
    admin_headers,
):
    """
    Cannot assign a task to a user that does not exist.
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

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/tasks"
        ),
        json={
            "title": "Invalid User Task",
            "assigned_to": str(uuid.uuid4()),
        },
        headers=admin_headers,
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Assigned user not found"
    )

def test_update_task_duplicate_title(
    client,
    admin_headers,
):
    """
    Cannot update a task to an existing title.
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

    first = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/tasks"
        ),
        json={
            "title": "First Task",
        },
        headers=admin_headers,
    )

    second = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/tasks"
        ),
        json={
            "title": "Second Task",
        },
        headers=admin_headers,
    )

    first_task = first.json()
    second_task = second.json()

    response = client.patch(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/tasks/"
            f"{second_task['id']}"
        ),
        json={
            "title": first_task["title"],
        },
        headers=admin_headers,
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "A task with this title already exists"
    )

def test_update_missing_task(
    client,
    admin_headers,
):
    """
    Updating a non-existing task should return 404.
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

    response = client.patch(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/tasks/"
            f"{uuid.uuid4()}"
        ),
        json={
            "title": "Does Not Exist",
        },
        headers=admin_headers,
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Task not found"
    )