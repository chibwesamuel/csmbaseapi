from uuid import UUID

from sqlalchemy.orm import Session

from app.models.organization_member import OrganizationMember
from app.models.user import User

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

    Returns:
        Organization instance on success.
        "slug_exists" if the slug already exists.
        "email_exists" if the email already exists.
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

    membership = OrganizationMember(
        organization_id=organization.id,
        user_id=current_user.id,
        role="owner",
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

    return update_repository(
        db,
        organization,
        organization_data,
    )


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

    return delete_repository(
        db,
        organization,
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