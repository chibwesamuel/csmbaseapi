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

from app.dependencies.organization import (
    get_current_project,
)

from app.models.user import User
from app.models.project import Project

from app.schemas.project_member import (
    ProjectMemberCreate,
    ProjectMemberUpdate,
    ProjectMemberResponse,
    PaginatedProjectMembersResponse,
)

from app.services.project_member import (
    add_project_member,
    get_members,
    get_member,
    change_member_role,
    remove_member,
)


router = APIRouter(
    prefix="/organizations/{organization_id}/projects/{project_id}/members",
    tags=["Project Members"],
)


@router.post(
    "",
    response_model=ProjectMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_member(
    organization_id: UUID,
    project_id: UUID,
    data: ProjectMemberCreate,
    db: Session = Depends(get_db),
    project: Project = Depends(get_current_project),
    current_user: User = Depends(
        require_permission(
            "projects.members.manage"
        )
    ),
):
    """
    Add a user to a project.

    The project must belong to the requested organization.
    """

    try:

        return add_project_member(
            db,
            project.id,
            data.user_id,
            data.role,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.get(
    "",
    response_model=PaginatedProjectMembersResponse,
)
def list_members(
    organization_id: UUID,
    project_id: UUID,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    project: Project = Depends(get_current_project),
    current_user: User = Depends(
        require_permission(
            "projects.view"
        )
    ),
):
    """
    List project members.

    The project must belong to the requested organization.
    """

    return get_members(
        db,
        project.id,
        skip,
        limit,
    )


@router.get(
    "/{user_id}",
    response_model=ProjectMemberResponse,
)
def get_single_member(
    organization_id: UUID,
    project_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db),
    project: Project = Depends(get_current_project),
    current_user: User = Depends(
        require_permission(
            "projects.view"
        )
    ),
):
    """
    Retrieve a project member.

    The project must belong to the requested organization.
    """

    member = get_member(
        db,
        project.id,
        user_id,
    )

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project member not found",
        )

    return member


@router.patch(
    "/{user_id}",
    response_model=ProjectMemberResponse,
)
def update_member(
    organization_id: UUID,
    project_id: UUID,
    user_id: UUID,
    data: ProjectMemberUpdate,
    db: Session = Depends(get_db),
    project: Project = Depends(get_current_project),
    current_user: User = Depends(
        require_permission(
            "projects.members.manage"
        )
    ),
):
    """
    Update project member role.

    The project must belong to the requested organization.
    """

    try:

        return change_member_role(
            db,
            project.id,
            user_id,
            data.role,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.delete(
    "/{user_id}",
)
def delete_member(
    organization_id: UUID,
    project_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db),
    project: Project = Depends(get_current_project),
    current_user: User = Depends(
        require_permission(
            "projects.members.manage"
        )
    ),
):
    """
    Remove a user from a project.

    The project must belong to the requested organization.
    """

    try:

        remove_member(
            db,
            project.id,
            user_id,
        )

        return {
            "message": "Project member removed successfully"
        }

    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )