from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class RefreshTokenResponse(BaseModel):
    """
    Returned after creating a refresh token.
    """

    refresh_token: str


class RefreshRequest(BaseModel):
    """
    Request to obtain a new access token.
    """

    refresh_token: str


class LogoutRequest(BaseModel):
    """
    Request to revoke a refresh token.
    """

    refresh_token: str


class RefreshTokenRecord(BaseModel):
    """
    Internal representation of a stored refresh token.
    """

    id: UUID
    user_id: UUID
    expires_at: datetime
    revoked_at: datetime | None = None
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }