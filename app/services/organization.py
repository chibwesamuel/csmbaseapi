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
):

    existing = get_organization_by_slug(
        db,
        organization_data.slug,
    )

    if existing:
        return None

    return create_repository(
        db,
        organization_data,
    )


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