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


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/",
    response_model=PaginatedUsersResponse,
)
def read_users(
    skip: int = 0,
    limit: int = 10,
    search: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("users.view")
    ),
):
    return list_users(
        db,
        skip,
        limit,
        search,
    )


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

    try:
        return create_user(
            db,
            user_data,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


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