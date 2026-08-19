from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from app.models.project import Project


def project_query(db: Session):
    """
    Base project query with required relationships loaded.
    """

    return (
        db.query(Project)
        .options(
            joinedload(
                Project.creator
            ),
        )
    )


def get_projects(
    db: Session,
    organization_id: UUID,
    skip: int = 0,
    limit: int = 10,
) -> list[Project]:
    """
    Retrieve projects belonging to an organization.
    """

    return (
        project_query(db)
        .filter(
            Project.organization_id == organization_id
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


def count_projects(
    db: Session,
    organization_id: UUID,
) -> int:
    """
    Count projects belonging to an organization.
    """

    return (
        db.query(Project)
        .filter(
            Project.organization_id == organization_id
        )
        .count()
    )


def get_project(
    db: Session,
    organization_id: UUID,
    project_id: UUID,
) -> Project | None:
    """
    Retrieve a single project by ID.
    """

    return (
        project_query(db)
        .filter(
            Project.organization_id == organization_id,
            Project.id == project_id,
        )
        .first()
    )

def get_project_by_id(
    db: Session,
    project_id: UUID,
) -> Project | None:
    """
    Retrieve a project by ID.
    """

    return (
        project_query(db)
        .filter(
            Project.id == project_id,
        )
        .first()
    )


def get_project_by_slug(
    db: Session,
    organization_id: UUID,
    slug: str,
) -> Project | None:
    """
    Retrieve a project by slug inside an organization.
    """

    return (
        db.query(Project)
        .filter(
            Project.organization_id == organization_id,
            Project.slug == slug,
        )
        .first()
    )


def create_project(
    db: Session,
    project: Project,
) -> Project:
    """
    Create a project.
    """

    db.add(project)
    db.commit()
    db.refresh(project)

    return get_project(
        db,
        project.organization_id,
        project.id,
    )


def update_project(
    db: Session,
    project: Project,
    data: dict,
) -> Project:
    """
    Update project fields.
    """

    for key, value in data.items():
        setattr(
            project,
            key,
            value,
        )

    db.commit()
    db.refresh(project)

    return get_project(
        db,
        project.organization_id,
        project.id,
    )


def delete_project(
    db: Session,
    project: Project,
) -> bool:
    """
    Delete a project.
    """

    db.delete(project)
    db.commit()

    return True