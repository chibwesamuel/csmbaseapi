def test_openapi_schema(client):
    response = client.get("/openapi.json")

    assert response.status_code == 200

    data = response.json()

    assert data["info"]["title"] == "CSMBaseAPI"
    assert "version" in data["info"]

    assert "/api/v1/auth/login" in data["paths"]
    assert "/api/v1/auth/register" in data["paths"]
    assert "/graphql" in data["paths"]


def test_openapi_tags(client):
    response = client.get("/openapi.json")

    assert response.status_code == 200

    data = response.json()

    tags = [
        tag["name"]
        for tag in data.get("tags", [])
    ]

    expected_tags = [
        "Authentication",
        "Users",
        "Roles",
        "Permissions",
        "Organization",
        "Organization Members",
        "GraphQL",
        "System",
    ]

    for tag in expected_tags:
        assert tag in tags