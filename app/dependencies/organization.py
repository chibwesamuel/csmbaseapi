from uuid import UUID

from fastapi import (
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.database.session import get_db

from app.dependencies.auth import get_current_user

from app.models.user import User
from app.models.organization import Organization
from app.models.organization_member import OrganizationMember
from app.models.project import Project


def get_current_organization(
    organization_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Organization:
    """
    Retrieve the requested organization and verify
    that the current user belongs to it.

    Order of checks:
    1. Organization must exist.
    2. User must belong to the organization.
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

    return organization


def get_current_project(
    project_id: UUID,
    organization: Organization = Depends(
        get_current_organization
    ),
    db: Session = Depends(get_db),
) -> Project:
    """
    Retrieve the requested project and verify that
    it belongs to the current organization.

    Order of checks:
    1. Organization must exist and current user must belong to it.
    2. Project must exist within that organization.
    """

    project = (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.organization_id == organization.id,
        )
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return project