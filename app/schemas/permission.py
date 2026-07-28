from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PermissionCreate(BaseModel):
    """
    Data required to create a permission.
    """

    name: str
    description: str | None = None


class PermissionUpdate(BaseModel):
    """
    Data used to update a permission.
    """

    name: str | None = None
    description: str | None = None


class PermissionResponse(BaseModel):
    """
    Permission returned to clients.
    """

    id: UUID
    name: str
    description: str | None

    model_config = ConfigDict(
        from_attributes=True
    )


class PaginatedPermissionsResponse(BaseModel):
    """
    Paginated list of permissions.
    """

    total: int

    page: int
    page_size: int

    total_pages: int

    has_next: bool
    has_previous: bool

    permissions: list[PermissionResponse]

    model_config = ConfigDict(
        from_attributes=True
    )