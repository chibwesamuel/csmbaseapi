from uuid import UUID

from sqlalchemy.orm import Session

from app.models.organization_member import OrganizationMember


def get_members(
    db: Session,
    organization_id: UUID,
    skip: int = 0,
    limit: int = 10,
):
    """
    Retrieve organization members.
    """

    return (
        db.query(OrganizationMember)
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
):
    """
    Count organization members.
    """

    return (
        db.query(OrganizationMember)
        .filter(
            OrganizationMember.organization_id == organization_id
        )
        .count()
    )


def get_member(
    db: Session,
    organization_id: UUID,
    user_id: UUID,
):
    """
    Retrieve a specific organization membership.
    """

    return (
        db.query(OrganizationMember)
        .filter(
            OrganizationMember.organization_id == organization_id,
            OrganizationMember.user_id == user_id,
        )
        .first()
    )


def create_member(
    db: Session,
    organization_id: UUID,
    user_id: UUID,
    role: str = "member",
):
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
):
    """
    Update a member role.
    """

    member.role = role

    db.commit()
    db.refresh(member)

    return member


def delete_member(
    db: Session,
    member: OrganizationMember,
):
    """
    Remove a member from an organization.
    """

    db.delete(member)
    db.commit()

    return True