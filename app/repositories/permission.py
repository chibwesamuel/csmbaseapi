from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.sorting import apply_sorting

from app.models.permission import Permission
from app.schemas.permission import (
    PermissionCreate,
    PermissionUpdate,
)


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


from app.core.sorting import apply_sorting


def get_permissions(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    search: str | None = None,
    sort_by: str | None = None,
    sort_order: str = "asc",
):
    """
    Return paginated permissions with
    optional search and sorting.
    """

    # Prevent invalid offsets
    if skip < 0:
        skip = 0

    # Prevent invalid limits
    if limit < 1:
        limit = 10

    if limit > 100:
        limit = 100

    query = db.query(Permission)

    # -----------------------------
    # Search
    # -----------------------------
    if search:
        term = f"%{search}%"

        query = query.filter(
            or_(
                Permission.name.ilike(term),
                Permission.description.ilike(term),
            )
        )

    # -----------------------------
    # Sorting
    # -----------------------------
    allowed_sort_fields = {
        "name": Permission.name,
        "description": Permission.description,
    }

    query = apply_sorting(
        query=query,
        sort_by=sort_by,
        sort_order=sort_order,
        allowed_fields=allowed_sort_fields,
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
    """
    Count permissions matching
    an optional search.
    """

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