from uuid import UUID
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from app.schemas.pagination import PaginationMeta


class TaskAttachmentCreate(BaseModel):
    """
    Schema for creating a task attachment.
    """

    file_name: str = Field(
        min_length=1,
        max_length=255,
    )

    file_path: str = Field(
        min_length=1,
        max_length=500,
    )

    file_type: str | None = Field(
        default=None,
        max_length=100,
    )

    file_size: int | None = Field(
        default=None,
        ge=0,
    )


class TaskAttachmentResponse(BaseModel):
    """
    Schema returned for a task attachment.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    task_id: UUID
    uploaded_by: UUID

    file_name: str
    file_path: str
    file_type: str | None
    file_size: int | None

    created_at: datetime


class PaginatedTaskAttachmentsResponse(BaseModel):
    """
    Paginated task attachment response.
    """

    attachments: list[TaskAttachmentResponse]
    total: int
    meta: PaginationMeta
