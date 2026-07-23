from sqlalchemy.orm import Session

from app.models.user import User
from app.models.role import Role


def assign_role_to_user(
    db: Session,
    user: User,
    role: Role,
) -> User:
    """
    Assign a role to a user.
    """

    user.roles.append(role)

    db.commit()
    db.refresh(user)

    return user


def remove_role_from_user(
    db: Session,
    user: User,
    role: Role,
) -> User:
    """
    Remove a role from a user.
    """

    user.roles.remove(role)

    db.commit()
    db.refresh(user)

    return user


def get_user_roles(
    user: User,
) -> list[Role]:
    """
    Retrieve all roles assigned to a user.
    """

    return user.roles


def get_role_users(
    role: Role,
) -> list[User]:
    """
    Retrieve all users assigned to a role.
    """

    return role.users