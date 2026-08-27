from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from app.core.security import (
    generate_email_verification_token,
    hash_email_verification_token,
)

from app.services.email_verification import (
    request_email_verification,
    verify_email,
)


def test_request_email_verification_sends_email(
    db,
    normal_user,
):
    """
    A verification request for an existing user should
    generate a token and send it through the email service.
    """

    with patch(
        "app.services.email_verification.send_email_verification_email"
    ) as mock_send_email_verification:

        raw_token = request_email_verification(
            db=db,
            email=normal_user.email,
        )

    assert raw_token is not None

    mock_send_email_verification.assert_called_once_with(
        to_email=normal_user.email,
        verification_token=raw_token,
    )


def test_request_email_verification_returns_none_for_unknown_email(
    db,
):
    """
    A verification request for an unknown email should
    return None and should not send an email.
    """

    with patch(
        "app.services.email_verification.send_email_verification_email"
    ) as mock_send_email_verification:

        result = request_email_verification(
            db=db,
            email="unknown@example.com",
        )

    assert result is None

    mock_send_email_verification.assert_not_called()


def test_request_email_verification_creates_token(
    db,
    normal_user,
):
    """
    Requesting email verification should persist a hashed
    verification token.
    """

    with patch(
        "app.services.email_verification.send_email_verification_email"
    ):

        raw_token = request_email_verification(
            db=db,
            email=normal_user.email,
        )

    token_hash = hash_email_verification_token(
        raw_token,
    )

    from app.repositories.email_verification_token import (
        get_email_verification_token,
    )

    token = get_email_verification_token(
        db=db,
        token_hash=token_hash,
    )

    assert token is not None
    assert token.user_id == normal_user.id
    assert token.token_hash == token_hash
    assert token.used_at is None
    assert token.revoked_at is None


def test_request_email_verification_revokes_previous_tokens(
    db,
    normal_user,
):
    """
    Requesting a new verification token should revoke any
    previously active verification tokens.
    """

    with patch(
        "app.services.email_verification.send_email_verification_email"
    ):

        first_token = request_email_verification(
            db=db,
            email=normal_user.email,
        )

        second_token = request_email_verification(
            db=db,
            email=normal_user.email,
        )

    assert first_token != second_token

    from app.repositories.email_verification_token import (
        get_email_verification_token,
    )

    first_record = get_email_verification_token(
        db=db,
        token_hash=hash_email_verification_token(
            first_token,
        ),
    )

    second_record = get_email_verification_token(
        db=db,
        token_hash=hash_email_verification_token(
            second_token,
        ),
    )

    assert first_record is not None
    assert second_record is not None

    assert first_record.revoked_at is not None
    assert second_record.revoked_at is None


def test_verify_email_success(
    db,
    normal_user,
):
    """
    A valid verification token should verify the user.
    """

    normal_user.is_verified = False
    db.commit()

    with patch(
        "app.services.email_verification.send_email_verification_email"
    ):

        raw_token = request_email_verification(
            db=db,
            email=normal_user.email,
        )

    result = verify_email(
        db=db,
        raw_token=raw_token,
    )

    assert result is True

    db.refresh(normal_user)

    assert normal_user.is_verified is True


def test_verify_email_marks_token_used(
    db,
    normal_user,
):
    """
    Successfully verifying an email should mark the token
    as used.
    """

    normal_user.is_verified = False
    db.commit()

    with patch(
        "app.services.email_verification.send_email_verification_email"
    ):

        raw_token = request_email_verification(
            db=db,
            email=normal_user.email,
        )

    result = verify_email(
        db=db,
        raw_token=raw_token,
    )

    assert result is True

    from app.repositories.email_verification_token import (
        get_email_verification_token,
    )

    token = get_email_verification_token(
        db=db,
        token_hash=hash_email_verification_token(
            raw_token,
        ),
    )

    assert token is not None
    assert token.used_at is not None


def test_verify_email_rejects_unknown_token(
    db,
):
    """
    An unknown verification token should be rejected.
    """

    result = verify_email(
        db=db,
        raw_token=generate_email_verification_token(),
    )

    assert result is False


def test_verify_email_rejects_used_token(
    db,
    normal_user,
):
    """
    A verification token that has already been used should
    not be accepted again.
    """

    normal_user.is_verified = False
    db.commit()

    with patch(
        "app.services.email_verification.send_email_verification_email"
    ):

        raw_token = request_email_verification(
            db=db,
            email=normal_user.email,
        )

    assert verify_email(
        db=db,
        raw_token=raw_token,
    ) is True

    assert verify_email(
        db=db,
        raw_token=raw_token,
    ) is False


def test_verify_email_rejects_revoked_token(
    db,
    normal_user,
):
    """
    A revoked verification token should be rejected.
    """

    normal_user.is_verified = False
    db.commit()

    with patch(
        "app.services.email_verification.send_email_verification_email"
    ):

        first_token = request_email_verification(
            db=db,
            email=normal_user.email,
        )

        request_email_verification(
            db=db,
            email=normal_user.email,
        )

    result = verify_email(
        db=db,
        raw_token=first_token,
    )

    assert result is False


def test_verify_email_rejects_expired_token(
    db,
    normal_user,
):
    """
    An expired verification token should be rejected.
    """

    normal_user.is_verified = False
    db.commit()

    raw_token = generate_email_verification_token()

    from app.repositories.email_verification_token import (
        create_email_verification_token,
    )

    create_email_verification_token(
        db=db,
        user_id=normal_user.id,
        token_hash=hash_email_verification_token(
            raw_token,
        ),
        expires_at=(
            datetime.now(timezone.utc)
            - timedelta(minutes=1)
        ),
    )

    result = verify_email(
        db=db,
        raw_token=raw_token,
    )

    assert result is False

    db.refresh(normal_user)

    assert normal_user.is_verified is False


def test_verify_email_is_idempotently_blocked_after_verification(
    db,
    normal_user,
):
    """
    Once a user has been verified, a previously valid token
    cannot be used again.
    """

    normal_user.is_verified = False
    db.commit()

    with patch(
        "app.services.email_verification.send_email_verification_email"
    ):

        raw_token = request_email_verification(
            db=db,
            email=normal_user.email,
        )

    assert verify_email(
        db=db,
        raw_token=raw_token,
    ) is True

    assert verify_email(
        db=db,
        raw_token=raw_token,
    ) is False
