import pytest

from fastapi import HTTPException

from app.dependencies.permissions import (
    require_superuser,
    require_active_user,
)


def test_require_superuser_denies_normal_user(
    registered_user,
):
    registered_user.is_superuser = False

    with pytest.raises(HTTPException) as exc:
        require_superuser(registered_user)

    assert exc.value.status_code == 403
    assert (
        exc.value.detail
        == "Superuser privileges required"
    )


def test_require_active_user_denies_inactive_user(
    registered_user,
):
    registered_user.is_active = False

    with pytest.raises(HTTPException) as exc:
        require_active_user(registered_user)

    assert exc.value.status_code == 403
    assert (
        exc.value.detail
        == "Inactive user account"
    )