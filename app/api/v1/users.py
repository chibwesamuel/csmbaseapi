from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.permissions import require_superuser
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.services.user import (
    list_users,
    get_user,
    update_user,
    change_user_status,
    delete_user,
)


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/",
    response_model=List[UserResponse],
)
def read_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    return list_users(db)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def read_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):

    user = get_user(
        db,
        user_id,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

@router.put(
    "/{user_id}",
    response_model=UserResponse,
)
def update_existing_user(
    user_id: str,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
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

@router.patch("/{user_id}/deactivate")
def deactivate_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
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

@router.patch("/{user_id}/activate")
def activate_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
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

@router.delete("/{user_id}")
def remove_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
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

    return user