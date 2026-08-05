from datetime import datetime
from uuid import UUID

from typing import Literal

from pydantic import BaseModel, ConfigDict


ProjectStatus = Literal[
    "active",
    "archived",
]


class ProjectCreate(BaseModel):
    """
    Data required to create a project.
    """

    name: str
    slug: str
    description: str | None = None
    status: ProjectStatus = "active"


class ProjectUpdate(BaseModel):
    """
    Data used to update a project.
    """

    name: str | None = None
    description: str | None = None
    status: ProjectStatus | None = None


class ProjectCreatorResponse(BaseModel):
    """
    Basic creator information.
    """

    id: UUID
    username: str
    email: str

    model_config = ConfigDict(
        from_attributes=True
    )


class ProjectResponse(BaseModel):
    """
    Project data returned to clients.
    """

    id: UUID

    organization_id: UUID

    created_by: UUID

    name: str
    slug: str
    description: str | None
    status: str

    creator: ProjectCreatorResponse

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class PaginatedProjectsResponse(BaseModel):
    """
    Paginated project response.
    """

    total: int
    skip: int
    limit: int

    projects: list[ProjectResponse]

    model_config = ConfigDict(
        from_attributes=True
    )