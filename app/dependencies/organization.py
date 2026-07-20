from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user

from app.models.user import User
from app.models.organization import Organization
from app.models.organization_member import OrganizationMember



def get_current_organization(
    organization_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Organization:
    """
    Retrieve the organization from the request
    and verify the current user belongs to it.
    """

    membership = (
        db.query(OrganizationMember)
        .filter(
            OrganizationMember.organization_id == organization_id,
            OrganizationMember.user_id == current_user.id,
        )
        .first()
    )


    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not belong to this organization",
        )


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


    return organization