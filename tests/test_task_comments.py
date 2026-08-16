import uuid

from app.models.user import User
from app.models.role import Role
from app.models.organization_member import OrganizationMember

from app.repositories.user_role import assign_role_to_user
from app.models.permission import Permission


def assert_status(response, expected):
    """
    Assert response status and print API errors when failing.
    """

    if response.status_code != expected:
        print("\nSTATUS CODE:", response.status_code)
        print("RESPONSE BODY:", response.text)

    assert response.status_code == expected

def assert_status(response, expected):
    """
    Assert response status and print API errors when failing.
    """

    if response.status_code != expected:
        print("\nSTATUS CODE:", response.status_code)
        print("RESPONSE BODY:", response.text)

    assert response.status_code == expected


def assign_task_permissions(
    db,
    user_id,
):
    """
    Give a test user the task permissions required to
    reach the comment ownership checks without granting
    system administrator privileges.
    """

    user = (
        db.query(User)
        .filter(
            User.id == user_id
        )
        .first()
    )

    assert user is not None

    permissions = (
        db.query(Permission)
        .filter(
            Permission.name.in_(
                [
                    "tasks.view",
                    "tasks.update",
                    "tasks.delete",
                ]
            )
        )
        .all()
    )

    assert len(permissions) == 3

    role = Role(
        name=f"Task Comment Tester {uuid.uuid4().hex[:8]}",
        description="Role for task comment tests",
    )

    db.add(role)
    db.flush()

    for permission in permissions:
        role.permissions.append(permission)

    db.commit()
    db.refresh(role)

    assign_role_to_user(
        db,
        user,
        role,
    )

    db.refresh(user)

    return user

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
            "title": f"Test Task {uuid.uuid4().hex[:8]}",
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

def test_task_comments_reject_missing_task(
    client,
    admin_headers,
):
    """
    A non-existent task must return 404.
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

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/tasks/"
            f"{uuid.uuid4()}/comments"
        ),
        headers=admin_headers,
    )

    assert_status(response, 404)

    assert response.json()["message"] == (
        "Task not found"
    )


def test_task_comments_reject_project_mismatch(
    client,
    admin_headers,
    admin_user,
):
    """
    A task belonging to another project must not be
    accessible through the requested project.
    """

    organization = create_test_organization(
        client,
        admin_headers,
    )

    project_one = create_test_project(
        client,
        admin_headers,
        organization["id"],
    )

    project_two = create_test_project(
        client,
        admin_headers,
        organization["id"],
    )

    add_admin_to_project(
        client,
        admin_headers,
        organization["id"],
        project_one["id"],
        admin_user,
    )

    task = create_test_task(
        client,
        admin_headers,
        organization["id"],
        project_one["id"],
    )

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project_two['id']}/tasks/"
            f"{task['id']}/comments"
        ),
        headers=admin_headers,
    )

    assert_status(response, 404)

    assert response.json()["message"] == (
        "Task not found"
    )


def test_task_comments_reject_organization_mismatch(
    client,
    admin_headers,
    admin_user,
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

    add_admin_to_project(
        client,
        admin_headers,
        organization_one["id"],
        project["id"],
        admin_user,
    )

    task = create_test_task(
        client,
        admin_headers,
        organization_one["id"],
        project["id"],
    )

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization_two['id']}/projects/"
            f"{project['id']}/tasks/"
            f"{task['id']}/comments"
        ),
        headers=admin_headers,
    )

    assert_status(response, 404)

    assert response.json()["message"] == (
        "Project not found"
    )


def test_non_project_member_cannot_create_comment(
    client,
    admin_headers,
):
    """
    A user who is not a project member cannot
    create a comment.
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

    task = create_test_task(
        client,
        admin_headers,
        organization["id"],
        project["id"],
    )

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/tasks/"
            f"{task['id']}/comments"
        ),
        json={
            "content": "Unauthorized comment",
        },
        headers=admin_headers,
    )

    assert_status(response, 400)

    assert response.json()["message"] == (
        "User is not a project member"
    )


def test_user_cannot_update_another_users_comment(
    client,
    admin_headers,
    admin_user,
    db,
):
    """
    A user cannot update another user's comment.
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
        "Original comment",
    )

    # ---------------------------------------------------------
    # Create another user.
    # ---------------------------------------------------------

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": (
                f"other{uuid.uuid4().hex[:8]}"
                "@example.com"
            ),
            "username": (
                f"other{uuid.uuid4().hex[:8]}"
            ),
            "password": "password123",
            "first_name": "Other",
            "last_name": "User",
        },
    )

    assert_status(response, 201)

    other_user = response.json()

    # ---------------------------------------------------------
    # Give the user the task permissions required to reach
    # the comment ownership check.
    # ---------------------------------------------------------

    assign_task_permissions(
        db,
        other_user["id"],
    )

    # ---------------------------------------------------------
    # Retrieve the user from the database and make sure the
    # account is active and verified.
    # ---------------------------------------------------------

    other_user_model = (
        db.query(User)
        .filter(
            User.id == other_user["id"]
        )
        .first()
    )

    assert other_user_model is not None

    other_user_model.is_active = True
    other_user_model.is_verified = True

    db.commit()
    db.refresh(other_user_model)

    # ---------------------------------------------------------
    # Retrieve the Admin organization role.
    #
    # The user needs an organization membership because
    # get_current_organization() checks organization_members
    # before the request can reach the comment service.
    # ---------------------------------------------------------

    organization_role = (
        db.query(Role)
        .filter(
            Role.name == "Admin"
        )
        .first()
    )

    assert organization_role is not None

    # ---------------------------------------------------------
    # Make the user a member of the organization.
    # ---------------------------------------------------------

    organization_member = OrganizationMember(
        organization_id=organization["id"],
        user_id=other_user["id"],
        role_id=organization_role.id,
    )

    db.add(organization_member)
    db.commit()
    db.refresh(organization_member)

    # Confirm the organization membership was created.
    organization_member_check = (
        db.query(OrganizationMember)
        .filter(
            OrganizationMember.organization_id
            == organization["id"],
            OrganizationMember.user_id
            == other_user["id"],
        )
        .first()
    )

    assert organization_member_check is not None

    # ---------------------------------------------------------
    # Make the user a member of the project.
    # ---------------------------------------------------------

    member_response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/members"
        ),
        json={
            "user_id": other_user["id"],
            "role": "contributor",
        },
        headers=admin_headers,
    )

    assert_status(member_response, 201)

    # ---------------------------------------------------------
    # Login as the other user.
    # ---------------------------------------------------------

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": other_user["email"],
            "password": "password123",
        },
    )

    assert_status(login_response, 200)

    other_headers = {
        "Authorization": (
            f"Bearer {login_response.json()['access_token']}"
        )
    }

    # ---------------------------------------------------------
    # Attempt to modify somebody else's comment.
    # ---------------------------------------------------------

    response = client.patch(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/tasks/"
            f"{task['id']}/comments/"
            f"{comment['id']}"
        ),
        json={
            "content": "Attempted unauthorized update",
        },
        headers=other_headers,
    )

    assert_status(response, 400)

    assert response.json()["message"] == (
        "You can only update your own comments"
    )


def test_user_cannot_delete_another_users_comment(
    client,
    admin_headers,
    admin_user,
    db,
):
    """
    A user cannot delete another user's comment.
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
        "Protected comment",
    )

    # Create another user.
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": (
                f"other{uuid.uuid4().hex[:8]}"
                "@example.com"
            ),
            "username": (
                f"other{uuid.uuid4().hex[:8]}"
            ),
            "password": "password123",
            "first_name": "Other",
            "last_name": "User",
        },
    )

    assert_status(response, 201)

    other_user = response.json()

    # Give the user the task permissions required to reach
    # the comment ownership check.
    assign_task_permissions(
        db,
        other_user["id"],
    )

    # Ensure the user is active and verified.
    other_user_model = (
        db.query(User)
        .filter(
            User.id == other_user["id"]
        )
        .first()
    )

    assert other_user_model is not None

    other_user_model.is_active = True
    other_user_model.is_verified = True

    db.commit()
    db.refresh(other_user_model)

    # Ensure the user belongs to the organization.
    organization_role = (
        db.query(Role)
        .filter(
            Role.name == "Admin"
        )
        .first()
    )

    assert organization_role is not None

    organization_member = OrganizationMember(
        organization_id=organization["id"],
        user_id=other_user["id"],
        role_id=organization_role.id,
    )

    db.add(organization_member)
    db.commit()
    db.refresh(organization_member)

    # Make the user a member of the project.
    member_response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/members"
        ),
        json={
            "user_id": other_user["id"],
            "role": "contributor",
        },
        headers=admin_headers,
    )

    assert_status(member_response, 201)

    # Login as the other user.
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": other_user["email"],
            "password": "password123",
        },
    )

    assert_status(login_response, 200)

    other_headers = {
        "Authorization": (
            f"Bearer {login_response.json()['access_token']}"
        )
    }

    # Attempt to delete somebody else's comment.
    response = client.delete(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/tasks/"
            f"{task['id']}/comments/"
            f"{comment['id']}"
        ),
        headers=other_headers,
    )

    assert_status(response, 400)

    assert response.json()["message"] == (
        "You can only delete your own comments"
    )


def test_comment_cannot_be_accessed_through_another_task(
    client,
    admin_headers,
    admin_user,
):
    """
    A comment belonging to one task must not be accessible
    through another task.
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

    add_admin_to_project(
        client,
        admin_headers,
        organization["id"],
        project["id"],
        admin_user,
    )

    task_one = create_test_task(
        client,
        admin_headers,
        organization["id"],
        project["id"],
    )

    task_two = create_test_task(
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
        task_one["id"],
        "Task one comment",
    )

    response = client.patch(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/tasks/"
            f"{task_two['id']}/comments/"
            f"{comment['id']}"
        ),
        json={
            "content": "Should not update",
        },
        headers=admin_headers,
    )

    assert_status(response, 404)

    assert response.json()["message"] == (
        "Comment not found"
    )