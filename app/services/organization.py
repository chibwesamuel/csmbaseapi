from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories.organization import (
    get_organizations,
    count_organizations,
    get_organization_by_id,
    get_organization_by_slug,
    create_organization as create_repository,
    update_organization as update_repository,
    delete_organization as delete_repository,
)

from app.repositories.organization_member import (
    get_user_organizations,
)

from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    PaginatedOrganizationsResponse,
)
from app.models.user import User
from app.models.organization_member import OrganizationMember


def list_organizations(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    search: str | None = None,
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
    organization_id,
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

    existing = get_organization_by_slug(
        db,
        organization_data.slug,
    )

    if existing:
        return None


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

    db.refresh(
        organization
    )


    return organization


def update_existing_organization(
    db: Session,
    organization_id,
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
    organization_id,
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