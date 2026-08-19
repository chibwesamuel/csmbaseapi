import uuid

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken


def create_refresh_token(
    db: Session,
    user_id: uuid.UUID,
    token_hash: str,
    expires_at: datetime,
) -> RefreshToken:
    """
    Store a new refresh token.
    """

    refresh_token = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
    )

    db.add(refresh_token)
    db.commit()
    db.refresh(refresh_token)

    return refresh_token


def get_refresh_token(
    db: Session,
    token_hash: str,
) -> RefreshToken | None:
    """
    Retrieve a refresh token by its hash.
    """

    return (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token_hash == token_hash,
        )
        .first()
    )


def get_refresh_token_for_update(
    db: Session,
    token_hash: str,
) -> RefreshToken | None:
    """
    Retrieve a refresh token while locking its database row.

    The row lock prevents concurrent refresh requests from
    rotating the same refresh token simultaneously.
    """

    return (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token_hash == token_hash,
        )
        .with_for_update()
        .first()
    )


def rotate_refresh_token(
    db: Session,
    refresh_token: RefreshToken,
    new_token_hash: str,
    new_expires_at: datetime,
) -> RefreshToken:
    """
    Revoke the existing refresh token and create its replacement
    within a single database transaction.
    """

    refresh_token.revoked_at = datetime.now(timezone.utc)

    new_refresh_token = RefreshToken(
        user_id=refresh_token.user_id,
        token_hash=new_token_hash,
        expires_at=new_expires_at,
    )

    db.add(new_refresh_token)

    db.commit()
    db.refresh(new_refresh_token)

    return new_refresh_token


def revoke_refresh_token(
    db: Session,
    refresh_token: RefreshToken,
) -> RefreshToken:
    """
    Revoke a refresh token.
    """

    refresh_token.revoked_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(refresh_token)

    return refresh_token


def revoke_all_user_tokens(
    db: Session,
    user_id: uuid.UUID,
) -> int:
    """
    Revoke every active refresh token belonging to a user.

    Returns the number of revoked tokens.
    """

    tokens = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
        )
        .all()
    )

    now = datetime.now(timezone.utc)

    for token in tokens:
        token.revoked_at = now

    db.commit()

    return len(tokens)


def revoke_all_user_tokens_without_commit(
    db: Session,
    user_id: uuid.UUID,
) -> int:
    """
    Revoke all active refresh tokens for a user without
    committing the current transaction.

    The caller is responsible for committing or rolling back.
    """

    tokens = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
        )
        .all()
    )

    now = datetime.now(timezone.utc)

    for token in tokens:
        token.revoked_at = now

    return len(tokens)


def delete_expired_tokens(
    db: Session,
) -> int:
    """
    Delete expired refresh tokens.

    Returns the number deleted.
    """

    expired = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.expires_at < datetime.now(timezone.utc),
        )
        .all()
    )

    deleted = len(expired)

    for token in expired:
        db.delete(token)

    db.commit()

    return deleted