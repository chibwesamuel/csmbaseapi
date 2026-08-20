from datetime import datetime, timedelta, timezone
import uuid

from sqlalchemy.orm import Session

from app.core.config import settings

from app.core.security import (
    generate_refresh_token,
    hash_refresh_token,
)

from app.repositories.refresh_token import (
    create_refresh_token as create_refresh_token_repository,
    get_refresh_token,
    get_refresh_token_for_update,
    rotate_refresh_token as rotate_refresh_token_repository,
    revoke_refresh_token as revoke_refresh_token_repository,
    revoke_all_user_tokens as revoke_all_user_tokens_repository,
    revoke_all_user_tokens_without_commit,
)

from app.models.user import User


def create_user_refresh_token(
    db: Session,
    user: User,
) -> str:
    """
    Generate and store a refresh token for a user.

    Returns the raw refresh token.
    """

    raw_token = generate_refresh_token()

    token_hash = hash_refresh_token(
        raw_token,
    )

    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
    )

    create_refresh_token_repository(
        db=db,
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at,
    )

    return raw_token


def validate_refresh_token(
    db: Session,
    refresh_token: str,
):
    """
    Validate a refresh token.

    Returns the associated user if valid.
    """

    token_hash = hash_refresh_token(
        refresh_token,
    )

    stored_token = get_refresh_token(
        db,
        token_hash,
    )

    if not stored_token:
        return None

    if stored_token.revoked_at:
        return None

    if stored_token.expires_at < datetime.now(timezone.utc):
        return None

    return stored_token.user


def rotate_user_refresh_token(
    db: Session,
    refresh_token: str,
):
    """
    Rotate a refresh token.

    The supplied refresh token is revoked and replaced with
    a newly generated refresh token.

    If a previously revoked refresh token is presented again,
    all active refresh tokens belonging to that user are revoked.
    """

    token_hash = hash_refresh_token(
        refresh_token,
    )

    stored_token = get_refresh_token_for_update(
        db,
        token_hash,
    )

    if not stored_token:
        return None

    # Reuse detection.
    #
    # A previously revoked token should never be presented
    # again during normal operation. If it is, revoke every
    # remaining active token belonging to the user.
    if stored_token.revoked_at:
        revoke_all_user_tokens_without_commit(
            db,
            stored_token.user_id,
        )

        db.commit()

        return None

    # Reject expired tokens.
    if stored_token.expires_at < datetime.now(timezone.utc):
        return None

    # Generate replacement refresh token.
    new_raw_token = generate_refresh_token()

    new_token_hash = hash_refresh_token(
        new_raw_token,
    )

    new_expires_at = (
        datetime.now(timezone.utc)
        + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
        )
    )

    # Revoke the old token and create the new token.
    rotate_refresh_token_repository(
        db=db,
        refresh_token=stored_token,
        new_token_hash=new_token_hash,
        new_expires_at=new_expires_at,
    )

    return stored_token.user, new_raw_token


def revoke_refresh_token(
    db: Session,
    refresh_token: str,
):
    """
    Revoke a single refresh token.
    """

    token_hash = hash_refresh_token(
        refresh_token,
    )

    stored_token = get_refresh_token(
        db,
        token_hash,
    )

    if not stored_token:
        return False

    if stored_token.revoked_at:
        return False

    revoke_refresh_token_repository(
        db,
        stored_token,
    )

    return True


def revoke_user_refresh_tokens(
    db: Session,
    user_id: uuid.UUID,
):
    """
    Revoke all refresh tokens for a user.
    """

    return revoke_all_user_tokens_repository(
        db,
        user_id,
    )