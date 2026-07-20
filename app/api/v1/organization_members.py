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

from app.models.user import User

from app.schemas.organization_member import (
    OrganizationMemberCreate,
    OrganizationMemberUpdate,
    OrganizationMemberResponse,
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
    response_model=list[OrganizationMemberResponse],
)
def get_organization_members(
    organization_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List members belonging to an organization.
    """

    return list_members(
        db,
        organization_id,
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
    current_user: User = Depends(get_current_user),
):
    """
    Add a user to an organization.
    """

    try:
        return add_member(
            db,
            organization_id,
            member_data.user_id,
            member_data.role,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
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
    current_user: User = Depends(get_current_user),
):
    """
    Update an organization member role.
    """

    try:
        return change_member_role(
            db,
            organization_id,
            user_id,
            member_data.role,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.delete(
    "/{organization_id}/members/{user_id}",
)
def delete_organization_member(
    organization_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )