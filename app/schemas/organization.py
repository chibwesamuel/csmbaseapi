from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OrganizationCreate(BaseModel):
    """
    Data required to create an organization.
    """

    name: str
    slug: str
    description: str | None = None


class OrganizationUpdate(BaseModel):
    """
    Data used to update an organization.
    """

    name: str | None = None
    slug: str | None = None
    description: str | None = None


class OrganizationResponse(BaseModel):
    """
    Organization data returned to clients.
    """

    id: UUID
    name: str
    slug: str
    description: str | None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class PaginatedOrganizationsResponse(BaseModel):
    """
    Paginated organization response.
    """

    total: int
    skip: int
    limit: int
    organizations: list[OrganizationResponse]

    model_config = ConfigDict(
        from_attributes=True
    )