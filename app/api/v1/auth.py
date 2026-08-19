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

from app.schemas.refresh_token import (
    RefreshRequest,
    LogoutRequest,
)

from app.services.auth import (
    register_user,
    login_user,
)

from app.services.refresh_token import (
    rotate_user_refresh_token,
    revoke_refresh_token,
)

from app.core.security import create_access_token


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description=(
        "Create a new CSMBaseAPI user account. "
        "Email addresses and usernames must be unique."
    ),
    responses={
        201: {
            "description": "User registered successfully",
        },
        400: {
            "description": (
                "Validation failed or the email/username "
                "already exists"
            ),
        },
    },
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    """
    Register a new user.
    """

    return register_user(
        db,
        user,
    )


@router.post(
    "/login",
    response_model=Token,
    summary="Authenticate a user",
    description=(
        "Authenticate using an email address and password. "
        "Returns both an access token and a refresh token."
    ),
    responses={
        200: {
            "description": "Authentication successful",
        },
        401: {
            "description": "Invalid email or password",
        },
    },
)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db),
):
    """
    Authenticate a user and return JWT tokens.
    """

    return login_user(
        db=db,
        email=credentials.email,
        password=credentials.password,
    )


@router.post(
    "/logout",
    summary="Logout user",
    description=(
        "Invalidate a refresh token so it can no longer "
        "be used to obtain new access tokens."
    ),
    responses={
        200: {
            "description": "Successfully logged out",
        },
        404: {
            "description": "Refresh token not found",
        },
    },
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
    summary="Refresh access token",
    description=(
        "Generate a new JWT access token using a valid "
        "refresh token."
    ),
    responses={
        200: {
            "description": "Access token refreshed successfully",
        },
        401: {
            "description": "Invalid or revoked refresh token",
        },
    },
)
def refresh_access_token(
    request: RefreshRequest,
    db: Session = Depends(get_db),
):
    """
    Rotate a refresh token and issue new access credentials.
    """

    result = rotate_user_refresh_token(
        db,
        request.refresh_token,
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user, new_refresh_token = result

    access_token = create_access_token(
        {
            "sub": user.email,
        }
    )

    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description=(
        "Return the profile of the currently "
        "authenticated user."
    ),
    responses={
        200: {
            "description": "Authenticated user returned",
        },
        401: {
            "description": "Authentication required",
        },
    },
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    """
    Return the currently authenticated user.
    """

    return current_user
