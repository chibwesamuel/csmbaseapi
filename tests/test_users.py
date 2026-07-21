import uuid


def test_create_user(client, admin_headers):

    unique = uuid.uuid4().hex[:8]

    payload = {
        "email": f"user_{unique}@example.com",
        "username": f"user_{unique}",
        "password": "Password123!",
        "first_name": "John",
        "last_name": "Doe",
    }

    response = client.post(
        "/users/",
        json=payload,
        headers=admin_headers,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == payload["email"]


def test_list_users(client, admin_headers):

    response = client.get(
        "/users/",
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert "users" in data
    assert "total" in data