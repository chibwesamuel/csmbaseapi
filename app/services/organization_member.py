from uuid import UUID

from sqlalchemy.orm import Session

from app.core.enums import OrganizationRole

from app.repositories.organization import (
    get_organization_by_id,
)

from app.repositories.user import (
    get_user_by_id,
)

from app.repositories.organization_member import (
    get_members,
    count_members,
    get_member,
    create_member,
    update_member_role,
    delete_member,
    get_user_organizations,
)

from app.models.organization_member import OrganizationMember

from app.schemas.organization_member import (
    PaginatedOrganizationMembersResponse,
)


def list_members(
    db: Session,
    organization_id: UUID,
    skip: int = 0,
    limit: int = 10,
):
    """
    List organization members.
    """

    members = get_members(
        db,
        organization_id,
        skip,
        limit,
    )

    total = count_members(
        db,
        organization_id,
    )

    return PaginatedOrganizationMembersResponse(
        total=total,
        skip=skip,
        limit=limit,
        members=members,
    )


def add_member(
    db: Session,
    organization_id: UUID,
    user_id: UUID,
    role: OrganizationRole = OrganizationRole.MEMBER,
):
    """
    Add a user to an organization.
    """

    organization = get_organization_by_id(
        db,
        organization_id,
    )

    if not organization:
        raise ValueError(
            "Organization not found"
        )

    user = get_user_by_id(
        db,
        user_id,
    )

    if not user:
        raise ValueError(
            "User not found"
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
        role.value,
    )


def change_member_role(
    db: Session,
    organization_id: UUID,
    user_id: UUID,
    role: OrganizationRole,
):
    """
    Change a member's role.
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


    if (
        member.role == OrganizationRole.OWNER.value
        and role != OrganizationRole.OWNER
    ):

        owner_count = (
            db.query(OrganizationMember)
            .filter(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.role == OrganizationRole.OWNER.value,
            )
            .count()
        )

        if owner_count == 1:
            raise ValueError(
                "An organization must have at least one owner"
            )


    return update_member_role(
        db,
        member,
        role.value,
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


    if member.role == OrganizationRole.OWNER.value:

        owner_count = (
            db.query(OrganizationMember)
            .filter(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.role == OrganizationRole.OWNER.value,
            )
            .count()
        )

        if owner_count == 1:
            raise ValueError(
                "Cannot remove the last owner of an organization"
            )


    return delete_member(
        db,
        member,
    )

def get_my_organizations(
    db: Session,
    user_id: UUID,
):
    """
    Retrieve organizations belonging to a user.
    """

    return get_user_organizations(
        db,
        user_id,
    )