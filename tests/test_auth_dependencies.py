from unittest.mock import patch

from fastapi import HTTPException

from app.dependencies.auth import get_current_user


def test_invalid_token_returns_401(db):
    with patch(
        "app.dependencies.auth.decode_access_token",
        return_value=None,
    ):
        try:
            get_current_user(
                token="invalid",
                db=db,
            )
            assert False

        except HTTPException as exc:
            assert exc.status_code == 401
            assert (
                exc.detail
                == "Invalid authentication credentials"
            )


def test_invalid_payload_returns_401(db):
    with patch(
        "app.dependencies.auth.decode_access_token",
        return_value={
            "username": "missing",
        },
    ):
        try:
            get_current_user(
                token="valid",
                db=db,
            )
            assert False

        except HTTPException as exc:
            assert exc.status_code == 401
            assert exc.detail == "Invalid token payload"


def test_missing_user_returns_401(db):
    with patch(
        "app.dependencies.auth.decode_access_token",
        return_value={
            "sub": "missing@example.com",
        },
    ):
        try:
            get_current_user(
                token="valid",
                db=db,
            )
            assert False

        except HTTPException as exc:
            assert exc.status_code == 401
            assert exc.detail == "User not found"