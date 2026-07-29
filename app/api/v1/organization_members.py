from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.database.session import get_db

from app.dependencies.permissions import require_permission
from app.dependencies.organization import get_current_organization

from app.models.organization import Organization
from app.models.user import User

from app.schemas.organization_member import (
    OrganizationMemberCreate,
    OrganizationMemberUpdate,
    OrganizationMemberResponse,
    PaginatedOrganizationMembersResponse,
)

from app.services.organization_member import (
    list_members,
    add_member,
    change_member_role,
    remove_member,
)


router = APIRouter(
    prefix="/organizations",
    tags=["Organization Members"],
)


@router.get(
    "/{organization_id}/members",
    response_model=PaginatedOrganizationMembersResponse,
)
def get_organization_members(
    organization_id: UUID,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    organization=Depends(get_current_organization),
    current_user: User = Depends(
        require_permission("organizations.members.view")
    ),
):
    """
    List all members belonging to an organization.
    """

    return list_members(
        db,
        organization_id,
        skip,
        limit,
    )


@router.post(
    "/{organization_id}/members",
    response_model=OrganizationMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_organization_member(
    organization_id: UUID,
    member_data: OrganizationMemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("organizations.members.create")
    ),
):
    """
    Add a user to an organization.
    """

    organization = (
        db.query(Organization)
        .filter(
            Organization.id == organization_id
        )
        .first()
    )

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    try:
        return add_member(
            db,
            organization_id,
            member_data.user_id,
            member_data.role,
        )

    except ValueError as error:

        message = str(error)

        if message == "User not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            )

        if message == "User is already a member of this organization":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=message,
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )


@router.patch(
    "/{organization_id}/members/{user_id}",
    response_model=OrganizationMemberResponse,
)
def update_organization_member(
    organization_id: UUID,
    user_id: UUID,
    member_data: OrganizationMemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("organizations.members.update")
    ),
):
    """
    Update an organization member's role.
    """

    try:
        return change_member_role(
            db,
            organization_id,
            user_id,
            member_data.role,
        )

    except ValueError as error:

        message = str(error)

        if message == "Membership not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )


@router.delete(
    "/{organization_id}/members/{user_id}",
)
def delete_organization_member(
    organization_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("organizations.members.delete")
    ),
):
    """
    Remove a user from an organization.
    """

    try:

        remove_member(
            db,
            organization_id,
            user_id,
        )

        return {
            "message": "Member removed successfully"
        }

    except ValueError as error:

        message = str(error)

        if message == "Membership not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )