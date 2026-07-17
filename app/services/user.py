from sqlalchemy.orm import Session

from app.repositories.user import (
    get_all_users,
    get_user_by_id,
    get_user_by_email,
    update_user as update_user_repository,
    update_user_status,
    delete_user as delete_user_repository,
)

from app.schemas.user import UserUpdate
from app.core.exceptions import EmailAlreadyRegistered


def list_users(
    db: Session,
):
    return get_all_users(db)


def get_user(
    db: Session,
    user_id: str,
):
    return get_user_by_id(
        db,
        user_id,
    )


def update_user(
    db: Session,
    user_id: str,
    user_data: UserUpdate,
):
    """
    Update an existing user.
    """

    user = get_user(
        db,
        user_id,
    )

    if not user:
        return None

    # Prevent duplicate email
    if (
        user_data.email
        and user_data.email != user.email
    ):
        existing_user = get_user_by_email(
            db,
            user_data.email,
        )

        if existing_user:
            raise EmailAlreadyRegistered()

    return update_user_repository(
        db,
        user,
        user_data,
    )

def change_user_status(
    db: Session,
    user_id: str,
    is_active: bool,
):
    """
    Activate or deactivate a user account.
    """

    user = get_user(
        db,
        user_id,
    )

    if not user:
        return None

    return update_user_status(
        db,
        user,
        is_active,
    )

def delete_user(
    db: Session,
    user_id: str,
):
    """
    Delete an existing user.
    """

    user = get_user(
        db,
        user_id,
    )

    if not user:
        return None

    return delete_user_repository(
        db,
        user,
    )