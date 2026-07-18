from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.permissions import require_superuser
from app.models.user import User

from app.schemas.role import (
    RoleCreate,
    RoleResponse,
    RoleUpdate,
    PaginatedRolesResponse,
)

from app.services.role import (
    create_new_role,
    delete_existing_role,
    get_role,
    list_roles,
    update_existing_role,
)

router = APIRouter(
    prefix="/roles",
    tags=["Roles"],
)


@router.get(
    "/",
    response_model=PaginatedRolesResponse,
)
def read_roles(
    skip: int = 0,
    limit: int = 10,
    search: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    return list_roles(
        db,
        skip,
        limit,
        search,
    )


@router.get(
    "/{role_id}",
    response_model=RoleResponse,
)
def read_role(
    role_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    role = get_role(
        db,
        role_id,
    )

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    return role


@router.post(
    "/",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_role(
    role_data: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    role = create_new_role(
        db,
        role_data,
    )

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Role already exists",
        )

    return role


@router.put(
    "/{role_id}",
    response_model=RoleResponse,
)
def update_role(
    role_id: str,
    role_data: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    role = update_existing_role(
        db,
        role_id,
        role_data,
    )

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    return role


@router.delete(
    "/{role_id}",
)
def delete_role(
    role_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    deleted = delete_existing_role(
        db,
        role_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    return {
        "message": "Role deleted successfully",
    }