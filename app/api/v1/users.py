from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.permissions import require_superuser
from app.models.user import User
from app.schemas.user import UserResponse
from app.services.user import (
    list_users,
    get_user,
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

    return user