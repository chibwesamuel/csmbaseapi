from fastapi import HTTPException, status


# ==========================================================
# Helper HTTP Exceptions
# ==========================================================

def email_already_registered():
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Email already registered",
    )


def invalid_credentials():
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password",
        headers={
            "WWW-Authenticate": "Bearer",
        },
    )


def forbidden(
    message: str = (
        "You do not have permission to perform this action"
    ),
):
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=message,
    )


def not_found(resource: str = "Resource"):
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{resource} not found",
    )


def bad_request(message: str):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=message,
    )


# ==========================================================
# Custom Exceptions
# ==========================================================

class EmailAlreadyRegistered(Exception):
    """
    Raised when attempting to register
    an email address that already exists.
    """

    def __init__(
        self,
        message: str = "Email already registered",
    ):
        self.message = message