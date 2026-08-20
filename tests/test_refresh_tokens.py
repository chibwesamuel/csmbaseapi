from fastapi import status


def register_and_login(client, unique_user):
    """
    Helper to register and login a user.
    """

    register = client.post(
        "/api/v1/auth/register",
        json=unique_user,
    )

    assert register.status_code == status.HTTP_201_CREATED

    login = client.post(
        "/api/v1/auth/login",
        json={
            "email": unique_user["email"],
            "password": unique_user["password"],
        },
    )

    assert login.status_code == status.HTTP_200_OK

    return login.json()


def test_login_returns_refresh_token(
    client,
    unique_user,
):
    """
    Login should return both access and refresh tokens.
    """

    tokens = register_and_login(
        client,
        unique_user,
    )

    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"


def test_refresh_access_token(
    client,
    unique_user,
):
    """
    A valid refresh token should generate new access
    and refresh tokens.
    """

    tokens = register_and_login(
        client,
        unique_user,
    )

    response = client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": tokens["refresh_token"],
        },
    )

    assert response.status_code == status.HTTP_200_OK

    refreshed = response.json()

    assert "access_token" in refreshed
    assert "refresh_token" in refreshed

    assert refreshed["refresh_token"] != (
        tokens["refresh_token"]
    )

    assert refreshed["token_type"] == "bearer"


def test_invalid_refresh_token(
    client,
):
    """
    Invalid refresh tokens should be rejected.
    """

    response = client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": "invalid-token",
        },
    )

    assert response.status_code == (
        status.HTTP_401_UNAUTHORIZED
    )

    assert response.json()["message"] == (
        "Invalid refresh token"
    )


def test_logout_revokes_refresh_token(
    client,
    unique_user,
):
    """
    Logout should revoke the refresh token.
    """

    tokens = register_and_login(
        client,
        unique_user,
    )

    response = client.post(
        "/api/v1/auth/logout",
        json={
            "refresh_token": tokens["refresh_token"],
        },
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.json()["message"] == (
        "Successfully logged out"
    )


def test_revoked_refresh_token_cannot_be_used(
    client,
    unique_user,
):
    """
    A revoked refresh token cannot generate new tokens.
    """

    tokens = register_and_login(
        client,
        unique_user,
    )

    logout = client.post(
        "/api/v1/auth/logout",
        json={
            "refresh_token": tokens["refresh_token"],
        },
    )

    assert logout.status_code == status.HTTP_200_OK

    response = client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": tokens["refresh_token"],
        },
    )

    assert response.status_code == (
        status.HTTP_401_UNAUTHORIZED
    )

    assert response.json()["message"] == (
        "Invalid refresh token"
    )


def test_logout_unknown_refresh_token(
    client,
):
    """
    Unknown refresh tokens should return not found.
    """

    response = client.post(
        "/api/v1/auth/logout",
        json={
            "refresh_token": "does-not-exist",
        },
    )

    assert response.status_code == (
        status.HTTP_404_NOT_FOUND
    )

    assert response.json()["message"] == (
        "Refresh token not found"
    )

def test_refresh_token_is_rotated(
    client,
    unique_user,
):
    """
    Refreshing should revoke the old token and issue a new one.
    """

    tokens = register_and_login(
        client,
        unique_user,
    )

    old_refresh_token = tokens["refresh_token"]

    response = client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": old_refresh_token,
        },
    )

    assert response.status_code == status.HTTP_200_OK

    refreshed = response.json()

    assert "access_token" in refreshed
    assert "refresh_token" in refreshed

    assert refreshed["refresh_token"] != (
        old_refresh_token
    )

    assert refreshed["token_type"] == "bearer"


def test_rotated_refresh_token_cannot_be_reused(
    client,
    unique_user,
):
    """
    A refresh token that has already been rotated
    cannot be used again.
    """

    tokens = register_and_login(
        client,
        unique_user,
    )

    old_refresh_token = tokens["refresh_token"]

    first_refresh = client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": old_refresh_token,
        },
    )

    assert first_refresh.status_code == status.HTTP_200_OK

    new_refresh_token = first_refresh.json()[
        "refresh_token"
    ]

    second_refresh = client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": old_refresh_token,
        },
    )

    assert second_refresh.status_code == (
        status.HTTP_401_UNAUTHORIZED
    )

    assert second_refresh.json()["message"] == (
        "Invalid refresh token"
    )

    # The replacement token should also have been
    # invalidated because reuse was detected.
    third_refresh = client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": new_refresh_token,
        },
    )

    assert third_refresh.status_code == (
        status.HTTP_401_UNAUTHORIZED
    )