from unittest.mock import patch

from fastapi import APIRouter

from app.main import app


router = APIRouter()


@router.get("/test-unhandled-exception")
async def unhandled_exception_endpoint():
    raise RuntimeError("test exception")


app.include_router(router)


def test_global_exception_handler_returns_generic_error():
    from fastapi.testclient import TestClient

    test_client = TestClient(
        app,
        raise_server_exceptions=False,
    )

    with patch(
        "app.core.exception_handlers.logger.exception"
    ) as mock_logger:

        response = test_client.get(
            "/test-unhandled-exception"
        )

        assert response.status_code == 500

        body = response.json()

        assert body["success"] is False
        assert body["message"] == "Internal server error"

        request_id = response.headers.get(
            "X-Request-ID"
        )

        assert request_id is not None

        mock_logger.assert_called_once()

        args = mock_logger.call_args[0]

        assert args[0] == (
            "Unhandled exception [request_id=%s] %s %s"
        )
        assert args[1] == request_id
        assert args[2] == "GET"
        assert args[3] == "/test-unhandled-exception"