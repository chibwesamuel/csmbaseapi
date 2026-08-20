import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app

from app.database.session import SessionLocal

from app.models.user import User
from app.models.permission import Permission
from app.models.role import Role

from app.repositories.user import get_user_by_email
from app.repositories.user_role import assign_role_to_user
from app.models.organization_member import OrganizationMember

from app.core.security import hash_password

from tests.seed import (
    seed_admin_role,
    seed_organization_roles,
)

from tests.factories import (
    user_payload,
    admin_payload,
)


# ---------------------------------------------------------
# Test Client
# ---------------------------------------------------------

@pytest.fixture(scope="session")
def client():
    return TestClient(app)


# ---------------------------------------------------------
# Database Session
# ---------------------------------------------------------

@pytest.fixture
def db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@pytest.fixture
def db_session(db):
    """
    Alias fixture for tests requiring db_session.
    """

    return db


# ---------------------------------------------------------
# Seed Roles
# ---------------------------------------------------------

@pytest.fixture
def seed_roles(db):
    """
    Ensure all required application roles exist.

    Creates:
    - Admin (system role)
    - owner (organization role)
    - admin (organization role)
    - member (organization role)
    """

    seed_admin_role(db)

    seed_organization_roles(db)


# ---------------------------------------------------------
# Generic User Payload
# ---------------------------------------------------------

@pytest.fixture
def unique_user():

    return user_payload()


# ---------------------------------------------------------
# Register a Normal User
# ---------------------------------------------------------

@pytest.fixture
def registered_user(
    client,
    db,
    unique_user,
):

    response = client.post(
        "/api/v1/auth/register",
        json=unique_user,
    )

    assert response.status_code == 201

    user = get_user_by_email(
        db,
        unique_user["email"],
    )

    assert user is not None

    return user


# ---------------------------------------------------------
# Create Normal User Model
# ---------------------------------------------------------

@pytest.fixture
def normal_user(db):

    username = f"user_{uuid.uuid4().hex[:8]}"

    user = User(
        email=f"{username}@example.com",
        username=username,
        first_name="John",
        last_name="Doe",
        hashed_password=hash_password(
            "Password123!"
        ),
        is_active=True,
        is_verified=False,
        is_superuser=False,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# ---------------------------------------------------------
# Create Inactive User Model
# ---------------------------------------------------------

@pytest.fixture
def inactive_user(db):

    username = f"inactive_{uuid.uuid4().hex[:8]}"

    user = User(
        email=f"{username}@example.com",
        username=username,
        first_name="Inactive",
        last_name="User",
        hashed_password=hash_password(
            "Password123!"
        ),
        is_active=False,
        is_verified=False,
        is_superuser=False,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# ---------------------------------------------------------
# Login as Normal User
# ---------------------------------------------------------

@pytest.fixture
def authenticated_headers(
    client,
    registered_user,
    unique_user,
):

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": registered_user.email,
            "password": unique_user["password"],
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


# ---------------------------------------------------------
# Seed Admin Role
# ---------------------------------------------------------

@pytest.fixture
def admin_role(
    db,
    seed_roles,
):
    """
    Return the seeded system Admin role.
    """

    return (
        db.query(Role)
        .filter(
            Role.name == "Admin"
        )
        .first()
    )


# ---------------------------------------------------------
# Create Admin User
# ---------------------------------------------------------

@pytest.fixture
def admin_user(
    client,
    db,
    admin_role,
):

    password = "AdminPassword123!"

    payload = admin_payload()

    # Ensure known password
    payload["password"] = password

    response = client.post(
        "/api/v1/auth/register",
        json=payload,
    )

    assert response.status_code == 201

    user = get_user_by_email(
        db,
        payload["email"],
    )

    assert user is not None

    assign_role_to_user(
        db,
        user,
        admin_role,
    )

    user.is_superuser = True
    user.is_verified = True
    user.is_active = True

    db.commit()
    db.refresh(user)

    # Test-only helper attribute
    user.test_password = password

    return user


# ---------------------------------------------------------
# Login Admin
# ---------------------------------------------------------

@pytest.fixture
def admin_headers(
    client,
    admin_user,
):

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": admin_user.email,
            "password": admin_user.test_password,
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


# ---------------------------------------------------------
# Seed Permission
# ---------------------------------------------------------

@pytest.fixture
def test_permission(db):

    permission = (
        db.query(Permission)
        .filter(
            Permission.name == "users.view"
        )
        .first()
    )

    if permission is None:

        permission = Permission(
            name="users.view",
            description="View users",
        )

        db.add(permission)
        db.commit()
        db.refresh(permission)

    return permission


# ---------------------------------------------------------
# Create Empty Role
# ---------------------------------------------------------

@pytest.fixture
def test_role(db):

    role = Role(
        name=f"Test Role {uuid.uuid4().hex[:8]}",
        description="Role for testing permissions",
    )

    db.add(role)
    db.commit()
    db.refresh(role)

    return role

@pytest.fixture
def admin_user_id(admin_user):
    return str(admin_user.id)


@pytest.fixture
def notification_user(
    db,
    registered_user,
):
    """
    Assign notification permissions to a normal test user.
    """

    permissions = (
        db.query(Permission)
        .filter(
            Permission.name.in_(
                [
                    "notifications.view",
                    "notifications.update",
                    "notifications.delete",
                ]
            )
        )
        .all()
    )

    role = Role(
        name=f"Notification Tester {uuid.uuid4().hex[:8]}",
        description="Role for notification endpoint tests",
    )

    db.add(role)
    db.flush()

    for permission in permissions:
        role.permissions.append(permission)

    db.commit()
    db.refresh(role)

    assign_role_to_user(
        db,
        registered_user,
        role,
    )

    db.refresh(registered_user)

    return registered_user

@pytest.fixture

def notification_headers(
    client,
    notification_user,
    unique_user,
):
    """
    Login as a user with notification permissions.
    """

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": notification_user.email,
            "password": unique_user["password"],
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }

@pytest.fixture
def organization_context(
    client,
    db,
    authenticated_headers,
    unique_user,
    seed_roles,
):
    """
    Create an organization and users representing
    each organization membership level.

    Returns:
    - organization owner
    - organization admin
    - organization member
    - non-member
    """

    # -----------------------------------------------------
    # Create organization as the authenticated user.
    # This user automatically becomes the owner.
    # -----------------------------------------------------

    unique = uuid.uuid4().hex[:8]

    organization_response = client.post(
        "/api/v1/organizations/",
        json={
            "name": f"Authorization Org {unique}",
            "slug": f"authorization-org-{unique}",
        },
        headers=authenticated_headers,
    )

    assert organization_response.status_code == 201

    organization = organization_response.json()

    owner = get_user_by_email(
        db,
        unique_user["email"],
    )

    assert owner is not None

    # -----------------------------------------------------
    # Get organization roles
    # -----------------------------------------------------

    owner_role = (
        db.query(Role)
        .filter(Role.name == "owner")
        .first()
    )

    admin_role = (
        db.query(Role)
        .filter(Role.name == "admin")
        .first()
    )

    member_role = (
        db.query(Role)
        .filter(Role.name == "member")
        .first()
    )

    assert owner_role is not None
    assert admin_role is not None
    assert member_role is not None

    # -----------------------------------------------------
    # Create organization admin
    # -----------------------------------------------------

    admin_unique = uuid.uuid4().hex[:8]

    admin_payload = {
        "email": f"org_admin_{admin_unique}@example.com",
        "username": f"org_admin_{admin_unique}",
        "password": "Password123!",
        "first_name": "Organization",
        "last_name": "Admin",
    }

    admin_response = client.post(
        "/api/v1/auth/register",
        json=admin_payload,
    )

    assert admin_response.status_code == 201

    organization_admin = get_user_by_email(
        db,
        admin_payload["email"],
    )

    assert organization_admin is not None

    assign_role_to_user(
        db,
        organization_admin,
        admin_role,
    )

    # -----------------------------------------------------
    # Create organization member
    # -----------------------------------------------------

    member_unique = uuid.uuid4().hex[:8]

    member_payload = {
        "email": f"org_member_{member_unique}@example.com",
        "username": f"org_member_{member_unique}",
        "password": "Password123!",
        "first_name": "Organization",
        "last_name": "Member",
    }

    member_response = client.post(
        "/api/v1/auth/register",
        json=member_payload,
    )

    assert member_response.status_code == 201

    organization_member = get_user_by_email(
        db,
        member_payload["email"],
    )

    assert organization_member is not None

    # -----------------------------------------------------
    # Create non-member
    # -----------------------------------------------------

    outsider_unique = uuid.uuid4().hex[:8]

    outsider_payload = {
        "email": f"outsider_{outsider_unique}@example.com",
        "username": f"outsider_{outsider_unique}",
        "password": "Password123!",
        "first_name": "Organization",
        "last_name": "Outsider",
    }

    outsider_response = client.post(
        "/api/v1/auth/register",
        json=outsider_payload,
    )

    assert outsider_response.status_code == 201

    outsider = get_user_by_email(
        db,
        outsider_payload["email"],
    )

    assert outsider is not None

    # -----------------------------------------------------
    # Create admin membership
    # -----------------------------------------------------

    admin_membership = OrganizationMember(
        organization_id=organization["id"],
        user_id=organization_admin.id,
        role_id=admin_role.id,
    )

    db.add(admin_membership)

    # -----------------------------------------------------
    # Create member membership
    # -----------------------------------------------------

    member_membership = OrganizationMember(
        organization_id=organization["id"],
        user_id=organization_member.id,
        role_id=member_role.id,
    )

    db.add(member_membership)

    db.commit()

    # -----------------------------------------------------
    # Login users
    # -----------------------------------------------------

    admin_login = client.post(
        "/api/v1/auth/login",
        json={
            "email": admin_payload["email"],
            "password": admin_payload["password"],
        },
    )

    assert admin_login.status_code == 200

    member_login = client.post(
        "/api/v1/auth/login",
        json={
            "email": member_payload["email"],
            "password": member_payload["password"],
        },
    )

    assert member_login.status_code == 200

    outsider_login = client.post(
        "/api/v1/auth/login",
        json={
            "email": outsider_payload["email"],
            "password": outsider_payload["password"],
        },
    )

    assert outsider_login.status_code == 200

    return {
        "organization": organization,

        "owner": owner,
        "owner_headers": authenticated_headers,

        "admin": organization_admin,
        "admin_headers": {
            "Authorization": (
                f"Bearer {admin_login.json()['access_token']}"
            )
        },

        "member": organization_member,
        "member_headers": {
            "Authorization": (
                f"Bearer {member_login.json()['access_token']}"
            )
        },

        "outsider": outsider,
        "outsider_headers": {
            "Authorization": (
                f"Bearer {outsider_login.json()['access_token']}"
            )
        },
    }