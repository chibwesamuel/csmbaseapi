from uuid import UUID

from sqlalchemy.orm import Session

from app.models.project import Project
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
)


def create_project(
    db: Session,
    organization_id: UUID,
    user_id: UUID,
    project_data: ProjectCreate,
):
    """
    Create a new project inside an organization.
    """

    existing = (
        db.query(Project)
        .filter(
            Project.organization_id == organization_id,
            Project.slug == project_data.slug,
        )
        .first()
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
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project


def list_projects(
    db: Session,
    organization_id: UUID,
    skip: int = 0,
    limit: int = 10,
):
    """
    Return paginated projects for an organization.
    """

    query = (
        db.query(Project)
        .filter(
            Project.organization_id == organization_id
        )
    )

    total = query.count()

    projects = (
        query
        .offset(skip)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "projects": projects,
    }


def get_project(
    db: Session,
    organization_id: UUID,
    project_id: UUID,
):
    """
    Retrieve a single project belonging to an
    organization.
    """

    return (
        db.query(Project)
        .filter(
            Project.organization_id == organization_id,
            Project.id == project_id,
        )
        .first()
    )


def update_project(
    db: Session,
    project: Project,
    project_data: ProjectUpdate,
):
    """
    Update an existing project.

    The project has already been validated by the
    authorization dependency before reaching this service.
    """

    updates = project_data.model_dump(
        exclude_unset=True
    )

    if "slug" in updates:

        existing = (
            db.query(Project)
            .filter(
                Project.organization_id == project.organization_id,
                Project.slug == updates["slug"],
                Project.id != project.id,
            )
            .first()
        )

        if existing:
            raise ValueError(
                "Project slug already exists in this organization"
            )

    for key, value in updates.items():
        setattr(project, key, value)

    db.commit()
    db.refresh(project)

    return project


def delete_project(
    db: Session,
    project: Project,
):
    """
    Delete a project.

    The project has already been validated by the
    authorization dependency before reaching this service.
    """

    db.delete(project)
    db.commit()

    return True