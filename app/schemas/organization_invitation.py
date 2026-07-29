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
    Schema for accepting an invitation.
    """

    token: str


class OrganizationInvitationResponse(
    BaseModel
):
    """
    Schema returned for organization invitations.
    """

    id: UUID

    organization_id: UUID

    role_id: UUID

    invited_by: UUID

    email: EmailStr

    token: str

    status: InvitationStatus

    expires_at: datetime

    accepted_at: datetime | None = None

    created_at: datetime


    model_config = ConfigDict(
        from_attributes=True
    )