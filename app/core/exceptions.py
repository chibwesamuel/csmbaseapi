from fastapi import HTTPException, status


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
            "WWW-Authenticate": "Bearer"
        },
    )

class EmailAlreadyRegistered(Exception):
    """
    Raised when attempting to use an email
    that already exists.
    """

    def __init__(self):
        self.message = "Email already registered"