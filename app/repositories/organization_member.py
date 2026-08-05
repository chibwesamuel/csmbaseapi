from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from app.models.organization import Organization
from app.models.organization_member import OrganizationMember
from app.models.role import Role


def member_query(db: Session):
    """
    Base query with required relationships loaded.
    """

    return (
        db.query(OrganizationMember)
        .options(
            joinedload(
                OrganizationMember.user
            ),
            joinedload(
                OrganizationMember.role
            ),
        )
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
        member_query(db)
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
    Count members in an organization.
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
    Count organization owners using the Role table.
    """

    return (
        db.query(OrganizationMember)
        .join(
            Role,
            OrganizationMember.role_id == Role.id,
        )
        .filter(
            OrganizationMember.organization_id == organization_id,
            Role.name == "owner",
        )
        .count()
    )


def get_member(
    db: Session,
    organization_id: UUID,
    user_id: UUID,
) -> OrganizationMember | None:
    """
    Retrieve membership by organization and user.
    """

    return (
        member_query(db)
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
    Retrieve membership by id.
    """

    return (
        member_query(db)
        .options(
            joinedload(
                OrganizationMember.organization
            ),
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
    role_id: UUID,
) -> OrganizationMember:
    """
    Add a user to an organization.
    """

    member = OrganizationMember(
        organization_id=organization_id,
        user_id=user_id,
        role_id=role_id,
    )

    db.add(member)
    db.commit()

    return get_member(
        db,
        organization_id,
        user_id,
    )


def update_member_role(
    db: Session,
    member: OrganizationMember,
    role_id: UUID,
) -> OrganizationMember:
    """
    Update organization member role.
    """

    member.role_id = role_id

    db.commit()

    return get_member(
        db,
        member.organization_id,
        member.user_id,
    )


def delete_member(
    db: Session,
    member: OrganizationMember,
) -> bool:
    """
    Remove a user from an organization.
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
    Retrieve all memberships for a user.
    """

    return (
        member_query(db)
        .options(
            joinedload(
                OrganizationMember.organization
            ),
        )
        .filter(
            OrganizationMember.user_id == user_id
        )
        .all()
    )