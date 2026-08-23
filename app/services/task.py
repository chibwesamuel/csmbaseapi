from uuid import UUID

from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.user import User
from app.models.task import Task
from app.models.project_member import ProjectMember

from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
)

from app.repositories.task import (
    create_task,
    get_task_by_title,
    list_tasks,
    update_task,
    delete_task,
)

from app.services.task_cache import (
    invalidate_task_cache,
)


def create_new_task(
    db: Session,
    project: Project,
    created_by: UUID,
    data: TaskCreate,
):
    """
    Create a new task.

    The project has already been validated by the
    get_current_project dependency.

    If a user is assigned to the task, that user
    must be a member of the project.
    """

    existing = get_task_by_title(
        db,
        project.id,
        data.title,
    )

    if existing:
        raise ValueError(
            "A task with this title already exists"
        )

    if data.assigned_to:

        user = (
            db.query(User)
            .filter(
                User.id == data.assigned_to
            )
            .first()
        )

        if not user:
            raise ValueError(
                "Assigned user not found"
            )

        membership = (
            db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project.id,
                ProjectMember.user_id == data.assigned_to,
            )
            .first()
        )

        if not membership:
            raise ValueError(
                "Assigned user is not a project member"
            )

    return create_task(
        db,
        project_id=project.id,
        created_by=created_by,
        assigned_to=data.assigned_to,
        title=data.title,
        description=data.description,
        status=data.status,
        priority=data.priority,
        due_date=data.due_date,
    )


def get_tasks(
    db: Session,
    project_id: UUID,
    skip: int = 0,
    limit: int = 10,
    status: str | None = None,
    priority: str | None = None,
    assigned_to: UUID | None = None,
):
    """
    List tasks belonging to a project.

    The project has already been validated by the
    get_current_project dependency.
    """

    total, tasks = list_tasks(
        db,
        project_id,
        skip,
        limit,
        status,
        priority,
        assigned_to,
    )

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "tasks": tasks,
    }


def get_single_task(
    task: Task,
) -> Task:
    """
    Return the already validated task.

    The task has already been validated by the
    get_current_task dependency.
    """

    return task


def edit_task(
    db: Session,
    project: Project,
    task: Task,
    data: TaskUpdate,
):
    """
    Update a task.

    The task has already been validated by the
    get_current_task dependency.

    If the title changes, the new title must remain
    unique within the project.

    If a user is assigned to the task, that user
    must be a member of the project.

    The project's cached task response is invalidated
    after a successful update.
    """

    if (
        data.title is not None
        and data.title != task.title
    ):
        duplicate = get_task_by_title(
            db,
            task.project_id,
            data.title,
        )

        if duplicate:
            raise ValueError(
                "A task with this title already exists"
            )

    if data.assigned_to is not None:

        user = (
            db.query(User)
            .filter(
                User.id == data.assigned_to
            )
            .first()
        )

        if not user:
            raise ValueError(
                "Assigned user not found"
            )

        membership = (
            db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == task.project_id,
                ProjectMember.user_id == data.assigned_to,
            )
            .first()
        )

        if not membership:
            raise ValueError(
                "Assigned user is not a project member"
            )

    task = update_task(
        db,
        task,
        title=data.title,
        description=data.description,
        status=data.status,
        priority=data.priority,
        assigned_to=data.assigned_to,
        due_date=data.due_date,
    )

    invalidate_task_cache(
        project.organization_id,
        project.id,
        task.id,
    )

    return task


def remove_task(
    db: Session,
    project: Project,
    task: Task,
):
    """
    Delete a task.

    The task has already been validated by the
    get_current_task dependency.

    The project's cached task response is invalidated
    after a successful deletion.
    """

    deleted = delete_task(
        db,
        task,
    )

    invalidate_task_cache(
        project.organization_id,
        project.id,
        task.id,
    )

    return deleted