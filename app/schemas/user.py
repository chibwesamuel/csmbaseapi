from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, ConfigDict


class UserCreate(BaseModel):
    """
    Data required to create a user.
    """

    email: EmailStr
    username: str
    password: str
    first_name: str
    last_name: str


class UserLogin(BaseModel):
    """
    Login credentials.
    """

    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    """
    Data used to update an existing user.
    """

    email: EmailStr | None = None
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None

    is_active: bool | None = None
    is_verified: bool | None = None
    is_superuser: bool | None = None

class UserResponse(BaseModel):
    """
    User data returned to clients.
    """

    id: UUID
    email: EmailStr
    username: str
    first_name: str
    last_name: str

    is_active: bool
    is_verified: bool
    is_superuser: bool

    created_at: datetime
    updated_at: datetime


    model_config = ConfigDict(
        from_attributes=True
    )


class Token(BaseModel):
    """
    JWT response.
    """

    access_token: str
    token_type: str = "bearer"

class PaginatedUsersResponse(BaseModel):
    """
    Paginated user response.
    """

    total: int
    skip: int
    limit: int
    users: list[UserResponse]

    model_config = ConfigDict(
        from_attributes=True
    )