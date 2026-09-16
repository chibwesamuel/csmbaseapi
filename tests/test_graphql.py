from fastapi.testclient import TestClient


def test_graphql_endpoint_available(client: TestClient):
    response = client.post(
        "/graphql",
        json={
            "query": """
            query {
                hello
            }
            """
        },
        headers={
            "host": "localhost",
        },
    )

    assert response.status_code == 200


def test_graphql_hello_query(client: TestClient):
    response = client.post(
        "/graphql",
        json={
            "query": """
            query {
                hello
            }
            """
        },
        headers={
            "host": "localhost",
        },
    )

    data = response.json()

    assert "data" in data
    assert data["data"]["hello"] == "Hello from CSMBaseAPI GraphQL 🚀"


def test_graphql_invalid_query(client: TestClient):
    response = client.post(
        "/graphql",
        json={
            "query": """
            query {
                invalidField
            }
            """
        },
        headers={
            "host": "localhost",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "errors" in data


def test_security_headers_are_present_on_graphql(client):
    response = client.post(
        "/graphql",
        json={
            "query": "{ hello }",
        },
        headers={
            "host": "localhost",
        },
    )

    assert response.status_code == 200

    assert response.headers["X-Content-Type-Options"] == (
        "nosniff"
    )

    assert response.headers["X-Frame-Options"] == "DENY"

    assert response.headers["Referrer-Policy"] == (
        "strict-origin-when-cross-origin"
    )

    assert response.headers["Permissions-Policy"] == (
        "camera=(), "
        "microphone=(), "
        "geolocation=(), "
        "payment=(), "
        "usb=()"
    )
