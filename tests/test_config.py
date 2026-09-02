from app.core.config import Settings


def test_settings_defaults():
    settings = Settings(
        DATABASE_URL="postgresql://localhost/test",
        SECRET_KEY="test-secret-key",
        DEBUG=False,
    )

    assert settings.APP_NAME == "CSMBaseAPI"
    assert settings.APP_VERSION == "1.0.0"
    assert settings.ENVIRONMENT == "development"
    assert settings.DEBUG is False

    assert settings.HOST == "0.0.0.0"
    assert settings.PORT == 8000

    assert settings.REDIS_URL == "redis://localhost:6379/0"

    assert settings.ALGORITHM == "HS256"
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30
    assert settings.REFRESH_TOKEN_EXPIRE_DAYS == 7
    assert settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES == 30
    assert settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES == 30

    assert settings.SMTP_HOST == "localhost"
    assert settings.SMTP_PORT == 587
    assert settings.SMTP_USERNAME == ""
    assert settings.SMTP_PASSWORD == ""
    assert settings.SMTP_FROM_EMAIL == "noreply@example.com"
    assert settings.SMTP_FROM_NAME == "CSMBaseAPI"
    assert settings.SMTP_USE_TLS is True

    assert (
        settings.PASSWORD_RESET_URL
        == "http://localhost:3000/reset-password"
    )

    assert (
        settings.EMAIL_VERIFICATION_URL
        == "http://localhost:3000/verify-email"
    )

    assert settings.CORS_ORIGINS == "*"


def test_settings_accept_environment_configuration():
    settings = Settings(
        APP_NAME="TestAPI",
        APP_VERSION="2.0.0",
        ENVIRONMENT="production",
        DEBUG=True,
        HOST="127.0.0.1",
        PORT=9000,
        DATABASE_URL="postgresql://localhost/test",
        REDIS_URL="redis://localhost:6380/1",
        SECRET_KEY="test-secret",
        ALGORITHM="HS256",
        ACCESS_TOKEN_EXPIRE_MINUTES=15,
        REFRESH_TOKEN_EXPIRE_DAYS=14,
        PASSWORD_RESET_TOKEN_EXPIRE_MINUTES=20,
        EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES=25,
        SMTP_HOST="smtp.example.com",
        SMTP_PORT=465,
        SMTP_USERNAME="user",
        SMTP_PASSWORD="password",
        SMTP_FROM_EMAIL="noreply@example.com",
        SMTP_FROM_NAME="Test API",
        SMTP_USE_TLS=False,
        PASSWORD_RESET_URL="https://example.com/reset",
        EMAIL_VERIFICATION_URL="https://example.com/verify",
        CORS_ORIGINS="https://example.com,https://admin.example.com",
    )

    assert settings.APP_NAME == "TestAPI"
    assert settings.ENVIRONMENT == "production"
    assert settings.DEBUG is True
    assert settings.PORT == 9000
    assert settings.REDIS_URL == "redis://localhost:6380/1"
    assert settings.SMTP_PORT == 465
    assert settings.SMTP_USE_TLS is False
    assert settings.CORS_ORIGINS == (
        "https://example.com,https://admin.example.com"
    )