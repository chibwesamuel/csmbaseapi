from sqlalchemy.orm import Session

from app.repositories.user_role import (
    assign_role_to_user,
    remove_role_from_user,
    get_user_roles,
)

from app.repositories.user import get_user_by_id
from app.repositories.role import get_role_by_id


def assign_user_role(
    db: Session,
    user_id,
    role_id,
):
    user = get_user_by_id(
        db,
        user_id,
    )

    if not user:
        return None

    role = get_role_by_id(
        db,
        role_id,
    )

    if not role:
        return None

    return assign_role_to_user(
        db,
        user,
        role,
    )


def remove_user_role(
    db: Session,
    user_id,
    role_id,
):
    user = get_user_by_id(
        db,
        user_id,
    )

    if not user:
        return None

    role = get_role_by_id(
        db,
        role_id,
    )

    if not role:
        return None

    return remove_role_from_user(
        db,
        user,
        role,
    )


def list_user_roles(
    db: Session,
    user_id,
):
    user = get_user_by_id(
        db,
        user_id,
    )

    if not user:
        return None

    return get_user_roles(
        db,
        user,
    )