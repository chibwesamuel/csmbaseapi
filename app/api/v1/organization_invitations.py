# app/api/v1/organization_invitations.py

from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.database.session import get_db

from app.dependencies.organization import (
    require_organization_admin,
)

from app.dependencies.auth import (
    get_current_user,
)

from app.models.user import User

from app.schemas.organization_invitation import (
    OrganizationInvitationCreate,
    OrganizationInvitationAccept,
    OrganizationInvitationResponse,
    PaginatedOrganizationInvitationsResponse,
)

from app.services.organization_invitation import (
    create_organization_invitation,
    get_invitation,
    accept_invitation,
    cancel_invitation,
)

from app.repositories.organization_invitation import (
    get_organization_invitations,
    count_organization_invitations,
)


router = APIRouter(
    prefix="/organizations",
    tags=["Organization Invitations"],
)


@router.post(
    "/{organization_id}/invitations",
    response_model=OrganizationInvitationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_invitation(
    organization_id: UUID,
    invitation_data: OrganizationInvitationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    membership=Depends(require_organization_admin),
):
    """
    Create an organization invitation.

    Requires organization owner/admin privileges.
    """

    try:
        return create_organization_invitation(
            db,
            organization_id,
            invitation_data.role_id,
            invitation_data.email,
            current_user.id,
        )

    except ValueError as error:

        message = str(error)

        if message == (
            "A pending invitation already exists for this email"
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=message,
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )


@router.get(
    "/{organization_id}/invitations",
    response_model=PaginatedOrganizationInvitationsResponse,
)
def list_organization_invitations(
    organization_id: UUID,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    membership=Depends(require_organization_admin),
):
    """
    List invitations for an organization.

    Requires organization owner/admin privileges.
    """

    invitations = get_organization_invitations(
        db,
        organization_id,
        skip,
        limit,
    )

    total = count_organization_invitations(
        db,
        organization_id,
    )

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "invitations": invitations,
    }


@router.get(
    "/invitations/{token}",
    response_model=OrganizationInvitationResponse,
)
def retrieve_invitation(
    token: str,
    db: Session = Depends(get_db),
):
    """
    Retrieve invitation using token.
    """

    try:
        return get_invitation(
            db,
            token,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


@router.post(
    "/invitations/accept",
)
def accept_organization_invitation(
    invitation_data: OrganizationInvitationAccept,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Accept an organization invitation.
    """

    try:

        membership = accept_invitation(
            db,
            invitation_data.token,
            current_user.id,
        )

        return {
            "message": "Invitation accepted successfully",
            "organization_id": membership.organization_id,
        }

    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.delete(
    "/{organization_id}/invitations/{invitation_id}",
)
def delete_organization_invitation(
    organization_id: UUID,
    invitation_id: UUID,
    db: Session = Depends(get_db),
    membership=Depends(require_organization_admin),
):
    """
    Cancel an organization invitation.

    Requires organization owner/admin privileges.
    """

    try:

        cancel_invitation(
            db,
            invitation_id,
        )

        return {
            "message": "Invitation cancelled successfully"
        }

    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )