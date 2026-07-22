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

from tests.seed import seed_admin_role
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
def registered_user(client, unique_user):

    response = client.post(
        "/auth/register",
        json=unique_user,
    )

    assert response.status_code == 201

    return unique_user


# ---------------------------------------------------------
# Login as Normal User
# ---------------------------------------------------------

@pytest.fixture
def authenticated_headers(client, registered_user):

    response = client.post(
        "/auth/login",
        json={
            "email": registered_user["email"],
            "password": registered_user["password"],
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
def admin_role(db):

    return seed_admin_role(db)


# ---------------------------------------------------------
# Create Admin User
# ---------------------------------------------------------

@pytest.fixture
def admin_user(client, db, admin_role):

    payload = admin_payload()

    response = client.post(
        "/auth/register",
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

    return payload


# ---------------------------------------------------------
# Login Admin
# ---------------------------------------------------------

@pytest.fixture
def admin_headers(client, admin_user):

    response = client.post(
        "/auth/login",
        json={
            "email": admin_user["email"],
            "password": admin_user["password"],
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
        .filter(Permission.name == "users.view")
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