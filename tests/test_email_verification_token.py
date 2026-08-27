from datetime import datetime, timedelta, timezone

from app.core.security import (
    generate_email_verification_token,
    hash_email_verification_token,
)

from app.repositories.email_verification_token import (
    create_email_verification_token,
    create_email_verification_token_without_commit,
    get_email_verification_token,
    get_email_verification_token_for_update,
    revoke_email_verification_token,
    revoke_all_user_email_verification_tokens,
    revoke_all_user_email_verification_tokens_without_commit,
    mark_email_verification_token_used,
    delete_expired_email_verification_tokens,
)


def test_create_email_verification_token(
    db,
    normal_user,
):
    """
    Creating an email verification token should persist
    the token and return the database record.
    """

    raw_token = generate_email_verification_token()
    token_hash = hash_email_verification_token(raw_token)

    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(minutes=30)
    )

    token = create_email_verification_token(
        db=db,
        user_id=normal_user.id,
        token_hash=token_hash,
        expires_at=expires_at,
    )

    assert token is not None
    assert token.id is not None
    assert token.user_id == normal_user.id
    assert token.token_hash == token_hash
    assert token.expires_at == expires_at
    assert token.used_at is None
    assert token.revoked_at is None


def test_create_email_verification_token_without_commit(
    db,
    normal_user,
):
    """
    Creating a token without commit should add it to the
    current transaction without committing it.
    """

    raw_token = generate_email_verification_token()
    token_hash = hash_email_verification_token(raw_token)

    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(minutes=30)
    )

    token = create_email_verification_token_without_commit(
        db=db,
        user_id=normal_user.id,
        token_hash=token_hash,
        expires_at=expires_at,
    )

    assert token is not None
    assert token.user_id == normal_user.id
    assert token.token_hash == token_hash

    db.commit()
    db.refresh(token)

    assert token.id is not None


def test_get_email_verification_token(
    db,
    normal_user,
):
    """
    A token should be retrievable using its hash.
    """

    raw_token = generate_email_verification_token()
    token_hash = hash_email_verification_token(raw_token)

    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(minutes=30)
    )

    created = create_email_verification_token(
        db=db,
        user_id=normal_user.id,
        token_hash=token_hash,
        expires_at=expires_at,
    )

    retrieved = get_email_verification_token(
        db=db,
        token_hash=token_hash,
    )

    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.user_id == normal_user.id


def test_get_email_verification_token_returns_none_for_unknown_hash(
    db,
):
    """
    An unknown token hash should return None.
    """

    result = get_email_verification_token(
        db=db,
        token_hash="a" * 64,
    )

    assert result is None


def test_get_email_verification_token_for_update(
    db,
    normal_user,
):
    """
    The repository should retrieve an existing token using
    the row-locking query used during token consumption.
    """

    raw_token = generate_email_verification_token()
    token_hash = hash_email_verification_token(raw_token)

    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(minutes=30)
    )

    created = create_email_verification_token(
        db=db,
        user_id=normal_user.id,
        token_hash=token_hash,
        expires_at=expires_at,
    )

    retrieved = get_email_verification_token_for_update(
        db=db,
        token_hash=token_hash,
    )

    assert retrieved is not None
    assert retrieved.id == created.id


def test_revoke_email_verification_token(
    db,
    normal_user,
):
    """
    Revoking a token should set revoked_at.
    """

    raw_token = generate_email_verification_token()
    token_hash = hash_email_verification_token(raw_token)

    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(minutes=30)
    )

    token = create_email_verification_token(
        db=db,
        user_id=normal_user.id,
        token_hash=token_hash,
        expires_at=expires_at,
    )

    assert token.revoked_at is None

    revoked = revoke_email_verification_token(
        db=db,
        email_verification_token=token,
    )

    assert revoked.revoked_at is not None


def test_revoke_all_user_email_verification_tokens(
    db,
    normal_user,
):
    """
    Revoking all active tokens should revoke every active
    token belonging to the user.
    """

    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(minutes=30)
    )

    tokens = []

    for _ in range(3):
        raw_token = generate_email_verification_token()
        token_hash = hash_email_verification_token(raw_token)

        token = create_email_verification_token(
            db=db,
            user_id=normal_user.id,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        tokens.append(token)

    revoked_count = revoke_all_user_email_verification_tokens(
        db=db,
        user_id=normal_user.id,
    )

    assert revoked_count == 3

    for token in tokens:
        db.refresh(token)
        assert token.revoked_at is not None


def test_revoke_all_user_email_verification_tokens_does_not_revoke_used_tokens(
    db,
    normal_user,
):
    """
    Already-used verification tokens should not be counted
    or modified when revoking active tokens.
    """

    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(minutes=30)
    )

    active_raw_token = generate_email_verification_token()
    active_hash = hash_email_verification_token(
        active_raw_token,
    )

    used_raw_token = generate_email_verification_token()
    used_hash = hash_email_verification_token(
        used_raw_token,
    )

    active_token = create_email_verification_token(
        db=db,
        user_id=normal_user.id,
        token_hash=active_hash,
        expires_at=expires_at,
    )

    used_token = create_email_verification_token(
        db=db,
        user_id=normal_user.id,
        token_hash=used_hash,
        expires_at=expires_at,
    )

    mark_email_verification_token_used(
        db=db,
        email_verification_token=used_token,
    )

    revoked_count = revoke_all_user_email_verification_tokens(
        db=db,
        user_id=normal_user.id,
    )

    assert revoked_count == 1

    db.refresh(active_token)
    db.refresh(used_token)

    assert active_token.revoked_at is not None
    assert used_token.revoked_at is None


def test_revoke_all_user_email_verification_tokens_without_commit(
    db,
    normal_user,
):
    """
    The without-commit variant should modify active tokens
    without committing the transaction itself.
    """

    raw_token = generate_email_verification_token()
    token_hash = hash_email_verification_token(raw_token)

    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(minutes=30)
    )

    token = create_email_verification_token(
        db=db,
        user_id=normal_user.id,
        token_hash=token_hash,
        expires_at=expires_at,
    )

    revoked_count = (
        revoke_all_user_email_verification_tokens_without_commit(
            db=db,
            user_id=normal_user.id,
        )
    )

    assert revoked_count == 1
    assert token.revoked_at is not None

    db.commit()


def test_mark_email_verification_token_used(
    db,
    normal_user,
):
    """
    Marking a verification token as used should populate
    used_at.
    """

    raw_token = generate_email_verification_token()
    token_hash = hash_email_verification_token(raw_token)

    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(minutes=30)
    )

    token = create_email_verification_token(
        db=db,
        user_id=normal_user.id,
        token_hash=token_hash,
        expires_at=expires_at,
    )

    assert token.used_at is None

    used_token = mark_email_verification_token_used(
        db=db,
        email_verification_token=token,
    )

    assert used_token.used_at is not None


def test_delete_expired_email_verification_tokens(
    db,
    normal_user,
):
    """
    Expired verification tokens should be deleted.
    """

    expired_token_hash = hash_email_verification_token(
        generate_email_verification_token(),
    )

    active_token_hash = hash_email_verification_token(
        generate_email_verification_token(),
    )

    expired_token = create_email_verification_token(
        db=db,
        user_id=normal_user.id,
        token_hash=expired_token_hash,
        expires_at=(
            datetime.now(timezone.utc)
            - timedelta(minutes=1)
        ),
    )

    active_token = create_email_verification_token(
        db=db,
        user_id=normal_user.id,
        token_hash=active_token_hash,
        expires_at=(
            datetime.now(timezone.utc)
            + timedelta(minutes=30)
        ),
    )

    expired_id = expired_token.id
    active_id = active_token.id

    deleted_count = delete_expired_email_verification_tokens(
        db=db,
    )

    assert deleted_count == 1

    assert (
        get_email_verification_token(
            db=db,
            token_hash=expired_token_hash,
        )
        is None
    )

    remaining = get_email_verification_token(
        db=db,
        token_hash=active_token_hash,
    )

    assert remaining is not None
    assert remaining.id == active_id
    assert remaining.id != expired_id
