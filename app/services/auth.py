from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    verify_password,
)

from app.repositories.user import (
    create_user,
    get_user_by_email,
)

from app.schemas.user import UserCreate
from app.core.exceptions import email_already_registered


def register_user(
    db: Session,
    user_data: UserCreate,
):

    existing_user = get_user_by_email(
        db,
        user_data.email,
    )

    if existing_user:
        email_already_registered()

    hashed_password = hash_password(
        user_data.password
    )

    return create_user(
        db=db,
        user_data=user_data,
        hashed_password=hashed_password,
    )


def authenticate_user(
    db: Session,
    email: str,
    password: str,
):

    user = get_user_by_email(
        db,
        email,
    )

    if not user:
        return None

    if not verify_password(
        password,
        user.hashed_password,
    ):
        return None

    return user