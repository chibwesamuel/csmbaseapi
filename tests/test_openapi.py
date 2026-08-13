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

def test_openapi_security_scheme(client):
    response = client.get("/openapi.json")

    assert response.status_code == 200

    data = response.json()

    security_schemes = (
        data["components"]["securitySchemes"]
    )

    assert "OAuth2PasswordBearer" in security_schemes

    scheme = security_schemes["OAuth2PasswordBearer"]

    assert scheme["type"] == "oauth2"
    assert scheme["flows"]["password"]["tokenUrl"] == (
        "/api/v1/auth/login"
    )

def test_openapi_protected_endpoints(client):
    response = client.get("/openapi.json")

    assert response.status_code == 200

    paths = response.json()["paths"]

    protected_paths = [
        "/api/v1/auth/me",
        "/api/v1/users/",
        "/api/v1/users/me",
        "/api/v1/roles/",
        "/api/v1/permissions/",
        "/api/v1/organizations/",
    ]

    for path in protected_paths:
        assert path in paths

        for operation in paths[path].values():
            if not isinstance(operation, dict):
                continue

            assert "security" in operation
            assert {
                "OAuth2PasswordBearer": []
            } in operation["security"]

def test_openapi_public_auth_endpoints(client):
    response = client.get("/openapi.json")

    assert response.status_code == 200

    paths = response.json()["paths"]

    public_endpoints = [
        ("/api/v1/auth/login", "post"),
        ("/api/v1/auth/register", "post"),
        ("/api/v1/auth/refresh", "post"),
    ]

    for path, method in public_endpoints:
        operation = paths[path][method]

        assert "security" not in operation