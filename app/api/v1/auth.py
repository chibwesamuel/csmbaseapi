from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db

from app.dependencies.auth import get_current_user
from app.dependencies.permissions import require_superuser

from app.models.user import User

from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserLogin,
    Token,
)

from app.services.auth import (
    register_user,
    login_user,
)

from app.services.refresh_token import (
    validate_refresh_token,
    revoke_refresh_token,
)

from app.core.security import create_access_token

from app.schemas.refresh_token import (
    RefreshRequest,
    LogoutRequest,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    """
    Register a new user.
    """

    try:
        return register_user(
            db,
            user,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.post(
    "/login",
    response_model=Token,
)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db),
):
    """
    Authenticate a user and return a JWT access token.
    """

    try:
        return login_user(
            db=db,
            email=credentials.email,
            password=credentials.password,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
        )

@router.post(
    "/logout",
)
def logout(
    request: LogoutRequest,
    db: Session = Depends(get_db),
):
    """
    Revoke a refresh token.
    """

    revoked = revoke_refresh_token(
        db,
        request.refresh_token,
    )

    if not revoked:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Refresh token not found",
        )

    return {
        "message": "Successfully logged out",
    }

@router.post(
    "/refresh",
    response_model=Token,
)
def refresh_access_token(
    request: RefreshRequest,
    db: Session = Depends(get_db),
):
    """
    Generate a new access token using a refresh token.
    """

    user = validate_refresh_token(
        db,
        request.refresh_token,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    access_token = create_access_token(
        {
            "sub": user.email,
        }
    )

    return Token(
        access_token=access_token,
        refresh_token=request.refresh_token,
        token_type="bearer",
    )

@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    """
    Return the currently authenticated user.
    """

    return current_user


@router.get(
    "/admin-test",
)
def admin_test(
    current_user: User = Depends(require_superuser),
):
    """
    Test endpoint requiring superuser access.
    """

    return {
        "message": "Welcome, admin!",
        "email": current_user.email,
    }