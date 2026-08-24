from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    generate_password_reset_token,
    hash_password_reset_token,
    hash_password,
)

from app.repositories.user import (
    get_user_by_email,
)

from app.services.email import (
    send_password_reset_email,
)

from app.repositories.password_reset_token import (
    create_password_reset_token,
    get_password_reset_token_for_update,
    revoke_all_user_password_reset_tokens_without_commit,
)

from app.repositories.refresh_token import (
    revoke_all_user_tokens_without_commit,
)


def request_password_reset(
    db: Session,
    email: str,
) -> str | None:
    """
    Create a password reset token for a user.

    Returns the raw reset token when the user exists.

    Returns None when no user exists for the supplied email.
    """

    user = get_user_by_email(
        db,
        email,
    )

    if not user:
        return None

    # Invalidate previously issued reset tokens.
    revoke_all_user_password_reset_tokens_without_commit(
        db,
        user.id,
    )

    raw_token = generate_password_reset_token()

    token_hash = hash_password_reset_token(
        raw_token,
    )

    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES,
        )
    )

    create_password_reset_token(
        db=db,
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at,
    )

    send_password_reset_email(
        to_email=user.email,
        reset_token=raw_token,
    )

    return raw_token


def reset_password(
    db: Session,
    raw_token: str,
    new_password: str,
) -> bool:
    """
    Reset a user's password using a valid password reset token.

    The password change, token consumption, and refresh-token
    revocation are committed as one database transaction.

    Returns True when the password was successfully changed.
    Returns False when the reset token is invalid.
    """

    token_hash = hash_password_reset_token(
        raw_token,
    )

    reset_token = get_password_reset_token_for_update(
        db,
        token_hash,
    )

    if not reset_token:
        return False

    # Token has already been used.
    if reset_token.used_at:
        return False

    # Token has been explicitly revoked.
    if reset_token.revoked_at:
        return False

    # Token has expired.
    if reset_token.expires_at < datetime.now(timezone.utc):
        return False

    user = reset_token.user

    if not user:
        return False

    # Update password.
    user.hashed_password = hash_password(
        new_password,
    )

    # Consume the reset token.
    reset_token.used_at = datetime.now(
        timezone.utc,
    )

    # Invalidate all existing refresh tokens/sessions.
    revoke_all_user_tokens_without_commit(
        db,
        user.id,
    )

    db.commit()

    return True

@patch(
    "app.services.password_reset.send_password_reset_email"
)
def test_request_password_reset_sends_email(
    mock_send_password_reset_email,
    db,
    normal_user,
):
    """
    A password reset request for an existing user should
    send the generated reset token through the email service.
    """

    raw_token = request_password_reset(
        db=db,
        email=normal_user.email,
    )

    assert raw_token is not None

    mock_send_password_reset_email.assert_called_once_with(
        to_email=normal_user.email,
        reset_token=raw_token,
    )