from uuid import UUID

from sqlalchemy.orm import Session

from app.core.enums import OrganizationRole

from app.models.organization import Organization
from app.models.organization_member import OrganizationMember

from app.repositories.organization import (
    get_organization_by_id,
)

from app.repositories.user import (
    get_user_by_id,
)

from app.repositories.organization_member import (
    get_members,
    count_members,
    count_owners,
    get_member,
    create_member,
    update_member_role,
    delete_member,
    get_user_organizations,
)

from app.schemas.organization_member import (
    PaginatedOrganizationMembersResponse,
)


def list_members(
    db: Session,
    organization_id: UUID,
    skip: int = 0,
    limit: int = 10,
) -> PaginatedOrganizationMembersResponse:
    """
    Retrieve paginated members of an organization.
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
    role: OrganizationRole | str = OrganizationRole.MEMBER,
) -> OrganizationMember:
    """
    Add a user to an organization.
    """

    organization = get_organization_by_id(
        db,
        organization_id,
    )

    if organization is None:
        raise ValueError(
            "Organization not found"
        )

    user = get_user_by_id(
        db,
        user_id,
    )

    if user is None:
        raise ValueError(
            "User not found"
        )

    existing_member = get_member(
        db,
        organization_id,
        user_id,
    )

    if existing_member is not None:
        raise ValueError(
            "User is already a member of this organization"
        )

    role_value = (
        role.value
        if isinstance(role, OrganizationRole)
        else role
    )

    return create_member(
        db,
        organization_id,
        user_id,
        role_value,
    )


def change_member_role(
    db: Session,
    organization_id: UUID,
    user_id: UUID,
    role: OrganizationRole | str,
) -> OrganizationMember:
    """
    Change a member's role.
    """

    member = get_member(
        db,
        organization_id,
        user_id,
    )

    if member is None:
        raise ValueError(
            "Membership not found"
        )

    role_value = (
        role.value
        if isinstance(role, OrganizationRole)
        else role
    )

    if (
        member.role == OrganizationRole.OWNER.value
        and role_value != OrganizationRole.OWNER.value
    ):
        owner_count = count_owners(
            db,
            organization_id,
        )

        if owner_count == 1:
            raise ValueError(
                "An organization must have at least one owner"
            )

    return update_member_role(
        db,
        member,
        role_value,
    )


def remove_member(
    db: Session,
    organization_id: UUID,
    user_id: UUID,
) -> bool:
    """
    Remove a user from an organization.
    """

    member = get_member(
        db,
        organization_id,
        user_id,
    )

    if member is None:
        raise ValueError(
            "Membership not found"
        )

    if member.role == OrganizationRole.OWNER.value:

        owner_count = count_owners(
            db,
            organization_id,
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
) -> list[Organization]:
    """
    Retrieve all organizations the user belongs to.
    """

    return get_user_organizations(
        db,
        user_id,
    )