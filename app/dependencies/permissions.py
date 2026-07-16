from fastapi import Depends, HTTPException, status

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