from unittest.mock import patch

import pytest
from fastapi import Request

from app.core.exceptions import RateLimitExceeded
from app.dependencies.rate_limit import rate_limit


def create_request(client_ip="127.0.0.1"):
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/test",
        "headers": [],
        "client": (client_ip, 12345),
        "query_string": b"",
        "server": ("testserver", 80),
        "scheme": "http",
    }

    return Request(scope)


# ---------------------------------------------------------
# Unit Tests
# ---------------------------------------------------------


def test_rate_limit_allows_requests_under_limit():
    dependency = rate_limit(
        name="test",
        limit=3,
        window=60,
    )

    request = create_request()

    with patch(
        "app.dependencies.rate_limit.increment",
        side_effect=[1, 2, 3],
    ) as mock_increment:

        assert dependency(request) is None
        assert dependency(request) is None
        assert dependency(request) is None

    assert mock_increment.call_count == 3

    mock_increment.assert_any_call(
        "rate_limit:test:127.0.0.1",
        expire=60,
    )


def test_rate_limit_rejects_request_over_limit():
    dependency = rate_limit(
        name="test",
        limit=3,
        window=60,
    )

    request = create_request()

    with patch(
        "app.dependencies.rate_limit.increment",
        side_effect=[1, 2, 3, 4],
    ):

        assert dependency(request) is None
        assert dependency(request) is None
        assert dependency(request) is None

        with pytest.raises(RateLimitExceeded) as exc_info:
            dependency(request)

    assert exc_info.value.status_code == 429
    assert exc_info.value.message == (
        "Too many requests. Please try again later."
    )
    assert exc_info.value.headers == {
        "Retry-After": "60",
    }


def test_rate_limit_fails_open_when_redis_unavailable():
    dependency = rate_limit(
        name="test",
        limit=3,
        window=60,
    )

    request = create_request()

    with patch(
        "app.dependencies.rate_limit.increment",
        return_value=None,
    ) as mock_increment:

        assert dependency(request) is None

    mock_increment.assert_called_once_with(
        "rate_limit:test:127.0.0.1",
        expire=60,
    )


def test_rate_limit_uses_client_ip_in_key():
    dependency = rate_limit(
        name="login",
        limit=5,
        window=60,
    )

    request = create_request(
        client_ip="192.168.1.25",
    )

    with patch(
        "app.dependencies.rate_limit.increment",
        return_value=1,
    ) as mock_increment:

        assert dependency(request) is None

    mock_increment.assert_called_once_with(
        "rate_limit:login:192.168.1.25",
        expire=60,
    )


def test_rate_limit_handles_missing_client():
    dependency = rate_limit(
        name="test",
        limit=3,
        window=60,
    )

    scope = {
        "type": "http",
        "method": "GET",
        "path": "/test",
        "headers": [],
        "client": None,
        "query_string": b"",
        "server": ("testserver", 80),
        "scheme": "http",
    }

    request = Request(scope)

    with patch(
        "app.dependencies.rate_limit.increment",
        return_value=1,
    ) as mock_increment:

        assert dependency(request) is None

    mock_increment.assert_called_once_with(
        "rate_limit:test:unknown",
        expire=60,
    )


# ---------------------------------------------------------
# HTTP Integration Tests
# ---------------------------------------------------------


def test_login_rate_limit_returns_429(
    client,
    unique_user,
):
    """
    Login must return HTTP 429 after five requests from
    the same client IP.
    """

    with patch(
        "app.dependencies.rate_limit.increment",
        return_value=1,
    ):
        register_response = client.post(
            "/api/v1/auth/register",
            json=unique_user,
        )

    assert register_response.status_code == 201

    with patch(
        "app.dependencies.rate_limit.increment",
        side_effect=[1, 2, 3, 4, 5, 6],
    ):

        for _ in range(5):
            response = client.post(
                "/api/v1/auth/login",
                json={
                    "email": unique_user["email"],
                    "password": unique_user["password"],
                },
            )

            assert response.status_code == 200

        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": unique_user["email"],
                "password": unique_user["password"],
            },
        )

    assert response.status_code == 429
    assert response.headers["Retry-After"] == "60"
    assert response.json()["message"] == (
        "Too many requests. Please try again later."
    )


def test_register_rate_limit_returns_429(client):
    """
    Registration must return HTTP 429 after five requests
    from the same client IP.
    """

    with patch(
        "app.dependencies.rate_limit.increment",
        side_effect=[1, 2, 3, 4, 5, 6],
    ):

        for index in range(5):
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "email": (
                        f"rateuser{index}"
                        "@example.com"
                    ),
                    "username": (
                        f"rateuser{index}"
                    ),
                    "password": "password123",
                    "first_name": "Rate",
                    "last_name": "User",
                },
            )

            assert response.status_code == 201

        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "rateuser5@example.com",
                "username": "rateuser5",
                "password": "password123",
                "first_name": "Rate",
                "last_name": "User",
            },
        )

    assert response.status_code == 429
    assert response.headers["Retry-After"] == "60"


def test_refresh_rate_limit_returns_429(
    client,
    unique_user,
):
    """
    Refresh must return HTTP 429 after ten requests from
    the same client IP.

    The refresh token itself is intentionally invalid. This
    allows us to verify that the rate-limit dependency runs
    before the endpoint's refresh-token validation.
    """

    with patch(
        "app.dependencies.rate_limit.increment",
        return_value=1,
    ):
        register_response = client.post(
            "/api/v1/auth/register",
            json=unique_user,
        )

    assert register_response.status_code == 201

    with patch(
        "app.dependencies.rate_limit.increment",
        side_effect=list(range(1, 12)),
    ):

        for _ in range(10):
            response = client.post(
                "/api/v1/auth/refresh",
                json={
                    "refresh_token": "invalid-refresh-token",
                },
            )

            assert response.status_code == 401

        response = client.post(
            "/api/v1/auth/refresh",
            json={
                "refresh_token": "invalid-refresh-token",
            },
        )

    assert response.status_code == 429
    assert response.headers["Retry-After"] == "60"
    assert response.json()["message"] == (
        "Too many requests. Please try again later."
    )


def test_forgot_password_rate_limit_returns_429(
    client,
    unique_user,
):
    """
    Forgot-password must return HTTP 429 after five
    requests from the same client IP.

    Email delivery is mocked because this test is concerned
    only with rate limiting, not SMTP connectivity.
    """

    with patch(
        "app.dependencies.rate_limit.increment",
        return_value=1,
    ):
        register_response = client.post(
            "/api/v1/auth/register",
            json=unique_user,
        )

    assert register_response.status_code == 201

    with patch(
        "app.dependencies.rate_limit.increment",
        side_effect=[1, 2, 3, 4, 5, 6],
    ), patch(
        "app.services.password_reset.send_password_reset_email",
    ):

        for _ in range(5):
            response = client.post(
                "/api/v1/auth/forgot-password",
                json={
                    "email": unique_user["email"],
                },
            )

            assert response.status_code == 200

        response = client.post(
            "/api/v1/auth/forgot-password",
            json={
                "email": unique_user["email"],
            },
        )

    assert response.status_code == 429
    assert response.headers["Retry-After"] == "60"
    assert response.json()["message"] == (
        "Too many requests. Please try again later."
    )


def test_reset_password_rate_limit_returns_429(client):
    """
    Reset-password must return HTTP 429 after five
    requests from the same client IP.

    An invalid token is intentional. The first five requests
    should reach token validation and return HTTP 400. The
    sixth request should be blocked by the rate limiter first.
    """

    with patch(
        "app.dependencies.rate_limit.increment",
        side_effect=[1, 2, 3, 4, 5, 6],
    ):

        for _ in range(5):
            response = client.post(
                "/api/v1/auth/reset-password",
                json={
                    "token": "invalid-token",
                    "new_password": "NewPassword123",
                },
            )

            assert response.status_code == 400

        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": "invalid-token",
                "new_password": "NewPassword123",
            },
        )

    assert response.status_code == 429
    assert response.headers["Retry-After"] == "60"
    assert response.json()["message"] == (
        "Too many requests. Please try again later."
    )
