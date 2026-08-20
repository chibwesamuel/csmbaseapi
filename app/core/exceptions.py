from typing import Optional


class AppException(Exception):
    """
    Base exception for application-level errors.

    Application and service layers raise these exceptions
    without depending on FastAPI.
    """

    status_code: int = 500

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        headers: Optional[dict[str, str]] = None,
    ):
        super().__init__(message)

        self.message = message

        if status_code is not None:
            self.status_code = status_code

        self.headers = headers


class EmailAlreadyRegistered(AppException):
    """
    Raised when attempting to register an email
    address that already exists.
    """

    def __init__(
        self,
        message: str = "Email already registered",
    ):
        super().__init__(
            message=message,
            status_code=400,
        )

class UsernameAlreadyRegistered(AppException):
    """
    Raised when attempting to register a username
    that already exists.
    """

    def __init__(
        self,
        message: str = "Username already registered",
    ):
        super().__init__(
            message=message,
            status_code=400,
        )

class InvalidCredentials(AppException):
    """
    Raised when authentication credentials are invalid.
    """

    def __init__(
        self,
        message: str = "Invalid email or password",
    ):
        super().__init__(
            message=message,
            status_code=401,
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )


class Forbidden(AppException):
    """
    Raised when the authenticated user is not
    allowed to perform an action.
    """

    def __init__(
        self,
        message: str = (
            "You do not have permission to perform this action"
        ),
    ):
        super().__init__(
            message=message,
            status_code=403,
        )


class ResourceNotFound(AppException):
    """
    Raised when a requested resource does not exist.
    """

    def __init__(
        self,
        resource: str = "Resource",
    ):
        super().__init__(
            message=f"{resource} not found",
            status_code=404,
        )


class BadRequest(AppException):
    """
    Raised when a request cannot be processed because
    of invalid application-level input.
    """

    def __init__(
        self,
        message: str,
    ):
        super().__init__(
            message=message,
            status_code=400,
        )


# ==========================================================
# Backward-compatible exception helpers
# ==========================================================

def email_already_registered():
    raise EmailAlreadyRegistered()


def invalid_credentials():
    raise InvalidCredentials()


def forbidden(
    message: str = (
        "You do not have permission to perform this action"
    ),
):
    raise Forbidden(message)


def not_found(
    resource: str = "Resource",
):
    raise ResourceNotFound(resource)


def bad_request(
    message: str,
):
    raise BadRequest(message)