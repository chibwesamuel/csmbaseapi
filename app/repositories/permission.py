from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.permission import Permission
from app.schemas.permission import PermissionCreate, PermissionUpdate


def get_permission_by_id(
    db: Session,
    permission_id,
):
    return (
        db.query(Permission)
        .filter(Permission.id == permission_id)
        .first()
    )


def get_permission_by_name(
    db: Session,
    name: str,
):
    return (
        db.query(Permission)
        .filter(Permission.name == name)
        .first()
    )


def get_permissions(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    search: str | None = None,
):
    query = db.query(Permission)

    if search:
        term = f"%{search}%"

        query = query.filter(
            or_(
                Permission.name.ilike(term),
                Permission.description.ilike(term),
            )
        )

    return (
        query
        .offset(skip)
        .limit(limit)
        .all()
    )


def count_permissions(
    db: Session,
    search: str | None = None,
):
    query = db.query(Permission)

    if search:
        term = f"%{search}%"

        query = query.filter(
            or_(
                Permission.name.ilike(term),
                Permission.description.ilike(term),
            )
        )

    return query.count()


def create_permission(
    db: Session,
    permission_data: PermissionCreate,
):
    permission = Permission(
        name=permission_data.name,
        description=permission_data.description,
    )

    db.add(permission)
    db.commit()
    db.refresh(permission)

    return permission


def update_permission(
    db: Session,
    permission: Permission,
    permission_data: PermissionUpdate,
):
    update_data = permission_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(
            permission,
            field,
            value,
        )

    db.commit()
    db.refresh(permission)

    return permission


def delete_permission(
    db: Session,
    permission: Permission,
):
    db.delete(permission)
    db.commit()

    return True