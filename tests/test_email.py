from unittest.mock import MagicMock, patch

from app.core.config import settings
from app.services.email import (
    send_email,
    send_password_reset_email,
)


@patch("app.services.email.smtplib.SMTP")
def test_send_email(mock_smtp):
    """
    send_email should construct and send a plain-text
    email using the configured SMTP server.
    """

    smtp = MagicMock()
    mock_smtp.return_value.__enter__.return_value = smtp

    send_email(
        to_email="user@example.com",
        subject="Test Email",
        body="This is a test email.",
    )

    mock_smtp.assert_called_once()

    smtp.send_message.assert_called_once()

    message = smtp.send_message.call_args.args[0]

    assert message["To"] == "user@example.com"
    assert message["Subject"] == "Test Email"
    assert "This is a test email." in message.get_content()


@patch("app.services.email.send_email")
def test_send_password_reset_email(mock_send_email):
    """
    send_password_reset_email should construct a reset
    URL and pass the correct email content to send_email.
    """

    token = "test-reset-token"

    send_password_reset_email(
        to_email="user@example.com",
        reset_token=token,
    )

    mock_send_email.assert_called_once()

    call = mock_send_email.call_args

    assert call.kwargs["to_email"] == "user@example.com"
    assert call.kwargs["subject"] == "Password Reset Request"

    body = call.kwargs["body"]

    assert token in body
    assert "reset-password" in body
    assert (
        str(settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)
        in body
    )