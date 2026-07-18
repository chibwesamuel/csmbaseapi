from sqlalchemy.orm import Session

from app.repositories.user import (
    get_all_users,
    get_user_by_id,
    get_user_by_email,
    update_user as update_user_repository,
    update_user_status,
    delete_user as delete_user_repository,
    get_user_by_username,
    create_user as create_user_repository,
)
from app.core.security import hash_password
from app.schemas.user import UserCreate

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

def create_user(
    db: Session,
    user_data: UserCreate,
):
    """
    Create a new user.
    """

    existing_email = get_user_by_email(
        db,
        user_data.email,
    )

    if existing_email:
        raise ValueError(
            "Email already registered"
        )


    existing_username = get_user_by_username(
        db,
        user_data.username,
    )

    if existing_username:
        raise ValueError(
            "Username already taken"
        )


    hashed_password = hash_password(
        user_data.password
    )


    return create_user_repository(
        db,
        user_data,
        hashed_password,
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