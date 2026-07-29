from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    EmailStr,
    ConfigDict,
)

from app.models.organization_invitation import (
    InvitationStatus,
)


class OrganizationInvitationCreate(
    BaseModel
):
    """
    Schema for creating an organization invitation.
    """

    email: EmailStr
    role_id: UUID


class OrganizationInvitationAccept(
    BaseModel
):
    """
    Schema used when accepting an invitation.
    """

    token: str


class OrganizationInvitationBase(
    BaseModel
):
    """
    Shared fields for organization invitations.
    """

    email: EmailStr

    role_id: UUID


class OrganizationInvitationResponse(
    OrganizationInvitationBase
):
    """
    Response schema for organization invitations.
    """

    id: UUID

    organization_id: UUID

    invited_by: UUID

    token: str

    status: InvitationStatus

    expires_at: datetime

    accepted_at: datetime | None = None

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class PaginatedOrganizationInvitationsResponse(
    BaseModel
):
    """
    Paginated organization invitation response.
    """

    total: int

    skip: int

    limit: int

    invitations: list[
        OrganizationInvitationResponse
    ]