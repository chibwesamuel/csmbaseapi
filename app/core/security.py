from datetime import datetime, timedelta, timezone
import hashlib
import secrets
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    """
    Hash a plain text password.
    """
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """
    Verify a password against its hash.
    """
    return pwd_context.verify(
        plain_password,
        hashed_password,
    )


def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a JWT access token.
    """

    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (
        expires_delta
        if expires_delta
        else timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    to_encode.update(
        {
            "exp": expire,
            "type": "access",
        }
    )

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def decode_access_token(
    token: str,
) -> dict | None:
    """
    Decode and validate a JWT access token.
    Returns the payload if valid, otherwise None.
    """

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        if payload.get("type") != "access":
            return None

        return payload

    except JWTError:
        return None

def generate_refresh_token() -> str:
    """
    Generate a secure random refresh token.
    """

    return secrets.token_urlsafe(64)


def hash_refresh_token(
    refresh_token: str,
) -> str:
    """
    Hash a refresh token before storing it.
    """

    return hashlib.sha256(
        refresh_token.encode("utf-8")
    ).hexdigest()


def verify_refresh_token(
    refresh_token: str,
    stored_hash: str,
) -> bool:
    """
    Verify a refresh token against its stored hash.
    """

    return (
        hash_refresh_token(refresh_token)
        == stored_hash
    )

def generate_password_reset_token() -> str:
    """
    Generate a cryptographically secure password reset token.

    The raw token is intended to be sent to the user.
    Only its hash should be stored in the database.
    """

    return secrets.token_urlsafe(64)


def hash_password_reset_token(
    reset_token: str,
) -> str:
    """
    Hash a password reset token before storing it.

    SHA-256 is appropriate here because the reset token
    has high entropy and is not a user-chosen secret.
    """

    return hashlib.sha256(
        reset_token.encode("utf-8")
    ).hexdigest()