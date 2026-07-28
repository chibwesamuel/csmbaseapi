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
    page: int = 1,
    page_size: int = 10,
    search: str | None = None,
    sort_by: str | None = None,
    sort_order: str = "asc",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """
    Retrieve roles.

    Supports:

    - Pagination
    - Search
    - Sorting

    Examples:

    /roles?page=1&page_size=20

    /roles?search=admin

    /roles?sort_by=name&sort_order=desc
    """

    if page < 1:
        page = 1

    if page_size < 1:
        page_size = 10

    if page_size > 100:
        page_size = 100

    skip = (
        page - 1
    ) * page_size

    return list_roles(
        db=db,
        skip=skip,
        limit=page_size,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
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