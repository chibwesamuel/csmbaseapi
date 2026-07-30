from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.database.session import get_db

from app.dependencies.permissions import (
    require_permission,
)

from app.models.user import User

from app.schemas.role import RoleResponse

from app.services.user_role import (
    assign_user_role,
    remove_user_role,
    list_user_roles,
)


router = APIRouter(
    prefix="/users",
    tags=["User Roles"],
)


@router.post(
    "/{user_id}/roles/{role_id}",
    response_model=RoleResponse,
)
def assign_role(
    user_id: UUID,
    role_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("users.update")
    ),
):
    """
    Assign a role to a user.
    """

    try:
        user = assign_user_role(
            db,
            user_id,
            role_id,
        )

        return user.roles[-1]

    except ValueError as error:

        message = str(error)

        if message in (
            "User not found",
            "Role not found",
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            )

        if message == "Role already assigned to user":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=message,
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )


@router.delete(
    "/{user_id}/roles/{role_id}",
)
def remove_role(
    user_id: UUID,
    role_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("users.update")
    ),
):
    """
    Remove a role from a user.
    """

    try:
        remove_user_role(
            db,
            user_id,
            role_id,
        )

        return {
            "message": "Role removed from user successfully"
        }

    except ValueError as error:

        message = str(error)

        if message in (
            "User not found",
            "Role not found",
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            )

        if message == "Role is not assigned to user":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=message,
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )


@router.get(
    "/{user_id}/roles",
    response_model=list[RoleResponse],
)
def get_roles(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("users.view")
    ),
):
    """
    Retrieve all roles assigned to a user.
    """

    try:
        return list_user_roles(
            db,
            user_id,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )