from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field


class TaskCommentCreate(BaseModel):
    """
    Schema for creating a task comment.
    """

    content: str = Field(
        ...,
        min_length=1,
        max_length=5000,
    )


class TaskCommentUpdate(BaseModel):
    """
    Schema for updating a task comment.
    """

    content: str = Field(
        ...,
        min_length=1,
        max_length=5000,
    )


class TaskCommentResponse(BaseModel):
    """
    Task comment response.
    """

    id: UUID
    task_id: UUID
    user_id: UUID
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }


class PaginatedTaskCommentsResponse(BaseModel):
    """
    Paginated task comments response.
    """

    total: int
    skip: int
    limit: int
    comments: list[TaskCommentResponse]