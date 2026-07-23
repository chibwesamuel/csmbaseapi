from datetime import datetime, timedelta, timezone
import uuid

from sqlalchemy.orm import Session

from app.core.security import (
    generate_refresh_token,
    hash_refresh_token,
    verify_refresh_token,
)

from app.repositories.refresh_token import (
    create_refresh_token as create_refresh_token_repository,
    get_refresh_token,
    revoke_refresh_token as revoke_refresh_token_repository,
    revoke_all_user_tokens as revoke_all_user_tokens_repository,
)

from app.models.user import User


REFRESH_TOKEN_EXPIRE_DAYS = 7


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
        days=REFRESH_TOKEN_EXPIRE_DAYS,
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