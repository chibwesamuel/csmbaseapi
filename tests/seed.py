from sqlalchemy.orm import Session

from app.models.permission import Permission
from app.models.role import Role


DEFAULT_PERMISSIONS = [
    "users.view",
    "users.create",
    "users.update",
    "users.delete",

    "roles.view",
    "roles.create",
    "roles.update",
    "roles.delete",

    "permissions.view",
    "permissions.create",
    "permissions.update",
    "permissions.delete",

    "organizations.view",
    "organizations.create",
    "organizations.update",
    "organizations.delete",
]


def seed_permissions(db: Session):

    permissions = []

    for name in DEFAULT_PERMISSIONS:

        permission = (
            db.query(Permission)
            .filter(Permission.name == name)
            .first()
        )

        if permission is None:

            permission = Permission(
                name=name,
                description=name,
            )

            db.add(permission)
            db.flush()

        permissions.append(permission)

    db.commit()

    return permissions


def seed_admin_role(db: Session):

    role = (
        db.query(Role)
        .filter(Role.name == "Admin")
        .first()
    )

    if role is None:

        role = Role(
            name="Admin",
            description="System Administrator",
        )

        db.add(role)
        db.flush()

    permissions = seed_permissions(db)

    for permission in permissions:

        if permission not in role.permissions:
            role.permissions.append(permission)

    db.commit()

    return role