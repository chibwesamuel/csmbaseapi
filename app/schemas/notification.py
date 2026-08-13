from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class NotificationCreate(BaseModel):
    """
    Schema used internally when creating
    a notification.
    """

    user_id: UUID

    type: str = Field(
        min_length=1,
        max_length=50,
    )

    title: str = Field(
        min_length=1,
        max_length=200,
    )

    message: str = Field(
        min_length=1,
    )


class NotificationResponse(BaseModel):
    """
    Notification response schema.
    """

    id: UUID
    user_id: UUID
    type: str
    title: str
    message: str
    is_read: bool
    read_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class PaginatedNotificationsResponse(BaseModel):
    """
    Paginated notification response.
    """

    total: int
    skip: int
    limit: int
    notifications: list[NotificationResponse]