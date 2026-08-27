import uuid

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.email_verification_token import (
    EmailVerificationToken,
)


def create_email_verification_token(
    db: Session,
    user_id: uuid.UUID,
    token_hash: str,
    expires_at: datetime,
) -> EmailVerificationToken:
    """
    Store a new email verification token.

    This function commits the transaction immediately.
    """

    email_verification_token = EmailVerificationToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
    )

    db.add(email_verification_token)
    db.commit()
    db.refresh(email_verification_token)

    return email_verification_token


def create_email_verification_token_without_commit(
    db: Session,
    user_id: uuid.UUID,
    token_hash: str,
    expires_at: datetime,
) -> EmailVerificationToken:
    """
    Store a new email verification token without committing.

    The caller is responsible for committing or rolling back
    the current transaction.
    """

    email_verification_token = EmailVerificationToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
    )

    db.add(email_verification_token)

    return email_verification_token


def get_email_verification_token(
    db: Session,
    token_hash: str,
) -> EmailVerificationToken | None:
    """
    Retrieve an email verification token by its hash.
    """

    return (
        db.query(EmailVerificationToken)
        .filter(
            EmailVerificationToken.token_hash == token_hash,
        )
        .first()
    )


def get_email_verification_token_for_update(
    db: Session,
    token_hash: str,
) -> EmailVerificationToken | None:
    """
    Retrieve an email verification token while locking
    its database row.

    The row lock prevents the same verification token from
    being consumed concurrently by multiple requests.
    """

    return (
        db.query(EmailVerificationToken)
        .filter(
            EmailVerificationToken.token_hash == token_hash,
        )
        .with_for_update()
        .first()
    )


def revoke_email_verification_token(
    db: Session,
    email_verification_token: EmailVerificationToken,
) -> EmailVerificationToken:
    """
    Revoke an email verification token.
    """

    email_verification_token.revoked_at = (
        datetime.now(timezone.utc)
    )

    db.commit()
    db.refresh(email_verification_token)

    return email_verification_token


def revoke_all_user_email_verification_tokens(
    db: Session,
    user_id: uuid.UUID,
) -> int:
    """
    Revoke all active email verification tokens belonging
    to a user.

    Returns the number of tokens revoked.
    """

    tokens = (
        db.query(EmailVerificationToken)
        .filter(
            EmailVerificationToken.user_id == user_id,
            EmailVerificationToken.used_at.is_(None),
            EmailVerificationToken.revoked_at.is_(None),
        )
        .all()
    )

    now = datetime.now(timezone.utc)

    for token in tokens:
        token.revoked_at = now

    db.commit()

    return len(tokens)


def revoke_all_user_email_verification_tokens_without_commit(
    db: Session,
    user_id: uuid.UUID,
) -> int:
    """
    Revoke all active email verification tokens for a user
    without committing the current transaction.

    The caller is responsible for committing or rolling back.
    """

    tokens = (
        db.query(EmailVerificationToken)
        .filter(
            EmailVerificationToken.user_id == user_id,
            EmailVerificationToken.used_at.is_(None),
            EmailVerificationToken.revoked_at.is_(None),
        )
        .all()
    )

    now = datetime.now(timezone.utc)

    for token in tokens:
        token.revoked_at = now

    return len(tokens)


def mark_email_verification_token_used(
    db: Session,
    email_verification_token: EmailVerificationToken,
) -> EmailVerificationToken:
    """
    Mark an email verification token as used.
    """

    email_verification_token.used_at = (
        datetime.now(timezone.utc)
    )

    db.commit()
    db.refresh(email_verification_token)

    return email_verification_token


def delete_expired_email_verification_tokens(
    db: Session,
) -> int:
    """
    Delete expired email verification tokens.

    Returns the number of deleted tokens.
    """

    expired_tokens = (
        db.query(EmailVerificationToken)
        .filter(
            EmailVerificationToken.expires_at
            < datetime.now(timezone.utc),
        )
        .all()
    )

    deleted = len(expired_tokens)

    for token in expired_tokens:
        db.delete(token)

    db.commit()

    return deleted