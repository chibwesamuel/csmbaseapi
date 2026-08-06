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