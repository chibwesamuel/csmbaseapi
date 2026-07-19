from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.permissions import require_superuser
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
    role_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
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
)
def add_role_permission(
    role_id: str,
    permission_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    role = assign_permission(
        db,
        role_id,
        permission_id,
    )

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role or permission not found",
        )

    return role


@router.delete(
    "/{role_id}/permissions/{permission_id}",
)
def remove_role_permission(
    role_id: str,
    permission_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    role = revoke_permission(
        db,
        role_id,
        permission_id,
    )

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role or permission not found",
        )

    return {
        "message": "Permission removed from role successfully"
    }