from unittest.mock import MagicMock

import pytest

from fastapi import HTTPException

from app.dependencies.permissions import (
    require_superuser,
    require_active_user,
    require_verified_user,
    require_permission,
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

def test_require_verified_user_allows_verified_user(
    registered_user,
):
    registered_user.is_verified = True

    result = require_verified_user(
        registered_user
    )

    assert result == registered_user


def test_require_verified_user_denies_unverified_user(
    registered_user,
):
    registered_user.is_verified = False

    with pytest.raises(HTTPException) as exc:
        require_verified_user(
            registered_user
        )

    assert exc.value.status_code == 403
    assert (
        exc.value.detail
        == "User account is not verified"
    )


def test_require_permission_allows_user_with_permission():
    permission = MagicMock()
    permission.name = "users.view"

    role = MagicMock()
    role.permissions = [permission]

    user = MagicMock()
    user.roles = [role]

    checker = require_permission(
        "users.view"
    )

    result = checker(user)

    assert result == user


def test_require_permission_denies_user_without_permission():
    permission = MagicMock()
    permission.name = "users.view"

    role = MagicMock()
    role.permissions = [permission]

    user = MagicMock()
    user.roles = [role]

    checker = require_permission(
        "users.delete"
    )

    with pytest.raises(HTTPException) as exc:
        checker(user)

    assert exc.value.status_code == 403
    assert (
        exc.value.detail
        == "Permission 'users.delete' required"
    )


def test_require_permission_denies_user_without_roles():
    user = MagicMock()
    user.roles = []

    checker = require_permission(
        "users.view"
    )

    with pytest.raises(HTTPException) as exc:
        checker(user)

    assert exc.value.status_code == 403
    assert (
        exc.value.detail
        == "Permission 'users.view' required"
    )


def test_require_permission_finds_permission_through_multiple_roles():
    first_permission = MagicMock()
    first_permission.name = "users.view"

    second_permission = MagicMock()
    second_permission.name = "projects.view"

    first_role = MagicMock()
    first_role.permissions = [first_permission]

    second_role = MagicMock()
    second_role.permissions = [second_permission]

    user = MagicMock()
    user.roles = [
        first_role,
        second_role,
    ]

    checker = require_permission(
        "projects.view"
    )

    result = checker(user)

    assert result == user