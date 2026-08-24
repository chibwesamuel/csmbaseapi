import uuid

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.password_reset_token import (
    PasswordResetToken,
)


def create_password_reset_token(
    db: Session,
    user_id: uuid.UUID,
    token_hash: str,
    expires_at: datetime,
) -> PasswordResetToken:
    """
    Store a new password reset token.

    This function commits the transaction immediately.
    """

    password_reset_token = PasswordResetToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
    )

    db.add(password_reset_token)
    db.commit()
    db.refresh(password_reset_token)

    return password_reset_token


def create_password_reset_token_without_commit(
    db: Session,
    user_id: uuid.UUID,
    token_hash: str,
    expires_at: datetime,
) -> PasswordResetToken:
    """
    Store a new password reset token without committing.

    The caller is responsible for committing or rolling back
    the current transaction.
    """

    password_reset_token = PasswordResetToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
    )

    db.add(password_reset_token)

    return password_reset_token


def get_password_reset_token(
    db: Session,
    token_hash: str,
) -> PasswordResetToken | None:
    """
    Retrieve a password reset token by its hash.
    """

    return (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.token_hash == token_hash,
        )
        .first()
    )


def get_password_reset_token_for_update(
    db: Session,
    token_hash: str,
) -> PasswordResetToken | None:
    """
    Retrieve a password reset token while locking its
    database row.

    The row lock prevents the same reset token from being
    consumed concurrently by multiple requests.
    """

    return (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.token_hash == token_hash,
        )
        .with_for_update()
        .first()
    )


def revoke_password_reset_token(
    db: Session,
    password_reset_token: PasswordResetToken,
) -> PasswordResetToken:
    """
    Revoke a password reset token.
    """

    password_reset_token.revoked_at = (
        datetime.now(timezone.utc)
    )

    db.commit()
    db.refresh(password_reset_token)

    return password_reset_token


def revoke_all_user_password_reset_tokens(
    db: Session,
    user_id: uuid.UUID,
) -> int:
    """
    Revoke all active password reset tokens belonging
    to a user.

    Returns the number of tokens revoked.
    """

    tokens = (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.user_id == user_id,
            PasswordResetToken.used_at.is_(None),
            PasswordResetToken.revoked_at.is_(None),
        )
        .all()
    )

    now = datetime.now(timezone.utc)

    for token in tokens:
        token.revoked_at = now

    db.commit()

    return len(tokens)


def revoke_all_user_password_reset_tokens_without_commit(
    db: Session,
    user_id: uuid.UUID,
) -> int:
    """
    Revoke all active password reset tokens for a user
    without committing the current transaction.

    The caller is responsible for committing or rolling back.
    """

    tokens = (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.user_id == user_id,
            PasswordResetToken.used_at.is_(None),
            PasswordResetToken.revoked_at.is_(None),
        )
        .all()
    )

    now = datetime.now(timezone.utc)

    for token in tokens:
        token.revoked_at = now

    return len(tokens)


def mark_password_reset_token_used(
    db: Session,
    password_reset_token: PasswordResetToken,
) -> PasswordResetToken:
    """
    Mark a password reset token as used.
    """

    password_reset_token.used_at = (
        datetime.now(timezone.utc)
    )

    db.commit()
    db.refresh(password_reset_token)

    return password_reset_token


def delete_expired_password_reset_tokens(
    db: Session,
) -> int:
    """
    Delete expired password reset tokens.

    Returns the number deleted.
    """

    expired_tokens = (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.expires_at
            < datetime.now(timezone.utc),
        )
        .all()
    )

    deleted = len(expired_tokens)

    for token in expired_tokens:
        db.delete(token)

    db.commit()

    return deleted