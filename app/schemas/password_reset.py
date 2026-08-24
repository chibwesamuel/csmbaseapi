from pydantic import BaseModel, EmailStr


class PasswordResetRequest(BaseModel):
    """
    Request a password reset.
    """

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """
    Complete a password reset using a valid reset token.
    """

    token: str
    new_password: str