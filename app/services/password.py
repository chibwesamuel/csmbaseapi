from sqlalchemy.orm import Session

from app.core.exceptions import (
    BadRequest,
    InvalidCredentials,
)

from app.core.security import (
    hash_password,
    verify_password,
)

from app.models.user import User

from app.schemas.user import PasswordChange

from app.repositories.refresh_token import (
    revoke_all_user_tokens_without_commit,
)


def change_user_password(
    db: Session,
    user: User,
    password_data: PasswordChange,
) -> None:
    """
    Change the authenticated user's password.

    The password update and refresh-token revocation are
    committed as one database transaction.
    """

    if not verify_password(
        password_data.current_password,
        user.hashed_password,
    ):
        raise InvalidCredentials(
            message="Current password is incorrect",
        )

    if password_data.current_password == (
        password_data.new_password
    ):
        raise BadRequest(
            "New password must be different from the current password"
        )

    user.hashed_password = hash_password(
        password_data.new_password,
    )

    revoke_all_user_tokens_without_commit(
        db,
        user.id,
    )

    db.commit()