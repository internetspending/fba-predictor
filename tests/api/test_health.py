"""Test health endpoint."""

from fastapi.testclient import TestClient

# HTTP status codes
HTTP_OK = 200
HTTP_METHOD_NOT_ALLOWED = 405


def test_health_endpoint(client: TestClient) -> None:
    """Test that health endpoint returns 200 and correct response."""
    response = client.get("/v1/health")

    assert response.status_code == HTTP_OK
    assert response.json() == {"status": "ok"}


def test_health_endpoint_content_type(client: TestClient) -> None:
    """Test that health endpoint returns JSON content type."""
    response = client.get("/v1/health")

    assert response.headers["content-type"] == "application/json"


def test_health_endpoint_methods(client: TestClient) -> None:
    """Test that health endpoint only accepts GET requests."""
    # GET should work
    response = client.get("/v1/health")
    assert response.status_code == HTTP_OK

    # POST should not work
    response = client.post("/v1/health")
    assert response.status_code == HTTP_METHOD_NOT_ALLOWED
