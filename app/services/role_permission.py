from sqlalchemy.orm import Session

from app.repositories.role_permission import (
    add_permission_to_role,
    remove_permission_from_role,
    get_role_permissions,
)

from app.repositories.role import get_role_by_id
from app.repositories.permission import get_permission_by_id


def assign_permission(
    db: Session,
    role_id,
    permission_id,
):
    role = get_role_by_id(
        db,
        role_id,
    )

    if not role:
        return None

    permission = get_permission_by_id(
        db,
        permission_id,
    )

    if not permission:
        return None

    return add_permission_to_role(
        db,
        role,
        permission,
    )


def revoke_permission(
    db: Session,
    role_id,
    permission_id,
):
    role = get_role_by_id(
        db,
        role_id,
    )

    if not role:
        return None

    permission = get_permission_by_id(
        db,
        permission_id,
    )

    if not permission:
        return None

    return remove_permission_from_role(
        db,
        role,
        permission,
    )


def list_role_permissions(
    db: Session,
    role_id,
):
    role = get_role_by_id(
        db,
        role_id,
    )

    if not role:
        return None

    return get_role_permissions(
        db,
        role,
    )