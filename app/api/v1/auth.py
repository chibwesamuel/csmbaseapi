from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db

from app.dependencies.auth import get_current_user

from app.models.user import User

from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserLogin,
    Token,
    PasswordChange,
)

from app.schemas.password_reset import (
    PasswordResetRequest,
    PasswordResetConfirm,
)

from app.services.password import (
    change_user_password,
)

from app.services.password_reset import (
    request_password_reset,
    reset_password,
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

@router.post(
    "/change-password",
    summary="Change current user's password",
    description=(
        "Change the password of the currently authenticated "
        "user. The current password must be supplied correctly."
    ),
    responses={
        200: {
            "description": "Password changed successfully",
        },
        400: {
            "description": (
                "The new password is the same as the current password"
            ),
        },
        401: {
            "description": "Current password is incorrect",
        },
    },
)
def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Change the authenticated user's password.
    """

    change_user_password(
        db=db,
        user=current_user,
        password_data=password_data,
    )

    return {
        "message": "Password changed successfully",
    }

@router.post(
    "/forgot-password",
    summary="Request a password reset",
    description=(
        "Request a password reset using an email address. "
        "The response does not reveal whether the email "
        "belongs to an existing account."
    ),
    responses={
        200: {
            "description": "Password reset request processed",
        },
    },
)
def forgot_password(
    request: PasswordResetRequest,
    db: Session = Depends(get_db),
):
    """
    Request a password reset.

    The API intentionally returns the same response whether
    or not the supplied email belongs to an existing user.
    """

    reset_token = request_password_reset(
        db=db,
        email=request.email,
    )

    response = {
        "message": (
            "If an account exists for this email, "
            "a password reset link has been generated."
        ),
    }

    # Temporary development behavior.
    #
    # Until an email delivery service is implemented, expose
    # the generated token so the reset flow can be tested.
    if reset_token:
        response["reset_token"] = reset_token

    return response


@router.post(
    "/reset-password",
    summary="Reset password",
    description=(
        "Reset a user's password using a valid password "
        "reset token."
    ),
    responses={
        200: {
            "description": "Password reset successfully",
        },
        400: {
            "description": (
                "Invalid, expired, used, or revoked "
                "password reset token"
            ),
        },
    },
)
def reset_password_endpoint(
    request: PasswordResetConfirm,
    db: Session = Depends(get_db),
):
    """
    Reset a user's password using a password reset token.
    """

    success = reset_password(
        db=db,
        raw_token=request.token,
        new_password=request.new_password,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token",
        )

    return {
        "message": "Password reset successfully",
    }

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
