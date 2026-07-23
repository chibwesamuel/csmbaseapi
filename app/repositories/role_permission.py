from app.models.permission import Permission
from app.models.role import Role

from sqlalchemy.orm import Session


def add_permission_to_role(
    db: Session,
    role: Role,
    permission: Permission,
) -> Permission:
    """
    Assign a permission to a role.
    """

    role.permissions.append(permission)

    db.commit()
    db.refresh(role)

    return permission


def remove_permission_from_role(
    db: Session,
    role: Role,
    permission: Permission,
) -> Role:
    """
    Remove a permission from a role.
    """

    role.permissions.remove(permission)

    db.commit()
    db.refresh(role)

    return role


def get_role_permissions(
    role: Role,
) -> list[Permission]:
    """
    Retrieve all permissions assigned to a role.
    """

    return role.permissions