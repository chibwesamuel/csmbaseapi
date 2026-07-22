from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from app.models.organization import Organization
from app.models.organization_member import (
    OrganizationMember,
    MEMBER,
    OWNER,
)


def get_members(
    db: Session,
    organization_id: UUID,
    skip: int = 0,
    limit: int = 10,
) -> list[OrganizationMember]:
    """
    Retrieve members belonging to an organization.
    """

    return (
        db.query(OrganizationMember)
        .options(
            joinedload(OrganizationMember.user)
        )
        .filter(
            OrganizationMember.organization_id == organization_id
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


def count_members(
    db: Session,
    organization_id: UUID,
) -> int:
    """
    Count the number of members in an organization.
    """

    return (
        db.query(OrganizationMember)
        .filter(
            OrganizationMember.organization_id == organization_id
        )
        .count()
    )


def count_owners(
    db: Session,
    organization_id: UUID,
) -> int:
    """
    Count the number of owners in an organization.
    """

    return (
        db.query(OrganizationMember)
        .filter(
            OrganizationMember.organization_id == organization_id,
            OrganizationMember.role == OWNER,
        )
        .count()
    )


def get_member(
    db: Session,
    organization_id: UUID,
    user_id: UUID,
) -> OrganizationMember | None:
    """
    Retrieve a membership by organization and user.
    """

    return (
        db.query(OrganizationMember)
        .options(
            joinedload(OrganizationMember.user)
        )
        .filter(
            OrganizationMember.organization_id == organization_id,
            OrganizationMember.user_id == user_id,
        )
        .first()
    )


def get_member_by_id(
    db: Session,
    member_id: UUID,
) -> OrganizationMember | None:
    """
    Retrieve a membership by its primary key.
    """

    return (
        db.query(OrganizationMember)
        .options(
            joinedload(OrganizationMember.user),
            joinedload(OrganizationMember.organization),
        )
        .filter(
            OrganizationMember.id == member_id
        )
        .first()
    )


def create_member(
    db: Session,
    organization_id: UUID,
    user_id: UUID,
    role: str = MEMBER,
) -> OrganizationMember:
    """
    Add a user to an organization.
    """

    member = OrganizationMember(
        organization_id=organization_id,
        user_id=user_id,
        role=role,
    )

    db.add(member)
    db.commit()
    db.refresh(member)

    return member


def update_member_role(
    db: Session,
    member: OrganizationMember,
    role: str,
) -> OrganizationMember:
    """
    Update a member's role.
    """

    member.role = role

    db.commit()
    db.refresh(member)

    return member


def delete_member(
    db: Session,
    member: OrganizationMember,
) -> bool:
    """
    Remove a member from an organization.
    """

    db.delete(member)
    db.commit()

    return True


def get_user_organizations(
    db: Session,
    user_id: UUID,
) -> list[Organization]:
    """
    Retrieve all organizations a user belongs to.
    """

    return (
        db.query(Organization)
        .join(
            OrganizationMember,
            Organization.id == OrganizationMember.organization_id,
        )
        .filter(
            OrganizationMember.user_id == user_id
        )
        .all()
    )


def get_user_memberships(
    db: Session,
    user_id: UUID,
) -> list[OrganizationMember]:
    """
    Retrieve all membership records for a user.
    """

    return (
        db.query(OrganizationMember)
        .options(
            joinedload(OrganizationMember.organization)
        )
        .filter(
            OrganizationMember.user_id == user_id
        )
        .all()
    )