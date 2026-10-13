"""
Automated unit & integration tests for Labs 3 through 7.
Tests API connectivity with SQLite database, endpoints, validation, and error scenarios.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models import URLItem
from app.utils import BASE62_SET

from sqlalchemy.pool import StaticPool

# Create isolated in-memory test database with StaticPool so all sessions share the same in-memory DB
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


# Override get_db dependency to use test in-memory SQLite database
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_database():
    """Recreate tables fresh before every test."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


# --- Lab 3 Tests ---
def test_root_endpoint():
    """Verify GET / returns 200 and total database count."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Cloud-Based URL Shortener"
    assert data["status"] == "online"
    assert "total_persisted_urls" in data


def test_health_check_endpoint():
    """Verify GET /health confirms SQLite database connectivity."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "sqlite_connected"
    assert "persisted_records_count" in data


def test_post_echo_endpoint():
    """Verify POST /api/echo."""
    payload = {"message": "Cloud Health Check", "client_name": "Pytest Client"}
    response = client.post("/api/echo", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"


# --- Lab 4, 5, 7 Tests: Storing and Retrieving URLs through SQLite API ---
def test_store_url_through_api():
    """Verify POST /api/shorten saves URL to SQLite database automatically."""
    payload = {"url": "https://aws.amazon.com/architecture/"}
    response = client.post("/api/shorten", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    code = data["short_code"]
    assert len(code) == 6
    assert all(c in BASE62_SET for c in code)

    # Verify retrieval from database via API
    get_res = client.get(f"/api/urls/{code}")
    assert get_res.status_code == 200
    retrieved = get_res.json()
    assert retrieved["short_code"] == code
    assert retrieved["original_url"] == payload["url"]
    assert retrieved["click_count"] == 0
    assert retrieved["is_active"] is True


def test_store_url_with_custom_code():
    """Verify storing URL with custom alias in SQLite."""
    payload = {"url": "https://aws.amazon.com/dynamodb/", "custom_code": "my-dynamo"}
    response = client.post("/api/shorten", json=payload)
    assert response.status_code == 201
    assert response.json()["short_code"] == "my-dynamo"

    # Verify duplicate custom code rejected with 409
    res_dup = client.post("/api/shorten", json={"url": "https://other.com", "custom_code": "my-dynamo"})
    assert res_dup.status_code == 409


def test_retrieve_all_stored_urls():
    """Verify GET /api/urls lists all records stored in SQLite."""
    client.post("/api/shorten", json={"url": "https://aws.amazon.com/ec2/", "custom_code": "link-a"})
    client.post("/api/shorten", json={"url": "https://aws.amazon.com/s3/", "custom_code": "link-b"})

    response = client.get("/api/urls")
    assert response.status_code == 200
    data = response.json()
    assert data["total_records"] == 2
    codes = [item["short_code"] for item in data["urls"]]
    assert "link-a" in codes
    assert "link-b" in codes


def test_retrieve_non_existing_url_returns_404():
    """Verify querying a non-existent short code returns 404 Not Found."""
    response = client.get("/api/urls/non-existent-code")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_batch_store_multiple_urls_to_database():
    """Verify POST /api/shorten/batch stores multiple URLs to SQLite in one transaction."""
    urls = [
        "https://aws.amazon.com/lambda/",
        "https://aws.amazon.com/ecs/",
        "https://aws.amazon.com/cloudwatch/",
    ]
    response = client.post("/api/shorten/batch", json={"urls": urls})
    assert response.status_code == 201
    data = response.json()
    assert data["successful_count"] == 3

    # Check database record count
    list_res = client.get("/api/urls")
    assert list_res.json()["total_records"] == 3


def test_shorten_invalid_url_rejected():
    """Verify malformed URLs are rejected before touching database."""
    response = client.post("/api/shorten", json={"url": "ftp://bad-scheme.com"})
    assert response.status_code == 422


# --- Lab 8 Tests: URL Redirection ---
def test_redirect_to_original_url_success():
    """Verify GET /{short_code} returns HTTP 307 redirect pointing to target URL."""
    target = "https://aws.amazon.com/s3/"
    post_res = client.post("/api/shorten", json={"url": target, "custom_code": "s3-redirect"})
    assert post_res.status_code == 201

    # Request redirection without following redirect automatically
    redirect_res = client.get("/s3-redirect", follow_redirects=False)
    assert redirect_res.status_code == 307
    assert redirect_res.headers["location"] == target


def test_redirect_non_existing_code_returns_404():
    """Verify GET /{short_code} returns 404 if code is not in database."""
    response = client.get("/not-found-xyz", follow_redirects=False)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

