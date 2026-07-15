from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db

from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserLogin,
    TokenResponse,
)

from app.services.auth import (
    register_user,
    authenticate_user,
)

from app.core.security import create_access_token


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
):

    try:
        return register_user(
            db,
            user,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db),
):

    user = authenticate_user(
        db,
        credentials.email,
        credentials.password,
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

    token = create_access_token(
        {
            "sub": str(user.id),
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }