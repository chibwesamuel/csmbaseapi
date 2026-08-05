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

    "organizations.members.view",
    "organizations.members.create",
    "organizations.members.update",
    "organizations.members.delete",

    "projects.view",
    "projects.create",
    "projects.update",
    "projects.delete",
]


def seed_permissions(db: Session):
    """
    Seed all application permissions.
    """

    permissions = []

    for name in DEFAULT_PERMISSIONS:

        permission = (
            db.query(Permission)
            .filter(
                Permission.name == name
            )
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
    """
    Seed the global system administrator role.
    """

    role = (
        db.query(Role)
        .filter(
            Role.name == "Admin"
        )
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


def seed_organization_roles(db: Session):
    """
    Seed organization membership roles.

    These roles are referenced by:
    organization_members.role_id
    """

    organization_roles = [
        {
            "name": "owner",
            "description": "Organization Owner",
        },
        {
            "name": "admin",
            "description": "Organization Administrator",
        },
        {
            "name": "member",
            "description": "Organization Member",
        },
    ]

    roles = []

    for role_data in organization_roles:

        role = (
            db.query(Role)
            .filter(
                Role.name == role_data["name"]
            )
            .first()
        )

        if role is None:

            role = Role(
                name=role_data["name"],
                description=role_data["description"],
            )

            db.add(role)
            db.flush()

        roles.append(role)

    db.commit()

    return roles