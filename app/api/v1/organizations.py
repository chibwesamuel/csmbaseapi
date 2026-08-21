from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.database.session import get_db

from app.dependencies.auth import get_current_user

from app.dependencies.permissions import (
    require_permission,
)

from app.dependencies.organization_permissions import (
    require_organization_admin,
    require_organization_owner,
    require_organization_member,
)

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

from app.services.organization_cache import (
    cache_organization,
    get_cached_organization,
)


router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
)


# =========================================================
# MY ORGANIZATIONS
# =========================================================

@router.get(
    "/my",
    response_model=list[OrganizationResponse],
)
def read_my_organizations(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    """
    Retrieve all organizations belonging to
    the authenticated user.
    """

    return get_my_organizations(
        db,
        current_user.id,
    )


# =========================================================
# LIST ALL ORGANIZATIONS
# =========================================================

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
        require_permission(
            "organizations.view"
        )
    ),
):
    """
    Retrieve a paginated list of organizations.

    Requires the global:
        organizations.view

    permission.
    """

    return list_organizations(
        db,
        skip,
        limit,
        search,
    )


# =========================================================
# GET SINGLE ORGANIZATION
# =========================================================

@router.get(
    "/{organization_id}",
    response_model=OrganizationResponse,
)
def read_organization(
    organization_id: UUID,
    db: Session = Depends(get_db),
    membership=Depends(
        require_organization_member
    ),
):
    """
    Retrieve a single organization.

    The authenticated user must be a member
    of the requested organization.

    Authorization is always verified before
    consulting the response cache.
    """

    cached = get_cached_organization(
        organization_id
    )

    if cached is not None:
        return cached

    organization = get_organization(
        db,
        organization_id,
    )

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    response = OrganizationResponse.model_validate(
        organization
    )

    data = response.model_dump(
        mode="json"
    )

    cache_organization(
        organization_id,
        data,
    )

    return response


# =========================================================
# CREATE ORGANIZATION
# =========================================================

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

    The authenticated user automatically
    becomes the organization owner.
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


# =========================================================
# UPDATE ORGANIZATION
# =========================================================

@router.put(
    "/{organization_id}",
    response_model=OrganizationResponse,
)
def update_organization(
    organization_id: UUID,
    organization_data: OrganizationUpdate,
    db: Session = Depends(get_db),
    membership=Depends(
        require_organization_admin
    ),
):
    """
    Update an organization.

    The authenticated user must be either:
    - the organization owner
    - an organization admin
    """

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


# =========================================================
# DELETE ORGANIZATION
# =========================================================

@router.delete(
    "/{organization_id}",
)
def delete_organization(
    organization_id: UUID,
    db: Session = Depends(get_db),
    membership=Depends(
        require_organization_owner
    ),
):
    """
    Delete an organization.

    Only the organization owner can
    delete the organization.
    """

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