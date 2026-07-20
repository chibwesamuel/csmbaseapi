from uuid import UUID

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.organization import Organization

from app.repositories.organization_member import (
    get_members,
    get_member,
    create_member,
    update_member_role,
    delete_member,
)


VALID_MEMBER_ROLES = {
    "owner",
    "admin",
    "member",
}


def list_members(
    db: Session,
    organization_id: UUID,
):
    """
    List all members of an organization.
    """

    return get_members(
        db,
        organization_id,
    )


def add_member(
    db: Session,
    organization_id: UUID,
    user_id: UUID,
    role: str = "member",
):
    """
    Add a user to an organization.
    """

    organization = (
        db.query(Organization)
        .filter(
            Organization.id == organization_id
        )
        .first()
    )

    if not organization:
        raise ValueError(
            "Organization not found"
        )


    user = (
        db.query(User)
        .filter(
            User.id == user_id
        )
        .first()
    )

    if not user:
        raise ValueError(
            "User not found"
        )


    if role not in VALID_MEMBER_ROLES:
        raise ValueError(
            "Invalid membership role"
        )


    existing_member = get_member(
        db,
        organization_id,
        user_id,
    )

    if existing_member:
        raise ValueError(
            "User is already a member of this organization"
        )


    return create_member(
        db,
        organization_id,
        user_id,
        role,
    )


def change_member_role(
    db: Session,
    organization_id: UUID,
    user_id: UUID,
    role: str,
):
    """
    Change a member's role.
    """

    if role not in VALID_MEMBER_ROLES:
        raise ValueError(
            "Invalid membership role"
        )


    member = get_member(
        db,
        organization_id,
        user_id,
    )

    if not member:
        raise ValueError(
            "Membership not found"
        )


    return update_member_role(
        db,
        member,
        role,
    )


def remove_member(
    db: Session,
    organization_id: UUID,
    user_id: UUID,
):
    """
    Remove a user from an organization.
    """

    member = get_member(
        db,
        organization_id,
        user_id,
    )

    if not member:
        raise ValueError(
            "Membership not found"
        )


    return delete_member(
        db,
        member,
    )