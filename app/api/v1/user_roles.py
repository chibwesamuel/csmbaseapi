from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.permissions import require_superuser
from app.models.user import User

from app.services.user_role import (
    assign_user_role,
    remove_user_role,
    list_user_roles,
)

from app.schemas.role import RoleResponse


router = APIRouter(
    prefix="/users",
    tags=["User Roles"],
)


@router.post(
    "/{user_id}/roles/{role_id}",
    response_model=RoleResponse,
)
def assign_role(
    user_id: str,
    role_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    user = assign_user_role(
        db,
        user_id,
        role_id,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User or role not found",
        )

    return user.roles[-1]


@router.delete(
    "/{user_id}/roles/{role_id}",
)
def remove_role(
    user_id: str,
    role_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    user = remove_user_role(
        db,
        user_id,
        role_id,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User or role not found",
        )

    return {
        "message": "Role removed from user successfully"
    }


@router.get(
    "/{user_id}/roles",
    response_model=list[RoleResponse],
)
def get_roles(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    roles = list_user_roles(
        db,
        user_id,
    )

    if roles is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return roles