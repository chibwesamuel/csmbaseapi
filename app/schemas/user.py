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


class TokenResponse(BaseModel):
    """
    JWT response.
    """

    access_token: str
    token_type: str = "bearer"