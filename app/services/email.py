import smtplib

from email.message import EmailMessage

from app.core.config import settings


def send_email(
    to_email: str,
    subject: str,
    body: str,
) -> None:
    """
    Send a plain-text email using the configured SMTP server.
    """

    message = EmailMessage()

    message["From"] = (
        f"{settings.SMTP_FROM_NAME} "
        f"<{settings.SMTP_FROM_EMAIL}>"
    )

    message["To"] = to_email
    message["Subject"] = subject

    message.set_content(body)

    with smtplib.SMTP(
        settings.SMTP_HOST,
        settings.SMTP_PORT,
    ) as smtp:

        if settings.SMTP_USE_TLS:
            smtp.starttls()

        if (
            settings.SMTP_USERNAME
            and settings.SMTP_PASSWORD
        ):
            smtp.login(
                settings.SMTP_USERNAME,
                settings.SMTP_PASSWORD,
            )

        smtp.send_message(message)


def send_password_reset_email(
    to_email: str,
    reset_token: str,
) -> None:
    """
    Send a password reset email containing a secure
    password reset link.
    """

    reset_url = (
        f"{settings.PASSWORD_RESET_URL}"
        f"?token={reset_token}"
    )

    subject = "Password Reset Request"

    body = (
        "Hello,\n\n"
        "We received a request to reset the password "
        "for your account.\n\n"
        "Use the link below to reset your password:\n\n"
        f"{reset_url}\n\n"
        f"This link expires in "
        f"{settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES} "
        "minutes.\n\n"
        "If you did not request a password reset, "
        "you can safely ignore this email.\n\n"
        "Regards,\n"
        f"{settings.APP_NAME}"
    )

    send_email(
        to_email=to_email,
        subject=subject,
        body=body,
    )

def send_email_verification_email(
    to_email: str,
    verification_token: str,
) -> None:
    """
    Send an email verification email containing a secure
    verification link.
    """

    verification_url = (
        f"{settings.EMAIL_VERIFICATION_URL}"
        f"?token={verification_token}"
    )

    subject = "Verify Your Email Address"

    body = (
        "Hello,\n\n"
        "Thank you for creating an account with "
        f"{settings.APP_NAME}.\n\n"
        "Please verify your email address by clicking "
        "the link below:\n\n"
        f"{verification_url}\n\n"
        f"This link expires in "
        f"{settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES} "
        "minutes.\n\n"
        "If you did not create this account, "
        "you can safely ignore this email.\n\n"
        "Regards,\n"
        f"{settings.APP_NAME}"
    )

    send_email(
        to_email=to_email,
        subject=subject,
        body=body,
    )