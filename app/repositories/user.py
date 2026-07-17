from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserUpdate,
)


def get_user_by_email(
    db: Session,
    email: str,
) -> User | None:
    return (
        db.query(User)
        .filter(User.email == email)
        .first()
    )


def get_user_by_username(
    db: Session,
    username: str,
) -> User | None:
    return (
        db.query(User)
        .filter(User.username == username)
        .first()
    )


def get_all_users(
    db: Session,
):
    return db.query(User).all()


def get_user_by_id(
    db: Session,
    user_id,
):
    return (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )


def create_user(
    db: Session,
    user_data: UserCreate,
    hashed_password: str,
) -> User:

    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def update_user(
    db: Session,
    user: User,
    user_data: UserUpdate,
) -> User:
    """
    Update an existing user.
    """

    update_data = user_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(
            user,
            field,
            value,
        )

    db.commit()
    db.refresh(user)

    return user


def update_user_status(
    db: Session,
    user: User,
    is_active: bool,
):
    """
    Update user active status.
    """

    user.is_active = is_active

    db.commit()
    db.refresh(user)

    return user

def delete_user(
    db: Session,
    user: User,
):
    """
    Delete a user from the database.
    """

    db.delete(user)
    db.commit()

    return True