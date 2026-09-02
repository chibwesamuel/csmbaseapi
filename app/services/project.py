from uuid import UUID

from sqlalchemy.orm import Session
from app.models.project_member import ProjectMember
from app.models.project import Project
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
)

from app.repositories.project import (
    get_projects,
    count_projects,
    get_project,
    get_project_by_slug,
    create_project as repository_create_project,
    update_project as repository_update_project,
    delete_project as repository_delete_project,
)

from app.services.project_cache import (
    invalidate_project_cache,
)

def create_project(
    db: Session,
    organization_id: UUID,
    user_id: UUID,
    project_data: ProjectCreate,
) -> Project:
    """
    Create a new project inside an organization.

    The project creator is automatically assigned
    as the project owner.

    Project creation and owner membership are committed
    as a single transaction.
    """

    existing = get_project_by_slug(
        db,
        organization_id,
        project_data.slug,
    )

    if existing:
        raise ValueError(
            "Project slug already exists in this organization"
        )

    project = Project(
        organization_id=organization_id,
        created_by=user_id,
        name=project_data.name,
        slug=project_data.slug,
        description=project_data.description,
        status=project_data.status,
    )

    try:
        project = repository_create_project(
            db,
            project,
        )

        membership = ProjectMember(
            project_id=project.id,
            user_id=user_id,
            role="owner",
        )

        db.add(membership)

        db.commit()
        db.refresh(project)

        return project

    except Exception:
        db.rollback()
        raise


def list_projects(
    db: Session,
    organization_id: UUID,
    skip: int = 0,
    limit: int = 10,
):
    """
    Return paginated projects for an organization.
    """

    total = count_projects(
        db,
        organization_id,
    )

    projects = get_projects(
        db,
        organization_id,
        skip,
        limit,
    )

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "projects": projects,
    }


def get_project_for_organization(
    db: Session,
    organization_id: UUID,
    project_id: UUID,
) -> Project | None:
    """
    Retrieve a project belonging to an organization.
    """

    return get_project(
        db,
        organization_id,
        project_id,
    )


def update_project(
    db: Session,
    project: Project,
    project_data: ProjectUpdate,
) -> Project:
    """
    Update an existing project.

    The project has already been validated by the
    authorization dependency before reaching this service.
    """

    updates = project_data.model_dump(
        exclude_unset=True
    )

    if "slug" in updates:

        existing = get_project_by_slug(
            db,
            project.organization_id,
            updates["slug"],
        )

        if (
            existing
            and existing.id != project.id
        ):
            raise ValueError(
                "Project slug already exists in this organization"
            )

    project = repository_update_project(
        db,
        project,
        updates,
    )

    invalidate_project_cache(
        project.organization_id,
        project.id,
    )

    return project


def delete_project(
    db: Session,
    project: Project,
) -> bool:
    """
    Delete a project.

    The project has already been validated by the
    authorization dependency before reaching this service.
    """

    deleted = repository_delete_project(
        db,
        project,
    )

    invalidate_project_cache(
        project.organization_id,
        project.id,
    )

    return deleted
