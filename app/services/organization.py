from uuid import UUID

from sqlalchemy.orm import Session

from app.models.organization_member import OrganizationMember
from app.models.user import User
from app.models.role import Role

from app.repositories.organization import (
    count_organizations,
    create_organization as create_repository,
    delete_organization as delete_repository,
    get_organization_by_email,
    get_organization_by_id,
    get_organization_by_slug,
    get_organizations,
    update_organization as update_repository,
)

from app.repositories.organization_member import (
    get_user_organizations,
)

from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    PaginatedOrganizationsResponse,
)

from app.services.organization_cache import (
    invalidate_organization_cache,
)


def get_role_by_name(
    db: Session,
    role_name: str,
) -> Role | None:
    """
    Retrieve a role by name.

    Handles different casing:
    owner / Owner / OWNER
    """

    return (
        db.query(Role)
        .filter(
            Role.name.ilike(role_name)
        )
        .first()
    )


def list_organizations(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    search: str | None = None,
    sort_by: str | None = None,
    sort_order: str = "asc",
):
    organizations = get_organizations(
        db,
        skip,
        limit,
        search,
    )

    total = count_organizations(
        db,
        search,
    )

    return PaginatedOrganizationsResponse(
        total=total,
        skip=skip,
        limit=limit,
        organizations=organizations,
    )


def get_organization(
    db: Session,
    organization_id: UUID,
):
    return get_organization_by_id(
        db,
        organization_id,
    )


def create_new_organization(
    db: Session,
    organization_data: OrganizationCreate,
    current_user: User,
):
    """
    Create an organization and assign
    the creator as the owner.
    """

    existing_slug = get_organization_by_slug(
        db,
        organization_data.slug,
    )

    if existing_slug:
        return "slug_exists"

    if organization_data.email:

        existing_email = get_organization_by_email(
            db,
            organization_data.email,
        )

        if existing_email:
            return "email_exists"

    organization = create_repository(
        db,
        organization_data,
    )

    owner_role = get_role_by_name(
        db,
        "owner",
    )

    if not owner_role:
        db.rollback()

        raise ValueError(
            "Owner role not found"
        )

    membership = OrganizationMember(
        organization_id=organization.id,
        user_id=current_user.id,
        role_id=owner_role.id,
    )

    db.add(membership)

    db.commit()
    db.refresh(organization)

    return organization


def update_existing_organization(
    db: Session,
    organization_id: UUID,
    organization_data: OrganizationUpdate,
):
    organization = get_organization_by_id(
        db,
        organization_id,
    )

    if not organization:
        return None

    organization = update_repository(
        db,
        organization,
        organization_data,
    )

    invalidate_organization_cache(
        organization_id
    )

    return organization


def delete_existing_organization(
    db: Session,
    organization_id: UUID,
):
    organization = get_organization_by_id(
        db,
        organization_id,
    )

    if not organization:
        return False

    deleted = delete_repository(
        db,
        organization,
    )

    invalidate_organization_cache(
        organization_id
    )

    return deleted


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