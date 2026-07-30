from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.schemas.permission import PermissionResponse

from app.database.session import get_db

from app.dependencies.permissions import (
    require_permission,
)

from app.models.user import User

from app.services.role_permission import (
    assign_permission,
    revoke_permission,
    list_role_permissions,
)


router = APIRouter(
    prefix="/roles",
    tags=["Role Permissions"],
)


@router.get(
    "/{role_id}/permissions",
)
def get_role_permissions(
    role_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("roles.view")
    ),
):
    """
    Retrieve all permissions assigned to a role.
    """

    permissions = list_role_permissions(
        db,
        role_id,
    )

    if permissions is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    return permissions


@router.post(
    "/{role_id}/permissions/{permission_id}",
    response_model=PermissionResponse,
)
def add_role_permission(
    role_id: UUID,
    permission_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("roles.update")
    ),
):
    """
    Assign a permission to a role.
    """

    try:
        return assign_permission(
            db,
            role_id,
            permission_id,
        )

    except ValueError as error:

        message = str(error)

        if message in (
            "Role not found",
            "Permission not found",
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            )

        if message == "Permission already assigned to role":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=message,
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )


@router.delete(
    "/{role_id}/permissions/{permission_id}",
)
def remove_role_permission(
    role_id: UUID,
    permission_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("roles.update")
    ),
):
    """
    Remove a permission from a role.
    """

    try:

        revoke_permission(
            db,
            role_id,
            permission_id,
        )

        return {
            "message": "Permission removed from role successfully"
        }

    except ValueError as error:

        message = str(error)

        if message in (
            "Role not found",
            "Permission not found",
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            )

        if message == "Permission is not assigned to role":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=message,
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )