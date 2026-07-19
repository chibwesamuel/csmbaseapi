from sqlalchemy.orm import Session

from app.models.role import Role
from app.models.permission import Permission


def add_permission_to_role(
    db: Session,
    role: Role,
    permission: Permission,
):
    if permission not in role.permissions:
        role.permissions.append(permission)

    db.commit()
    db.refresh(role)

    return role


def remove_permission_from_role(
    db: Session,
    role: Role,
    permission: Permission,
):
    if permission in role.permissions:
        role.permissions.remove(permission)

    db.commit()
    db.refresh(role)

    return role


def get_role_permissions(
    db: Session,
    role: Role,
):
    return role.permissions