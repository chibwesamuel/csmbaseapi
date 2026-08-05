from fastapi import status


def test_register_user(client, unique_user):
    response = client.post(
        "/api/v1/auth/register",
        json=unique_user,
    )

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert data["email"] == unique_user["email"]
    assert data["username"] == unique_user["username"]


def test_duplicate_registration(client, unique_user):
    client.post(
        "/api/v1/auth/register",
        json=unique_user,
    )

    response = client.post(
        "/api/v1/auth/register",
        json=unique_user,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_login(client, unique_user):
    client.post(
        "/api/v1/auth/register",
        json=unique_user,
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": unique_user["email"],
            "password": unique_user["password"],
        },
    )

    assert response.status_code == status.HTTP_200_OK

    token = response.json()

    assert "access_token" in token
    assert token["token_type"] == "bearer"


def test_invalid_login(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "wrong@example.com",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user(client, unique_user):
    client.post(
        "/api/v1/auth/register",
        json=unique_user,
    )

    login = client.post(
        "/api/v1/auth/login",
        json={
            "email": unique_user["email"],
            "password": unique_user["password"],
        },
    )

    assert login.status_code == status.HTTP_200_OK

    token = login.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == status.HTTP_200_OK

    me = response.json()

    assert me["email"] == unique_user["email"]

def test_get_current_user_without_token(client):
    response = client.get(
        "/api/v1/auth/me",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user_with_invalid_token(client):
    response = client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": "Bearer invalid.token.value"
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
