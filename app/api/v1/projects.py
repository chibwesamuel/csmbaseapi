from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from sqlalchemy.orm import Session

from app.database.session import get_db

from app.dependencies.organization import (
    get_current_organization,
    get_current_project,
)

from app.dependencies.permissions import (
    require_permission,
)

from app.models.organization import Organization
from app.models.project import Project
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
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
    organization: Organization = Depends(
        get_current_organization
    ),
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
        organization.id,
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
    organization: Organization = Depends(
        get_current_organization
    ),
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
            organization.id,
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
    project: Project = Depends(
        get_current_project
    ),
    current_user: User = Depends(
        require_permission(
            "projects.view"
        )
    ),
):
    """
    Retrieve a project.
    """

    return project


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
)
def update_existing_project(
    organization_id: UUID,
    project_id: UUID,
    project_data: ProjectUpdate,
    project: Project = Depends(
        get_current_project
    ),
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
        return update_project(
            db,
            project,
            project_data,
        )

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
    project: Project = Depends(
        get_current_project
    ),
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

    delete_project(
        db,
        project,
    )

    return {
        "message": "Project deleted successfully"
    }