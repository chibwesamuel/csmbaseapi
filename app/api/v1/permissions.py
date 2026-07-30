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

from app.schemas.permission import (
    PermissionCreate,
    PermissionUpdate,
    PermissionResponse,
    PaginatedPermissionsResponse,
)

from app.services.permission import (
    list_permissions,
    get_permission,
    create_new_permission,
    update_existing_permission,
    delete_existing_permission,
)


router = APIRouter(
    prefix="/permissions",
    tags=["Permissions"],
)


@router.get(
    "/",
    response_model=PaginatedPermissionsResponse,
)
def read_permissions(
    page: int = 1,
    page_size: int = 10,
    search: str | None = None,
    sort_by: str | None = None,
    sort_order: str = "asc",
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("permissions.view")
    ),
):
    """
    Retrieve permissions.

    Supports:

    - Pagination
    - Search
    - Sorting
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

    return list_permissions(
        db=db,
        skip=skip,
        limit=page_size,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get(
    "/{permission_id}",
    response_model=PermissionResponse,
)
def read_permission(
    permission_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("permissions.view")
    ),
):
    permission = get_permission(
        db,
        permission_id,
    )

    if permission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found",
        )

    return permission


@router.post(
    "/",
    response_model=PermissionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_permission(
    permission_data: PermissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("permissions.create")
    ),
):
    permission = create_new_permission(
        db,
        permission_data,
    )

    if permission is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Permission already exists",
        )

    return permission


@router.put(
    "/{permission_id}",
    response_model=PermissionResponse,
)
def update_permission(
    permission_id: str,
    permission_data: PermissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("permissions.update")
    ),
):
    permission = update_existing_permission(
        db,
        permission_id,
        permission_data,
    )

    if permission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found",
        )

    return permission


@router.delete(
    "/{permission_id}"
)
def delete_permission(
    permission_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("permissions.delete")
    ),
):
    deleted = delete_existing_permission(
        db,
        permission_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found",
        )

    return {
        "message": "Permission deleted successfully"
    }