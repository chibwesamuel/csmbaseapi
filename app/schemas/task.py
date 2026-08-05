from datetime import datetime
from uuid import UUID

from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
)


TaskStatusType = Literal[
    "todo",
    "in_progress",
    "completed",
]


TaskPriorityType = Literal[
    "low",
    "medium",
    "high",
]


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    assigned_to: UUID | None = None
    status: TaskStatusType = "todo"
    priority: TaskPriorityType = "medium"
    due_date: datetime | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    assigned_to: UUID | None = None
    status: TaskStatusType | None = None
    priority: TaskPriorityType | None = None
    assigned_to: UUID | None = None
    due_date: datetime | None = None


class TaskUserResponse(BaseModel):
    id: UUID
    username: str
    email: str

    model_config = ConfigDict(
        from_attributes=True,
    )


class TaskResponse(BaseModel):
    id: UUID

    project_id: UUID
    created_by: UUID
    assigned_to: UUID | None

    title: str
    description: str | None

    status: str
    priority: str

    due_date: datetime | None

    created_at: datetime
    updated_at: datetime

    creator: TaskUserResponse
    assignee: TaskUserResponse | None = None

    model_config = ConfigDict(
        from_attributes=True,
    )


class PaginatedTasksResponse(BaseModel):

    total: int
    skip: int
    limit: int

    tasks: list[TaskResponse]

    model_config = ConfigDict(
        from_attributes=True,
    )