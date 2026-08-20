from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db

from app.dependencies.auth import get_current_user
from app.dependencies.organization import get_current_organization

from app.models.user import User
from app.models.organization import Organization
from app.models.organization_member import OrganizationMember


def get_membership(
    organization: Organization = Depends(
        get_current_organization
    ),
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    """
    Retrieve the current user's membership in
    the current organization.
    """

    membership = (
        db.query(OrganizationMember)
        .filter(
            OrganizationMember.organization_id == organization.id,
            OrganizationMember.user_id == current_user.id,
        )
        .first()
    )

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization membership required",
        )

    return membership


def require_organization_owner(
    membership: OrganizationMember = Depends(
        get_membership
    ),
):
    """
    Require organization owner privileges.
    """

    if membership.role.name != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization owner privileges required",
        )

    return membership


def require_organization_admin(
    membership: OrganizationMember = Depends(
        get_membership
    ),
):
    """
    Require organization administrator privileges.

    Organization owners are also administrators.
    """

    if membership.role.name not in (
        "owner",
        "admin",
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization admin privileges required",
        )

    return membership


def require_organization_member(
    membership: OrganizationMember = Depends(
        get_membership
    ),
):
    """
    Require any membership in the organization.
    """

    return membership