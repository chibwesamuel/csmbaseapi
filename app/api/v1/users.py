from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.permissions import require_permission
from app.models.user import User

from app.schemas.user import (
    UserResponse,
    UserUpdate,
    UserCreate,
    PaginatedUsersResponse,
)

from app.services.user import (
    list_users,
    get_user,
    update_user,
    create_user,
    change_user_status,
    delete_user,
)

from app.core.query_params import (
    PageParam,
    PageSizeParam,
    SearchParam,
    SortByParam,
    SortOrderParam,
)


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


# ==========================================================
# List Users (Pagination + Search + Sorting + Filtering)
# ==========================================================

@router.get(
    "/",
    response_model=PaginatedUsersResponse,
)
def read_users(
    page: PageParam = 1,
    page_size: PageSizeParam = 10,
    search: SearchParam = None,
    sort_by: SortByParam = None,
    sort_order: SortOrderParam = "asc",
    is_active: bool | None = None,
    is_verified: bool | None = None,
    is_superuser: bool | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("users.view")
    ),
):
    """
    Retrieve users.

    Supports:

    - Pagination
    - Search
    - Sorting
    - Filtering

    Examples:

    /users?page=1&page_size=20

    /users?search=sam

    /users?sort_by=created_at&sort_order=desc

    /users?is_active=true
    """

    skip = (
        page - 1
    ) * page_size

    return list_users(
        db=db,
        skip=skip,
        limit=page_size,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        is_active=is_active,
        is_verified=is_verified,
        is_superuser=is_superuser,
    )


# ==========================================================
# Get Single User
# ==========================================================

# ==========================================================
# Get Current User Profile
# ==========================================================

@router.get(
    "/me",
    response_model=UserResponse,
)
def read_current_user(
    current_user: User = Depends(
        require_permission("users.view")
    ),
):
    """
    Retrieve currently authenticated user.
    """

    return current_user

@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def read_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("users.view")
    ),
):
    """
    Retrieve a single user.
    """

    user = get_user(
        db,
        user_id,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


# ==========================================================
# Create User
# ==========================================================

@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("users.create")
    ),
):
    """
    Create a new user.
    """

    return create_user(
        db,
        user_data,
    )


# ==========================================================
# Update User
# ==========================================================

@router.put(
    "/{user_id}",
    response_model=UserResponse,
)
def update_existing_user(
    user_id: str,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("users.update")
    ),
):
    """
    Update an existing user.
    """

    user = update_user(
        db,
        user_id,
        user_data,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


# ==========================================================
# Deactivate User
# ==========================================================

@router.patch(
    "/{user_id}/deactivate",
    response_model=UserResponse,
)
def deactivate_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("users.update")
    ),
):
    """
    Deactivate a user account.
    """

    user = change_user_status(
        db,
        user_id,
        False,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


# ==========================================================
# Activate User
# ==========================================================

@router.patch(
    "/{user_id}/activate",
    response_model=UserResponse,
)
def activate_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("users.update")
    ),
):
    """
    Activate a user account.
    """

    user = change_user_status(
        db,
        user_id,
        True,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


# ==========================================================
# Delete User
# ==========================================================

@router.delete(
    "/{user_id}",
)
def remove_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("users.delete")
    ),
):
    """
    Delete a user account.
    """

    deleted = delete_user(
        db,
        user_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return {
        "message": "User deleted successfully"
    }