from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db

from app.dependencies.auth import get_current_user
from app.dependencies.permissions import require_permission

from app.models.user import User

from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
    PaginatedOrganizationsResponse,
)

from app.services.organization import (
    list_organizations,
    get_organization,
    create_new_organization,
    update_existing_organization,
    delete_existing_organization,
    get_my_organizations,
)


router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
)

@router.get(
    "/my",
    response_model=list[OrganizationResponse],
)
def read_my_organizations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve organizations for the authenticated user.
    """

    return get_my_organizations(
        db,
        current_user.id,
    )

@router.get(
    "/",
    response_model=PaginatedOrganizationsResponse,
)
def read_organizations(
    skip: int = 0,
    limit: int = 10,
    search: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("organizations.view")
    ),
):

    return list_organizations(
        db,
        skip,
        limit,
        search,
    )


@router.get(
    "/{organization_id}",
    response_model=OrganizationResponse,
)
def read_organization(
    organization_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("organizations.view")
    ),
):

    organization = get_organization(
        db,
        organization_id,
    )

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    return organization


@router.post(
    "/",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_organization(
    organization_data: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    """
    Create a new organization.

    The authenticated user automatically becomes
    the organization owner.
    """

    organization = create_new_organization(
        db,
        organization_data,
        current_user,
    )

    if organization == "slug_exists":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Organization slug already exists",
        )

    if organization == "email_exists":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Organization email already exists",
        )

    return organization


@router.put(
    "/{organization_id}",
    response_model=OrganizationResponse,
)
def update_organization(
    organization_id: str,
    organization_data: OrganizationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("organizations.update")
    ),
):

    organization = update_existing_organization(
        db,
        organization_id,
        organization_data,
    )

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    return organization


@router.delete(
    "/{organization_id}",
)
def delete_organization(
    organization_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("organizations.delete")
    ),
):

    deleted = delete_existing_organization(
        db,
        organization_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    return {
        "message": "Organization deleted successfully"
    }