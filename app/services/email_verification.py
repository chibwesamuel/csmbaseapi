from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    generate_email_verification_token,
    hash_email_verification_token,
)

from app.repositories.user import (
    get_user_by_email,
)

from app.repositories.email_verification_token import (
    create_email_verification_token,
    get_email_verification_token_for_update,
    revoke_all_user_email_verification_tokens_without_commit,
)

from app.services.email import (
    send_email_verification_email,
)


def request_email_verification(
    db: Session,
    email: str,
) -> str | None:
    """
    Create an email verification token for a user.

    Any previously issued, unused verification tokens are
    revoked before creating the new token.

    Returns the raw verification token when the user exists.

    Returns None when no user exists for the supplied email.
    """

    user = get_user_by_email(
        db,
        email,
    )

    if not user:
        return None

    # If the user is already verified, there is no reason
    # to issue another verification token.
    if user.is_verified:
        return None

    # Invalidate previously issued verification tokens.
    revoke_all_user_email_verification_tokens_without_commit(
        db,
        user.id,
    )

    raw_token = generate_email_verification_token()

    token_hash = hash_email_verification_token(
        raw_token,
    )

    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES,
        )
    )

    create_email_verification_token(
        db=db,
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at,
    )

    send_email_verification_email(
        to_email=user.email,
        verification_token=raw_token,
    )

    return raw_token


def verify_email(
    db: Session,
    raw_token: str,
) -> bool:
    """
    Verify a user's email address using a valid verification token.

    The user verification, token consumption, and invalidation
    of remaining verification tokens are committed as one
    database transaction.

    Returns True when the email is successfully verified.

    Returns False when the token is invalid, expired, revoked,
    already used, or when the associated user cannot be found.
    """

    token_hash = hash_email_verification_token(
        raw_token,
    )

    verification_token = get_email_verification_token_for_update(
        db,
        token_hash,
    )

    if not verification_token:
        return False

    # Token has already been used.
    if verification_token.used_at:
        return False

    # Token has been explicitly revoked.
    if verification_token.revoked_at:
        return False

    # Token has expired.
    if verification_token.expires_at < datetime.now(timezone.utc):
        return False

    user = verification_token.user

    if not user:
        return False

    # Mark the user's email as verified.
    user.is_verified = True

    # Consume the verification token.
    verification_token.used_at = datetime.now(
        timezone.utc,
    )

    # Invalidate any other outstanding verification tokens
    # belonging to this user.
    revoke_all_user_email_verification_tokens_without_commit(
        db,
        user.id,
    )

    db.commit()

    return True