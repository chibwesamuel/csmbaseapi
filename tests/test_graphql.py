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
    )

    assert response.status_code == 200

    data = response.json()

    assert "errors" in data