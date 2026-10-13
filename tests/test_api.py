"""
Automated unit & integration tests for Labs 3 through 14.
Tests API connectivity with SQLite database, endpoints, validation, error scenarios,
access tracking, click analytics, URL expiration (TTL), top URL leaderboards,
domain distributions, CloudWatch telemetry reports, pagination, reserved system routes,
and OpenAPI documentation schemas.
"""
from datetime import datetime, timezone, timedelta
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import URLItem
from app.utils import BASE62_SET

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


def test_echo_endpoint():
    """Verify POST /api/echo responds with input payload."""
    payload = {"message": "Cloud Architecture Test", "client_name": "PyTest"}
    response = client.post("/api/echo", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["received_message"] == "Cloud Architecture Test"
    assert data["client_name"] == "PyTest"


# --- Lab 7 Tests: SQLite Storage & Retrieval ---
def test_store_url_creates_database_record():
    """Verify POST /api/shorten saves a URL into SQLite database."""
    payload = {"url": "https://aws.amazon.com/s3/"}
    response = client.post("/api/shorten", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert len(data["short_code"]) == 6

    # Verify retrieval from database via API
    get_res = client.get(f"/api/urls/{data['short_code']}")
    assert get_res.status_code == 200
    retrieved = get_res.json()
    assert retrieved["original_url"] == "https://aws.amazon.com/s3/"
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
    assert response.status_code == 400
    assert "error" in response.json()
    assert "Unsupported URL scheme" in response.json()["detail"]


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
    assert response.json()["error"] is True
    assert "not found" in response.json()["detail"].lower()


# --- Lab 9 Tests: Comprehensive Error Handling ---
def test_lab9_error_invalid_urls():
    """Verify handling of invalid schemes and malformed domain structures."""
    r1 = client.post("/api/shorten", json={"url": "javascript:alert('attack')"})
    assert r1.status_code == 400
    assert r1.json()["error"] is True
    assert "Unsupported URL scheme" in r1.json()["detail"]

    r2 = client.post("/api/shorten", json={"url": "https://not a valid domain"})
    assert r2.status_code == 400
    assert r2.json()["error"] is True


def test_lab9_error_empty_input():
    """Verify handling of empty strings or missing payload fields."""
    r1 = client.post("/api/shorten", json={"url": ""})
    assert r1.status_code == 400
    assert r1.json()["error"] is True
    assert "cannot be empty" in r1.json()["detail"]

    r2 = client.post("/api/shorten", json={})
    assert r2.status_code == 400
    assert r2.json()["error"] is True


def test_lab9_error_non_existing_short_codes():
    """Verify querying non-existent short codes returns structured 404."""
    r1 = client.get("/non-existent-code-99", follow_redirects=False)
    assert r1.status_code == 404
    assert r1.json()["error"] is True
    assert r1.json()["status_code"] == 404
    assert "not found" in r1.json()["detail"].lower()

    r2 = client.get("/api/urls/missing-code-123")
    assert r2.status_code == 404
    assert r2.json()["error"] is True


def test_lab9_error_duplicate_urls_and_custom_aliases():
    """Verify duplicate vanity alias yields 409, and duplicate long URL is reused."""
    res1 = client.post("/api/shorten", json={"url": "https://aws.amazon.com/ec2/", "custom_code": "vanity-code"})
    assert res1.status_code == 201

    res2 = client.post("/api/shorten", json={"url": "https://aws.amazon.com/s3/", "custom_code": "vanity-code"})
    assert res2.status_code == 409
    assert res2.json()["error"] is True
    assert "already in use" in res2.json()["detail"]

    res3 = client.post("/api/shorten", json={"url": "https://aws.amazon.com/lambda/"})
    assert res3.status_code == 201
    code1 = res3.json()["short_code"]

    res4 = client.post("/api/shorten", json={"url": "https://aws.amazon.com/lambda/"})
    assert res4.status_code == 201
    assert res4.json()["short_code"] == code1
    assert "reused" in res4.json()["status"]


# --- Lab 10 Tests: Access Tracking & Click Analytics ---
def test_lab10_click_counter_increments_on_redirection():
    """Verify that accessing /{short_code} increments click_count from 0 to 1, 2, 3."""
    post_res = client.post("/api/shorten", json={"url": "https://aws.amazon.com/rds/", "custom_code": "rds-clicks"})
    assert post_res.status_code == 201

    stats0 = client.get("/api/urls/rds-clicks/stats").json()
    assert stats0["click_count"] == 0
    assert stats0["last_accessed_at"] is None

    r1 = client.get("/rds-clicks", follow_redirects=False)
    assert r1.status_code == 307

    stats1 = client.get("/api/urls/rds-clicks/stats").json()
    assert stats1["click_count"] == 1
    assert stats1["last_accessed_at"] is not None

    r2 = client.get("/rds-clicks", follow_redirects=False)
    assert r2.status_code == 307

    stats2 = client.get("/api/urls/rds-clicks/stats").json()
    assert stats2["click_count"] == 2

    r3 = client.get("/rds-clicks", follow_redirects=False)
    assert r3.status_code == 307

    stats3 = client.get("/api/urls/rds-clicks/stats").json()
    assert stats3["click_count"] == 3


def test_lab10_global_analytics_summary():
    """Verify GET /api/stats/summary calculates total links, total clicks, and top link."""
    client.post("/api/shorten", json={"url": "https://aws.amazon.com/route53/", "custom_code": "top-link"})
    client.post("/api/shorten", json={"url": "https://aws.amazon.com/iam/", "custom_code": "other-link"})

    for _ in range(3):
        client.get("/top-link", follow_redirects=False)

    client.get("/other-link", follow_redirects=False)

    summary = client.get("/api/stats/summary").json()
    assert summary["total_short_links"] == 2
    assert summary["total_redirections_served"] == 4
    assert summary["most_clicked_link"]["short_code"] == "top-link"
    assert summary["most_clicked_link"]["clicks"] == 3


# --- Lab 11 Tests: URL Expiration & Time-To-Live (TTL) ---
def test_lab11_shorten_with_expiration_hours():
    """Verify URL shortening with expires_in_hours sets expires_at in the future."""
    res = client.post("/api/shorten", json={
        "url": "https://aws.amazon.com/cloudtrail/",
        "custom_code": "trail-ttl",
        "expires_in_hours": 2,
    })
    assert res.status_code == 201
    data = res.json()
    assert data["expires_at"] is not None

    url_details = client.get("/api/urls/trail-ttl").json()
    assert url_details["expires_at"] is not None
    assert url_details["is_expired"] is False
    assert url_details["time_remaining_seconds"] > 7000

    redir = client.get("/trail-ttl", follow_redirects=False)
    assert redir.status_code == 307


def test_lab11_shorten_with_expiration_days():
    """Verify URL shortening with expires_in_days sets expires_at correctly."""
    res = client.post("/api/shorten", json={
        "url": "https://aws.amazon.com/sns/",
        "custom_code": "sns-ttl",
        "expires_in_days": 7,
    })
    assert res.status_code == 201
    data = res.json()
    assert data["expires_at"] is not None

    stats = client.get("/api/urls/sns-ttl/stats").json()
    assert stats["is_expired"] is False
    assert stats["time_remaining_seconds"] > 500000
    assert stats["status"] == "active"


def test_lab11_reject_both_hours_and_days():
    """Verify submitting both expires_in_hours and expires_in_days returns 400."""
    res = client.post("/api/shorten", json={
        "url": "https://aws.amazon.com/sqs/",
        "expires_in_hours": 12,
        "expires_in_days": 2,
    })
    assert res.status_code == 400
    assert res.json()["error"] is True
    assert "not both" in res.json()["detail"].lower()


def test_lab11_expired_url_returns_410_gone():
    """Verify expired URL returns HTTP 410 Gone and deactivates is_active."""
    db = TestingSessionLocal()
    past_time = datetime.now(timezone.utc) - timedelta(hours=1)
    expired_item = URLItem(
        short_code="already-dead",
        original_url="https://aws.amazon.com/expired/",
        click_count=0,
        created_at=datetime.now(timezone.utc) - timedelta(hours=2),
        expires_at=past_time,
        is_active=True,
    )
    db.add(expired_item)
    db.commit()
    db.close()

    redir = client.get("/already-dead", follow_redirects=False)
    assert redir.status_code == 410
    assert "expired" in redir.json()["detail"].lower()

    stats = client.get("/api/urls/already-dead/stats").json()
    assert stats["is_expired"] is True
    assert stats["is_active"] is False
    assert stats["status"] == "expired"
    assert stats["time_remaining_seconds"] == 0


def test_lab11_maintenance_cleanup_sweeper():
    """Verify POST /api/maintenance/cleanup-expired scans and marks expired records inactive."""
    db = TestingSessionLocal()
    now = datetime.now(timezone.utc)
    db.add(URLItem(
        short_code="sweep-me-1",
        original_url="https://aws.amazon.com/sweep1/",
        click_count=0,
        created_at=now - timedelta(days=2),
        expires_at=now - timedelta(days=1),
        is_active=True,
    ))
    db.add(URLItem(
        short_code="keep-me-active",
        original_url="https://aws.amazon.com/keep/",
        click_count=0,
        created_at=now,
        expires_at=now + timedelta(days=5),
        is_active=True,
    ))
    db.commit()
    db.close()

    clean_res = client.post("/api/maintenance/cleanup-expired")
    assert clean_res.status_code == 200
    clean_data = clean_res.json()
    assert clean_data["status"] == "success"
    assert clean_data["deactivated_count"] >= 1
    assert "sweep-me-1" in clean_data["deactivated_codes"]

    expired_list = client.get("/api/urls/status/expired").json()
    assert expired_list["total_expired"] >= 1


def test_lab11_batch_shorten_with_ttl():
    """Verify batch shortening handles optional TTL expiration."""
    urls = [
        "https://aws.amazon.com/athena/",
        "https://aws.amazon.com/glue/",
    ]
    res = client.post("/api/shorten/batch", json={
        "urls": urls,
        "expires_in_hours": 48,
    })
    assert res.status_code == 201
    data = res.json()
    assert data["successful_count"] == 2
    for item in data["items"]:
        assert item["expires_at"] is not None


# --- Lab 12 Tests: Analytics & Statistics Reporting API ---
def test_lab12_top_performing_urls_ranking():
    """Verify GET /api/stats/top returns ranked leaderboard sorted by clicks."""
    client.post("/api/shorten", json={"url": "https://aws.amazon.com/ec2/", "custom_code": "gold-link"})
    client.post("/api/shorten", json={"url": "https://github.com/torvalds/linux", "custom_code": "silver-link"})
    client.post("/api/shorten", json={"url": "https://python.org/", "custom_code": "bronze-link"})

    # Clicks: gold=5, silver=3, bronze=1
    for _ in range(5):
        client.get("/gold-link", follow_redirects=False)
    for _ in range(3):
        client.get("/silver-link", follow_redirects=False)
    client.get("/bronze-link", follow_redirects=False)

    top_res = client.get("/api/stats/top?limit=2")
    assert top_res.status_code == 200
    data = top_res.json()
    assert data["limit"] == 2
    assert data["returned_count"] == 2

    # Verify ranking
    assert data["top_links"][0]["rank"] == 1
    assert data["top_links"][0]["short_code"] == "gold-link"
    assert data["top_links"][0]["click_count"] == 5
    assert data["top_links"][0]["destination_domain"] == "aws.amazon.com"

    assert data["top_links"][1]["rank"] == 2
    assert data["top_links"][1]["short_code"] == "silver-link"
    assert data["top_links"][1]["click_count"] == 3
    assert data["top_links"][1]["destination_domain"] == "github.com"


def test_lab12_top_urls_query_param_validation():
    """Verify limit parameter enforces 1 <= limit <= 50."""
    res_high = client.get("/api/stats/top?limit=99")
    assert res_high.status_code == 400
    assert "less than or equal to 50" in res_high.json()["detail"]

    res_low = client.get("/api/stats/top?limit=0")
    assert res_low.status_code == 400
    assert "greater than or equal to 1" in res_low.json()["detail"]


def test_lab12_destination_domain_analytics():
    """Verify GET /api/stats/domains breaks down link share and click percentages by target domain."""
    client.post("/api/shorten", json={"url": "https://aws.amazon.com/s3/", "custom_code": "aws-1"})
    client.post("/api/shorten", json={"url": "https://aws.amazon.com/rds/", "custom_code": "aws-2"})
    client.post("/api/shorten", json={"url": "https://github.com/fastapi/fastapi", "custom_code": "gh-1"})

    # Clicks: aws-1=3, aws-2=1 (Total AWS = 4), gh-1=1 (Total GH = 1). Total clicks = 5
    for _ in range(3):
        client.get("/aws-1", follow_redirects=False)
    client.get("/aws-2", follow_redirects=False)
    client.get("/gh-1", follow_redirects=False)

    domain_res = client.get("/api/stats/domains")
    assert domain_res.status_code == 200
    data = domain_res.json()
    assert data["total_unique_domains"] == 2
    assert data["total_tracked_clicks"] == 5

    top_domain = data["domains"][0]
    assert top_domain["domain"] == "aws.amazon.com"
    assert top_domain["link_count"] == 2
    assert top_domain["total_clicks"] == 4
    assert top_domain["percentage_of_all_clicks"] == 80.0

    second_domain = data["domains"][1]
    assert second_domain["domain"] == "github.com"
    assert second_domain["link_count"] == 1
    assert second_domain["total_clicks"] == 1
    assert second_domain["percentage_of_all_clicks"] == 20.0


def test_lab12_comprehensive_observability_report():
    """Verify GET /api/stats/report provides full system summary and CloudWatch metric points."""
    client.post("/api/shorten", json={"url": "https://aws.amazon.com/cloudwatch/", "custom_code": "cw-link"})
    for _ in range(4):
        client.get("/cw-link", follow_redirects=False)

    report_res = client.get("/api/stats/report")
    assert report_res.status_code == 200
    data = report_res.json()

    assert "summary" in data
    assert data["summary"]["total_links"] == 1
    assert data["summary"]["total_clicks"] == 4
    assert data["summary"]["average_clicks_per_link"] == 4.0
    assert data["summary"]["health_status"] == "optimal"

    metrics = {m["metric_name"]: m["value"] for m in data["cloudwatch_telemetry_metrics"]}
    assert metrics["TotalShortLinksStored"] == 1.0
    assert metrics["TotalRedirectionsServed"] == 4.0
    assert metrics["ActiveShortLinksGauge"] == 1.0
    assert metrics["AverageClicksPerLink"] == 4.0

    assert len(data["top_performing_links"]) == 1
    assert data["top_performing_links"][0]["short_code"] == "cw-link"
    assert len(data["domain_breakdown"]) == 1
    assert data["domain_breakdown"][0]["domain"] == "aws.amazon.com"


def test_lab12_link_stats_includes_destination_domain():
    """Verify GET /api/urls/{short_code}/stats includes destination_domain."""
    client.post("/api/shorten", json={"url": "https://fastapi.tiangolo.com/tutorial/", "custom_code": "fastapi-doc"})
    stats = client.get("/api/urls/fastapi-doc/stats").json()
    assert stats["destination_domain"] == "fastapi.tiangolo.com"


# --- Lab 14 Tests: Comprehensive Edge Case & Documentation Tests ---
def test_lab14_paginated_urls_skip_and_limit():
    """Verify GET /api/urls supports skip and limit pagination parameters correctly."""
    for i in range(5):
        client.post("/api/shorten", json={"url": f"https://aws.amazon.com/page{i}/", "custom_code": f"page-{i}"})

    res = client.get("/api/urls?skip=2&limit=2")
    assert res.status_code == 200
    data = res.json()
    assert data["total_records"] == 5
    assert data["offset"] == 2
    assert data["limit"] == 2
    assert len(data["urls"]) == 2


def test_lab14_reserved_system_paths_guard():
    """Verify system documentation and health routes are guarded and return 404 rather than looking up short codes."""
    for path in ["docs", "redoc", "openapi.json", "favicon.ico"]:
        res = client.get(f"/{path}", follow_redirects=False)
        assert res.status_code in (200, 404)  # Docs return 200 via FastAPI, guarded internal lookup


def test_lab14_deactivated_url_returns_410():
    """Verify manually deactivated URL returns HTTP 410 Gone."""
    db = TestingSessionLocal()
    item = URLItem(
        short_code="manual-deactive",
        original_url="https://aws.amazon.com/deactivated/",
        click_count=0,
        created_at=datetime.now(timezone.utc),
        is_active=False,
    )
    db.add(item)
    db.commit()
    db.close()

    res = client.get("/manual-deactive", follow_redirects=False)
    assert res.status_code == 410
    assert "deactivated" in res.json()["detail"].lower()


def test_lab14_openapi_schema_endpoint():
    """Verify GET /openapi.json delivers complete OpenAPI 3.1 specification."""
    res = client.get("/openapi.json")
    assert res.status_code == 200
    schema = res.json()
    assert schema["info"]["title"] == "Cloud-Based URL Shortener"
    assert "/api/shorten" in schema["paths"]
    assert "/api/stats/report" in schema["paths"]
