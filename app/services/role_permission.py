from uuid import UUID

from sqlalchemy.orm import Session

from app.models.permission import Permission

from app.repositories.role import (
    get_role_by_id,
)

from app.repositories.permission import (
    get_permission_by_id,
)

from app.repositories.role_permission import (
    add_permission_to_role,
    remove_permission_from_role,
    get_role_permissions,
)


def assign_permission(
    db: Session,
    role_id: UUID,
    permission_id: UUID,
) -> Permission:
    """
    Assign a permission to a role.
    """

    role = get_role_by_id(
        db,
        role_id,
    )

    if role is None:
        raise ValueError(
            "Role not found"
        )

    permission = get_permission_by_id(
        db,
        permission_id,
    )

    if permission is None:
        raise ValueError(
            "Permission not found"
        )

    if permission in role.permissions:
        raise ValueError(
            "Permission already assigned to role"
        )

    add_permission_to_role(
        db,
        role,
        permission,
    )

    return permission


def revoke_permission(
    db: Session,
    role_id: UUID,
    permission_id: UUID,
) -> Permission:
    """
    Remove a permission from a role.
    """

    role = get_role_by_id(
        db,
        role_id,
    )

    if role is None:
        raise ValueError(
            "Role not found"
        )

    permission = get_permission_by_id(
        db,
        permission_id,
    )

    if permission is None:
        raise ValueError(
            "Permission not found"
        )

    if permission not in role.permissions:
        raise ValueError(
            "Permission is not assigned to role"
        )

    remove_permission_from_role(
        db,
        role,
        permission,
    )

    return permission


def list_role_permissions(
    db: Session,
    role_id: UUID,
):
    """
    Retrieve all permissions assigned to a role.
    """

    role = get_role_by_id(
        db,
        role_id,
    )

    if role is None:
        return None

    return get_role_permissions(
        role,
    )