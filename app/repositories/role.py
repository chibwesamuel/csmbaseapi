from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.role import Role
from app.schemas.role import RoleCreate, RoleUpdate


def get_role_by_id(
    db: Session,
    role_id,
):
    return (
        db.query(Role)
        .filter(Role.id == role_id)
        .first()
    )


def get_role_by_name(
    db: Session,
    name: str,
):
    return (
        db.query(Role)
        .filter(Role.name == name)
        .first()
    )


def get_roles(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    search: str | None = None,
):
    query = db.query(Role)

    if search:
        term = f"%{search}%"

        query = query.filter(
            or_(
                Role.name.ilike(term),
                Role.description.ilike(term),
            )
        )

    return (
        query
        .offset(skip)
        .limit(limit)
        .all()
    )


def count_roles(
    db: Session,
    search: str | None = None,
):
    query = db.query(Role)

    if search:
        term = f"%{search}%"

        query = query.filter(
            or_(
                Role.name.ilike(term),
                Role.description.ilike(term),
            )
        )

    return query.count()


def create_role(
    db: Session,
    role_data: RoleCreate,
):
    role = Role(
        name=role_data.name,
        description=role_data.description,
    )

    db.add(role)
    db.commit()
    db.refresh(role)

    return role


def update_role(
    db: Session,
    role: Role,
    role_data: RoleUpdate,
):
    update_data = role_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(
            role,
            field,
            value,
        )

    db.commit()
    db.refresh(role)

    return role


def delete_role(
    db: Session,
    role: Role,
):
    db.delete(role)
    db.commit()

    return True