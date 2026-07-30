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
        "/api/v1/users/",
        json=payload,
        headers=admin_headers,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == payload["email"]


def test_list_users(client, admin_headers):

    response = client.get(
        "/api/v1/users/",
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert "users" in data
    assert "total" in data


def test_get_user(client, admin_headers):

    unique = uuid.uuid4().hex[:8]

    payload = {
        "email": f"get_{unique}@example.com",
        "username": f"get_{unique}",
        "password": "Password123!",
        "first_name": "Jane",
        "last_name": "Smith",
    }

    create_response = client.post(
        "/api/v1/users/",
        json=payload,
        headers=admin_headers,
    )

    assert create_response.status_code == 201

    user_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/users/{user_id}",
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == user_id
    assert data["email"] == payload["email"]


def test_update_user(client, admin_headers):

    unique = uuid.uuid4().hex[:8]

    payload = {
        "email": f"update_{unique}@example.com",
        "username": f"update_{unique}",
        "password": "Password123!",
        "first_name": "Old",
        "last_name": "Name",
    }

    create_response = client.post(
        "/api/v1/users/",
        json=payload,
        headers=admin_headers,
    )

    assert create_response.status_code == 201

    user_id = create_response.json()["id"]

    update_payload = {
        "first_name": "Updated",
        "last_name": "User",
    }

    response = client.put(
        f"/api/v1/users/{user_id}",
        json=update_payload,
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["first_name"] == "Updated"
    assert data["last_name"] == "User"


def test_deactivate_user(client, admin_headers):

    unique = uuid.uuid4().hex[:8]

    payload = {
        "email": f"deactivate_{unique}@example.com",
        "username": f"deactivate_{unique}",
        "password": "Password123!",
        "first_name": "Deactivate",
        "last_name": "User",
    }

    create_response = client.post(
        "/api/v1/users/",
        json=payload,
        headers=admin_headers,
    )

    assert create_response.status_code == 201

    user_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/users/{user_id}/deactivate",
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["is_active"] is False


def test_activate_user(client, admin_headers):

    unique = uuid.uuid4().hex[:8]

    payload = {
        "email": f"activate_{unique}@example.com",
        "username": f"activate_{unique}",
        "password": "Password123!",
        "first_name": "Activate",
        "last_name": "User",
    }

    create_response = client.post(
        "/api/v1/users/",
        json=payload,
        headers=admin_headers,
    )

    assert create_response.status_code == 201

    user_id = create_response.json()["id"]

    deactivate_response = client.patch(
        f"/api/v1/users/{user_id}/deactivate",
        headers=admin_headers,
    )

    assert deactivate_response.status_code == 200

    response = client.patch(
        f"/api/v1/users/{user_id}/activate",
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["is_active"] is True


def test_delete_user(client, admin_headers):

    unique = uuid.uuid4().hex[:8]

    payload = {
        "email": f"delete_{unique}@example.com",
        "username": f"delete_{unique}",
        "password": "Password123!",
        "first_name": "Delete",
        "last_name": "User",
    }

    create_response = client.post(
        "/api/v1/users/",
        json=payload,
        headers=admin_headers,
    )

    assert create_response.status_code == 201

    user_id = create_response.json()["id"]

    response = client.delete(
        f"/api/v1/users/{user_id}",
        headers=admin_headers,
    )

    assert response.status_code == 200

    assert response.json()["message"] == (
        "User deleted successfully"
    )


def test_create_duplicate_email(client, admin_headers):

    unique = uuid.uuid4().hex[:8]

    payload = {
        "email": f"duplicate_{unique}@example.com",
        "username": f"duplicate_{unique}",
        "password": "Password123!",
        "first_name": "Duplicate",
        "last_name": "User",
    }

    first_response = client.post(
        "/api/v1/users/",
        json=payload,
        headers=admin_headers,
    )

    assert first_response.status_code == 201

    duplicate_payload = {
        "email": payload["email"],
        "username": f"duplicate_user_{unique}",
        "password": "Password123!",
        "first_name": "Another",
        "last_name": "User",
    }

    second_response = client.post(
        "/api/v1/users/",
        json=duplicate_payload,
        headers=admin_headers,
    )

    assert second_response.status_code == 400