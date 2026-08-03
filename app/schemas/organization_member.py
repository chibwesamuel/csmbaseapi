from datetime import datetime
from uuid import UUID

from typing import Literal

from pydantic import BaseModel, ConfigDict


OrganizationRoleType = Literal[
    "owner",
    "admin",
    "member",
]


class OrganizationMemberCreate(BaseModel):
    """
    Data required to add a user to an organization.
    """

    user_id: UUID
    role: OrganizationRoleType = "member"


class OrganizationMemberUpdate(BaseModel):
    """
    Data used to update an organization membership.
    """

    role: OrganizationRoleType | None = None


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


class OrganizationMemberRoleResponse(BaseModel):
    """
    Role information returned with organization membership.
    """

    id: UUID
    name: str

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

    role: OrganizationMemberRoleResponse

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