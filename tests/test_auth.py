def test_register_user(client, unique_user):
    response = client.post(
        "/auth/register",
        json=unique_user,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == unique_user["email"]
    assert data["username"] == unique_user["username"]


def test_duplicate_registration(client, unique_user):
    client.post("/auth/register", json=unique_user)

    response = client.post(
        "/auth/register",
        json=unique_user,
    )

    assert response.status_code == 400


def test_login(client, unique_user):
    client.post("/auth/register", json=unique_user)

    response = client.post(
        "/auth/login",
        json={
            "email": unique_user["email"],
            "password": unique_user["password"],
        },
    )

    assert response.status_code == 200

    token = response.json()

    assert "access_token" in token
    assert token["token_type"] == "bearer"


def test_invalid_login(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "wrong@example.com",
            "password": "wrongpassword",
        },
    )

    assert response.status_code in (400, 401)


def test_get_current_user(client, unique_user):
    client.post("/auth/register", json=unique_user)

    login = client.post(
        "/auth/login",
        json={
            "email": unique_user["email"],
            "password": unique_user["password"],
        },
    )

    token = login.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    me = response.json()

    assert me["email"] == unique_user["email"]