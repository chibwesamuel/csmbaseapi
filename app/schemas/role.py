from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RoleCreate(BaseModel):
    """
    Data required to create a role.
    """

    name: str
    description: str | None = None


class RoleUpdate(BaseModel):
    """
    Data used to update a role.
    """

    name: str | None = None
    description: str | None = None


class RoleResponse(BaseModel):
    """
    Role data returned to clients.
    """

    id: UUID
    name: str
    description: str | None

    model_config = ConfigDict(
        from_attributes=True
    )


class PaginatedRolesResponse(BaseModel):
    """
    Paginated list of roles.
    """

    total: int
    skip: int
    limit: int
    roles: list[RoleResponse]