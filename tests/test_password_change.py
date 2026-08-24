from fastapi import status


def test_change_password(
    client,
    unique_user,
    authenticated_headers,
):
    """
    An authenticated user should be able to change
    their password using the correct current password.
    """

    response = client.post(
        "/api/v1/auth/change-password",
        headers=authenticated_headers,
        json={
            "current_password": unique_user["password"],
            "new_password": "NewSecurePassword123!",
        },
    )

    assert response.status_code == (
        status.HTTP_200_OK
    )

    assert response.json()["message"] == (
        "Password changed successfully"
    )


def test_change_password_requires_authentication(
    client,
    unique_user,
):
    """
    Password changes require authentication.
    """

    response = client.post(
        "/api/v1/auth/change-password",
        json={
            "current_password": unique_user["password"],
            "new_password": "NewSecurePassword123!",
        },
    )

    assert response.status_code == (
        status.HTTP_401_UNAUTHORIZED
    )


def test_change_password_rejects_wrong_current_password(
    client,
    authenticated_headers,
):
    """
    An incorrect current password should be rejected.
    """

    response = client.post(
        "/api/v1/auth/change-password",
        headers=authenticated_headers,
        json={
            "current_password": "WrongPassword123!",
            "new_password": "NewSecurePassword123!",
        },
    )

    assert response.status_code == (
        status.HTTP_401_UNAUTHORIZED
    )

    assert response.json()["message"] == (
        "Current password is incorrect"
    )


def test_change_password_rejects_same_password(
    client,
    unique_user,
    authenticated_headers,
):
    """
    The new password must differ from the current password.
    """

    response = client.post(
        "/api/v1/auth/change-password",
        headers=authenticated_headers,
        json={
            "current_password": unique_user["password"],
            "new_password": unique_user["password"],
        },
    )

    assert response.status_code == (
        status.HTTP_400_BAD_REQUEST
    )

    assert response.json()["message"] == (
        "New password must be different from the current password"
    )


def test_new_password_can_be_used_for_login(
    client,
    unique_user,
    authenticated_headers,
):
    """
    After changing the password, the new password
    should authenticate successfully.
    """

    new_password = "NewSecurePassword123!"

    response = client.post(
        "/api/v1/auth/change-password",
        headers=authenticated_headers,
        json={
            "current_password": unique_user["password"],
            "new_password": new_password,
        },
    )

    assert response.status_code == (
        status.HTTP_200_OK
    )

    login = client.post(
        "/api/v1/auth/login",
        json={
            "email": unique_user["email"],
            "password": new_password,
        },
    )

    assert login.status_code == (
        status.HTTP_200_OK
    )


def test_old_password_cannot_login_after_change(
    client,
    unique_user,
    authenticated_headers,
):
    """
    The old password must no longer authenticate
    after a successful password change.
    """

    response = client.post(
        "/api/v1/auth/change-password",
        headers=authenticated_headers,
        json={
            "current_password": unique_user["password"],
            "new_password": "NewSecurePassword123!",
        },
    )

    assert response.status_code == (
        status.HTTP_200_OK
    )

    login = client.post(
        "/api/v1/auth/login",
        json={
            "email": unique_user["email"],
            "password": unique_user["password"],
        },
    )

    assert login.status_code == (
        status.HTTP_401_UNAUTHORIZED
    )


def test_password_change_revokes_existing_refresh_tokens(
    client,
    unique_user,
    authenticated_headers,
):
    """
    Changing a password should invalidate refresh tokens
    issued before the password change.
    """

    login = client.post(
        "/api/v1/auth/login",
        json={
            "email": unique_user["email"],
            "password": unique_user["password"],
        },
    )

    assert login.status_code == (
        status.HTTP_200_OK
    )

    refresh_token = login.json()["refresh_token"]

    response = client.post(
        "/api/v1/auth/change-password",
        headers=authenticated_headers,
        json={
            "current_password": unique_user["password"],
            "new_password": "NewSecurePassword123!",
        },
    )

    assert response.status_code == (
        status.HTTP_200_OK
    )

    refresh = client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert refresh.status_code == (
        status.HTTP_401_UNAUTHORIZED
    )

    assert refresh.json()["message"] == (
        "Invalid refresh token"
    )