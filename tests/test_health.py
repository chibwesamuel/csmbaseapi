from unittest.mock import patch


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert "application" in data
    assert "version" in data


def test_readiness_check(client):
    response = client.get("/ready")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ready"
    assert "application" in data
    assert "version" in data

    assert data["dependencies"]["database"] == "available"
    assert data["dependencies"]["redis"] == "available"


def test_readiness_check_database_unavailable(client):
    with patch(
        "app.main.engine.connect",
        side_effect=Exception("Database unavailable"),
    ):
        response = client.get("/ready")

    assert response.status_code == 503

    data = response.json()

    assert data["status"] == "not_ready"
    assert data["dependencies"]["database"] == "unavailable"
    assert data["dependencies"]["redis"] == "available"


def test_readiness_check_redis_unavailable(client):
    with patch(
        "app.main.redis_is_available",
        return_value=False,
    ):
        response = client.get("/ready")

    assert response.status_code == 503

    data = response.json()

    assert data["status"] == "not_ready"
    assert data["dependencies"]["database"] == "available"
    assert data["dependencies"]["redis"] == "unavailable"
