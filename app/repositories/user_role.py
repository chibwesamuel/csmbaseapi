from sqlalchemy.orm import Session

from app.models.user import User
from app.models.role import Role


def assign_role_to_user(
    db: Session,
    user: User,
    role: Role,
):
    if role not in user.roles:
        user.roles.append(role)

        db.commit()
        db.refresh(user)

    return user


def remove_role_from_user(
    db: Session,
    user: User,
    role: Role,
):
    if role in user.roles:
        user.roles.remove(role)

        db.commit()
        db.refresh(user)

    return user


def get_user_roles(
    db: Session,
    user: User,
):
    return user.roles


def get_role_users(
    db: Session,
    role: Role,
):
    return role.users