from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.core.enums import OrganizationRole


class OrganizationMemberCreate(BaseModel):
    """
    Data required to add a user to an organization.
    """

    user_id: UUID
    role: OrganizationRole = OrganizationRole.MEMBER


class OrganizationMemberUpdate(BaseModel):
    """
    Data used to update an organization membership.
    """

    role: OrganizationRole | None = None


class OrganizationMemberUserResponse(BaseModel):
    """
    Basic user information returned with organization membership.
    """

    id: UUID
    username: str
    email: str

    model_config = ConfigDict(
        from_attributes=True
    )


class OrganizationMemberResponse(BaseModel):
    """
    Organization membership data returned to clients.
    """

    id: UUID

    organization_id: UUID
    user_id: UUID

    user: OrganizationMemberUserResponse

    role: str

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class PaginatedOrganizationMembersResponse(BaseModel):
    """
    Paginated organization member response.
    """

    total: int
    skip: int
    limit: int

    members: list[OrganizationMemberResponse]

    model_config = ConfigDict(
        from_attributes=True
    )