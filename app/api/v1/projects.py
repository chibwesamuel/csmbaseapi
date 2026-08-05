from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.database.session import get_db

from app.dependencies.permissions import require_permission

from app.models.user import User

from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    PaginatedProjectsResponse,
)

from app.services.project import (
    create_project,
    list_projects,
    get_project,
    update_project,
    delete_project,
)


router = APIRouter(
    prefix="/organizations/{organization_id}/projects",
    tags=["Projects"],
)


@router.get(
    "",
    response_model=PaginatedProjectsResponse,
)
def get_projects(
    organization_id: UUID,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "projects.view"
        )
    ),
):
    """
    List projects belonging to an organization.
    """

    return list_projects(
        db,
        organization_id,
        skip,
        limit,
    )


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_project(
    organization_id: UUID,
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "projects.create"
        )
    ),
):
    """
    Create a new project.
    """

    try:
        return create_project(
            db,
            organization_id,
            current_user.id,
            project_data,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
)
def get_single_project(
    organization_id: UUID,
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "projects.view"
        )
    ),
):
    """
    Retrieve a project.
    """

    project = get_project(
        db,
        organization_id,
        project_id,
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return project


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
)
def update_existing_project(
    organization_id: UUID,
    project_id: UUID,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "projects.update"
        )
    ),
):
    """
    Update a project.
    """

    try:
        project = update_project(
            db,
            organization_id,
            project_id,
            project_data,
        )

        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        return project

    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.delete(
    "/{project_id}",
)
def delete_existing_project(
    organization_id: UUID,
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "projects.delete"
        )
    ),
):
    """
    Delete a project.
    """

    deleted = delete_project(
        db,
        organization_id,
        project_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return {
        "message": "Project deleted successfully"
    }