from sqlalchemy.orm import Session

from app.repositories.user import (
    get_all_users,
    get_user_by_id,
)


def list_users(
    db: Session,
):
    return get_all_users(db)


def get_user(
    db: Session,
    user_id,
):
    return get_user_by_id(
        db,
        user_id,
    )