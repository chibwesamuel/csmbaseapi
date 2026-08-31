from unittest.mock import patch
from uuid import UUID


def test_request_logging_middleware(client):
    """
    Middleware should log each request and attach
    a request ID to the response.
    """

    with patch(
        "app.middleware.request_logging.logger.info"
    ) as mock_logger:

        response = client.get("/")

        assert response.status_code == 200

        request_id = response.headers.get(
            "X-Request-ID"
        )

        assert request_id is not None

        UUID(request_id)

        mock_logger.assert_called_once()

        args = mock_logger.call_args[0]

        assert args[0] == (
            "%s %s completed with %s in %.4fs "
            "[request_id=%s]"
        )
        assert args[1] == "GET"
        assert args[2] == "/"
        assert args[3] == 200
        assert args[4] >= 0
        assert args[5] == request_id
