from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from fastapi import status

from app.core.security import (
    hash_password,
    hash_password_reset_token,
)

from app.models.password_reset_token import (
    PasswordResetToken,
)

from app.repositories.password_reset_token import (
    get_password_reset_token,
)

from app.services.password_reset import (
    request_password_reset,
    reset_password,
)

@pytest.fixture(autouse=True)
def mock_password_reset_email():
    with patch(
        "app.services.password_reset.send_password_reset_email"
    ) as mock:
        yield mock

# ---------------------------------------------------------
# Request Password Reset
# ---------------------------------------------------------


def test_request_password_reset_creates_token(
    db,
    normal_user,
):
    """
    A password reset request for an existing user should
    create a reset token and return the raw token.
    """

    raw_token = request_password_reset(
        db=db,
        email=normal_user.email,
    )

    assert raw_token is not None
    assert len(raw_token) > 0

    from app.core.security import hash_password_reset_token

    token_hash = hash_password_reset_token(
        raw_token,
    )

    reset_token = get_password_reset_token(
        db,
        token_hash,
    )

    assert reset_token is not None
    assert reset_token.user_id == normal_user.id
    assert reset_token.used_at is None
    assert reset_token.revoked_at is None
    assert reset_token.expires_at > datetime.now(
        timezone.utc
    )


def test_request_password_reset_returns_none_for_unknown_email(
    db,
):
    """
    A password reset request for an unknown email should
    return None without creating a token.
    """

    result = request_password_reset(
        db=db,
        email="nonexistent@example.com",
    )

    assert result is None


def test_request_password_reset_revokes_previous_tokens(
    db,
    normal_user,
):
    """
    Requesting a new password reset should revoke any
    previously issued active reset tokens.
    """

    first_token = request_password_reset(
        db=db,
        email=normal_user.email,
    )

    assert first_token is not None

    second_token = request_password_reset(
        db=db,
        email=normal_user.email,
    )

    assert second_token is not None
    assert second_token != first_token

    from app.core.security import hash_password_reset_token

    first_record = get_password_reset_token(
        db,
        hash_password_reset_token(first_token),
    )

    second_record = get_password_reset_token(
        db,
        hash_password_reset_token(second_token),
    )

    assert first_record is not None
    assert second_record is not None

    assert first_record.revoked_at is not None
    assert second_record.revoked_at is None


def test_password_reset_token_stores_only_hash(
    db,
    normal_user,
):
    """
    The raw password reset token must never be stored in
    the database.
    """

    raw_token = request_password_reset(
        db=db,
        email=normal_user.email,
    )

    assert raw_token is not None

    from app.core.security import hash_password_reset_token

    reset_token = get_password_reset_token(
        db,
        hash_password_reset_token(raw_token),
    )

    assert reset_token is not None
    assert reset_token.token_hash != raw_token
    assert len(reset_token.token_hash) == 64


# ---------------------------------------------------------
# Reset Password
# ---------------------------------------------------------


def test_reset_password_successfully_changes_password(
    db,
    normal_user,
):
    """
    A valid password reset token should allow the user's
    password to be changed.
    """

    raw_token = request_password_reset(
        db=db,
        email=normal_user.email,
    )

    assert raw_token is not None

    result = reset_password(
        db=db,
        raw_token=raw_token,
        new_password="NewSecurePassword123!",
    )

    assert result is True

    db.refresh(normal_user)

    from app.core.security import verify_password

    assert verify_password(
        "NewSecurePassword123!",
        normal_user.hashed_password,
    )


def test_reset_password_marks_token_as_used(
    db,
    normal_user,
):
    """
    A successfully consumed password reset token should
    be marked as used.
    """

    raw_token = request_password_reset(
        db=db,
        email=normal_user.email,
    )

    assert raw_token is not None

    result = reset_password(
        db=db,
        raw_token=raw_token,
        new_password="NewSecurePassword123!",
    )

    assert result is True

    from app.core.security import hash_password_reset_token

    reset_token = get_password_reset_token(
        db,
        hash_password_reset_token(raw_token),
    )

    assert reset_token is not None
    assert reset_token.used_at is not None


def test_used_password_reset_token_cannot_be_reused(
    db,
    normal_user,
):
    """
    A password reset token must be single-use.
    """

    raw_token = request_password_reset(
        db=db,
        email=normal_user.email,
    )

    assert raw_token is not None

    first_reset = reset_password(
        db=db,
        raw_token=raw_token,
        new_password="NewSecurePassword123!",
    )

    assert first_reset is True

    second_reset = reset_password(
        db=db,
        raw_token=raw_token,
        new_password="AnotherPassword123!",
    )

    assert second_reset is False


def test_invalid_password_reset_token_is_rejected(
    db,
):
    """
    An unknown reset token should be rejected.
    """

    result = reset_password(
        db=db,
        raw_token="invalid-password-reset-token",
        new_password="NewSecurePassword123!",
    )

    assert result is False


def test_expired_password_reset_token_is_rejected(
    db,
    normal_user,
):
    """
    An expired password reset token must not be accepted.
    """

    raw_token = request_password_reset(
        db=db,
        email=normal_user.email,
    )

    assert raw_token is not None

    from app.core.security import hash_password_reset_token

    reset_token = get_password_reset_token(
        db,
        hash_password_reset_token(raw_token),
    )

    assert reset_token is not None

    reset_token.expires_at = (
        datetime.now(timezone.utc)
        - timedelta(minutes=1)
    )

    db.commit()

    result = reset_password(
        db=db,
        raw_token=raw_token,
        new_password="NewSecurePassword123!",
    )

    assert result is False


def test_revoked_password_reset_token_is_rejected(
    db,
    normal_user,
):
    """
    A revoked password reset token must not be accepted.
    """

    raw_token = request_password_reset(
        db=db,
        email=normal_user.email,
    )

    assert raw_token is not None

    from app.core.security import hash_password_reset_token
    from app.repositories.password_reset_token import (
        revoke_password_reset_token,
        get_password_reset_token,
    )

    reset_token = get_password_reset_token(
        db,
        hash_password_reset_token(raw_token),
    )

    assert reset_token is not None

    revoke_password_reset_token(
        db,
        reset_token,
    )

    result = reset_password(
        db=db,
        raw_token=raw_token,
        new_password="NewSecurePassword123!",
    )

    assert result is False


# ---------------------------------------------------------
# Refresh Token Invalidation
# ---------------------------------------------------------


def test_password_reset_revokes_existing_refresh_tokens(
    client,
    db,
    normal_user,
):
    """
    Resetting a password should invalidate all existing
    refresh tokens for the user.
    """

    password = "Password123!"

    # Ensure the known fixture password is correct.
    normal_user.hashed_password = hash_password(
        password,
    )

    db.commit()
    db.refresh(normal_user)

    login = client.post(
        "/api/v1/auth/login",
        json={
            "email": normal_user.email,
            "password": password,
        },
    )

    assert login.status_code == status.HTTP_200_OK

    refresh_token = login.json()["refresh_token"]

    raw_reset_token = request_password_reset(
        db=db,
        email=normal_user.email,
    )

    assert raw_reset_token is not None

    result = reset_password(
        db=db,
        raw_token=raw_reset_token,
        new_password="NewSecurePassword123!",
    )

    assert result is True

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


def test_password_reset_new_password_can_login(
    client,
    db,
    normal_user,
):
    """
    After a successful password reset, the new password
    should authenticate successfully.
    """

    raw_reset_token = request_password_reset(
        db=db,
        email=normal_user.email,
    )

    assert raw_reset_token is not None

    new_password = "NewSecurePassword123!"

    result = reset_password(
        db=db,
        raw_token=raw_reset_token,
        new_password=new_password,
    )

    assert result is True

    login = client.post(
        "/api/v1/auth/login",
        json={
            "email": normal_user.email,
            "password": new_password,
        },
    )

    assert login.status_code == status.HTTP_200_OK


def test_password_reset_old_password_cannot_login(
    client,
    db,
    normal_user,
):
    """
    After a successful password reset, the old password
    must no longer authenticate.
    """

    old_password = "Password123!"
    new_password = "NewSecurePassword123!"

    normal_user.hashed_password = hash_password(
        old_password,
    )

    db.commit()
    db.refresh(normal_user)

    raw_reset_token = request_password_reset(
        db=db,
        email=normal_user.email,
    )

    assert raw_reset_token is not None

    result = reset_password(
        db=db,
        raw_token=raw_reset_token,
        new_password=new_password,
    )

    assert result is True

    login = client.post(
        "/api/v1/auth/login",
        json={
            "email": normal_user.email,
            "password": old_password,
        },
    )

    assert login.status_code == (
        status.HTTP_401_UNAUTHORIZED
    )

def test_request_password_reset_sends_email(
    db,
    normal_user,
    mock_password_reset_email,
):
    """
    A password reset request for an existing user should
    send a password reset email containing the raw token.
    """

    raw_token = request_password_reset(
        db=db,
        email=normal_user.email,
    )

    mock_password_reset_email.assert_called_once_with(
        to_email=normal_user.email,
        reset_token=raw_token,
    )