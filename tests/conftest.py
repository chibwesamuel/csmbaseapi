import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client():
    return TestClient(app)


@pytest.fixture
def unique_user():
    """
    Generate unique user data for every test.
    """
    unique = uuid.uuid4().hex[:8]

    return {
        "email": f"test_{unique}@example.com",
        "username": f"user_{unique}",
        "password": "Password123!",
        "first_name": "Test",
        "last_name": "User",
    }