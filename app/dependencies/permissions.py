from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db

from app.dependencies.auth import get_current_user
from app.models.user import User


def require_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Ensure the current user account is active.
    """

    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account",
        )

    return current_user


def require_verified_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Ensure the current user email/account is verified.
    """

    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not verified",
        )

    return current_user


def require_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Ensure the current user has administrator privileges.
    """

    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser privileges required",
        )

    return current_user


def require_permission(permission_name: str):
    """
    Check whether the current user has a specific permission
    through any of their assigned roles.
    """

    def checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        user_permissions = []

        for role in current_user.roles:
            for permission in role.permissions:
                user_permissions.append(permission.name)

        if permission_name not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied",
            )

        return current_user

    return checker