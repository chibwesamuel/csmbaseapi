from unittest.mock import patch


def test_request_logging_middleware(client):
    """
    Middleware should log each request.
    """

    with patch(
        "app.middleware.request_logging.logger.info"
    ) as mock_logger:

        response = client.get("/")

        assert response.status_code == 200

        mock_logger.assert_called_once()

        args = mock_logger.call_args[0]

        assert args[0] == "%s %s completed with %s in %.4fs"
        assert args[1] == "GET"
        assert args[2] == "/"
        assert args[3] == 200