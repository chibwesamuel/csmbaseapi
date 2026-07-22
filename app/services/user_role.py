from uuid import UUID

from sqlalchemy.orm import Session

from app.models.role import Role
from app.models.user import User

from app.repositories.role import (
    get_role_by_id,
)

from app.repositories.user import (
    get_user_by_id,
)

from app.repositories.user_role import (
    assign_role_to_user,
    remove_role_from_user,
    get_user_roles,
)


def assign_user_role(
    db: Session,
    user_id: UUID,
    role_id: UUID,
) -> User:
    """
    Assign a role to a user.
    """

    user = get_user_by_id(
        db,
        user_id,
    )

    if user is None:
        raise ValueError(
            "User not found"
        )

    role = get_role_by_id(
        db,
        role_id,
    )

    if role is None:
        raise ValueError(
            "Role not found"
        )

    if role in user.roles:
        raise ValueError(
            "Role already assigned to user"
        )

    return assign_role_to_user(
        db,
        user,
        role,
    )


def remove_user_role(
    db: Session,
    user_id: UUID,
    role_id: UUID,
) -> User:
    """
    Remove a role from a user.
    """

    user = get_user_by_id(
        db,
        user_id,
    )

    if user is None:
        raise ValueError(
            "User not found"
        )

    role = get_role_by_id(
        db,
        role_id,
    )

    if role is None:
        raise ValueError(
            "Role not found"
        )

    if role not in user.roles:
        raise ValueError(
            "Role is not assigned to user"
        )

    return remove_role_from_user(
        db,
        user,
        role,
    )


def list_user_roles(
    db: Session,
    user_id: UUID,
) -> list[Role]:
    """
    Retrieve all roles assigned to a user.
    """

    user = get_user_by_id(
        db,
        user_id,
    )

    if user is None:
        raise ValueError(
            "User not found"
        )

    return get_user_roles(
        user,
    )