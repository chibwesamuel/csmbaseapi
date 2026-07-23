from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, HttpUrl


class OrganizationCreate(BaseModel):
    """
    Data required to create an organization.
    """

    name: str
    slug: str

    description: str | None = None

    email: EmailStr | None = None
    phone: str | None = None
    website: HttpUrl | None = None
    logo_url: HttpUrl | None = None

    address: str | None = None
    city: str | None = None
    country: str | None = None

    timezone: str | None = None
    currency: str | None = None


class OrganizationUpdate(BaseModel):
    """
    Data used to update an organization.
    """

    name: str | None = None
    slug: str | None = None

    description: str | None = None

    email: EmailStr | None = None
    phone: str | None = None
    website: HttpUrl | None = None
    logo_url: HttpUrl | None = None

    address: str | None = None
    city: str | None = None
    country: str | None = None

    timezone: str | None = None
    currency: str | None = None

    is_active: bool | None = None


class OrganizationResponse(BaseModel):
    """
    Organization data returned to clients.
    """

    id: UUID

    name: str
    slug: str

    description: str | None

    email: EmailStr | None
    phone: str | None
    website: HttpUrl | None
    logo_url: HttpUrl | None

    address: str | None
    city: str | None
    country: str | None

    timezone: str | None
    currency: str | None

    is_active: bool

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedOrganizationsResponse(BaseModel):
    """
    Paginated organization response.
    """

    total: int
    skip: int
    limit: int

    organizations: list[OrganizationResponse]

    model_config = ConfigDict(from_attributes=True)