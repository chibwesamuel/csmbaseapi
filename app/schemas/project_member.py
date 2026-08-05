from datetime import datetime
from uuid import UUID

from typing import Literal

from pydantic import BaseModel, ConfigDict


ProjectMemberRoleType = Literal[
    "owner",
    "admin",
    "contributor",
]


class ProjectMemberCreate(BaseModel):
    user_id: UUID
    role: ProjectMemberRoleType = "contributor"


class ProjectMemberUpdate(BaseModel):
    role: ProjectMemberRoleType | None = None


class ProjectMemberUserResponse(BaseModel):
    id: UUID
    username: str
    email: str

    model_config = ConfigDict(
        from_attributes=True,
    )


class ProjectMemberResponse(BaseModel):
    id: UUID

    project_id: UUID
    user_id: UUID

    user: ProjectMemberUserResponse

    role: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class PaginatedProjectMembersResponse(BaseModel):

    total: int
    skip: int
    limit: int

    members: list[ProjectMemberResponse]

    model_config = ConfigDict(
        from_attributes=True,
    )