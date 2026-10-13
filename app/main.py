"""
Cloud-Based URL Shortener API Service.
Lab 3: Core API Endpoints (Health, Echo, Root)
Lab 4: URL Intake and Validation Endpoints
Lab 5: Base62 Short Code Generation Endpoints
Lab 6: SQLite Database Engine & Lifespan Migrations
Lab 7: Persistent SQLite URL Storage & Retrieval Endpoints
Lab 8: URL Redirection (HTTP 307 Temporary Redirect)
Lab 9: Global Exception Handling & Error Management
Lab 10: Access Tracking & Real-Time Click Analytics
Lab 11: URL Expiration & Time-To-Live (TTL) Management
"""
from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import (
    URLBatchRequest,
    URLBatchResponse,
    URLDatabaseRecord,
    URLIntakeRequest,
    URLIntakeResponse,
    URLItem,
    URLShortenRequest,
    URLShortenResponse,
    URLStatsResponse,
)
from app.utils import (
    generate_short_code,
    is_valid_custom_code,
    is_valid_url,
)
from pydantic import BaseModel, Field


# ==========================================
# TTL & Expiration Helpers (Lab 11)
# ==========================================
def is_url_expired(record: URLItem) -> bool:
    """
    Checks if a URLItem has an expiration date set and has passed it in UTC.
    Safely handles both timezone-naive and timezone-aware datetimes from SQLite.
    """
    if not record.expires_at:
        return False
    exp = record.expires_at
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) > exp


def get_time_remaining_seconds(record: URLItem) -> Optional[int]:
    """
    Calculates remaining seconds until expiration.
    Returns 0 if already expired, None if no expiration was set.
    """
    if not record.expires_at:
        return None
    exp = record.expires_at
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    diff = (exp - datetime.now(timezone.utc)).total_seconds()
    return max(0, int(diff))


# ==========================================
# Application Lifespan (Database Initializer)
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Ensures SQLite tables are created automatically when the FastAPI app starts.
    In cloud environments, this mirrors automated schema migrations (e.g., Flyway, Alembic)
    running during container boot on AWS ECS or AWS App Runner.
    """
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Cloud-Based URL Shortener",
    description=(
        "Production-ready URL Shortener simulation built with FastAPI, SQLite, "
        "and Base62 collision-resistant hashing. Designed to reflect enterprise "
        "AWS Cloud Architecture (Route 53 -> CloudFront -> ALB -> ECS -> RDS/DynamoDB)."
    ),
    version="1.1.0",
    lifespan=lifespan,
)


# ==========================================
# Global Exception Handlers (Lab 9)
# ==========================================
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Global handler for standard HTTPExceptions.
    Returns a consistent JSON error schema across all endpoints.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "detail": exc.detail,
            "path": str(request.url.path),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Global handler for request body / parameter validation failures.
    Translates Pydantic errors into human-readable 400 Bad Request responses.
    """
    error_messages = []
    for err in exc.errors():
        field = " -> ".join(str(loc) for loc in err.get("loc", []))
        msg = err.get("msg", "Validation error")
        error_messages.append(f"Field '{field}': {msg}")

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": True,
            "status_code": status.HTTP_400_BAD_REQUEST,
            "detail": "; ".join(error_messages),
            "path": str(request.url.path),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


# ==========================================
# Pydantic Schemas for Echo/Testing
# ==========================================
class EchoRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500, description="Message to be echoed")
    client_name: Optional[str] = Field(default="Anonymous", description="Identifier of the caller")


class EchoResponse(BaseModel):
    status: str
    received_message: str
    client_name: str
    timestamp: str
    cloud_region_simulation: str


# ==========================================
# 1. Root / Service Metadata Endpoint (GET)
# ==========================================
@app.get(
    "/",
    tags=["Core"],
    summary="Service Welcome and Cloud Metadata",
    description="Returns welcome message, cloud architecture mapping, and service status.",
    status_code=status.HTTP_200_OK,
)
def root(db: Session = Depends(get_db)):
    persisted_count = db.query(URLItem).count()
    return {
        "service": "Cloud-Based URL Shortener",
        "status": "online",
        "version": "1.1.0",
        "aws_architecture_tier": "Compute Tier (Simulated ECS Fargate / EC2)",
        "database_tier": "Storage Tier (SQLite simulating Amazon RDS)",
        "total_persisted_urls": persisted_count,
        "docs_url": "/docs",
        "redoc_url": "/redoc",
    }


# ==========================================
# 2. Health Check Probe (GET) - Lab 3
# ==========================================
@app.get(
    "/health",
    tags=["Monitoring"],
    summary="Application & Database Health Check",
    description="Used by Cloud Load Balancers (like AWS ALB) to monitor container and database connection health.",
    status_code=status.HTTP_200_OK,
)
def health_check(db: Session = Depends(get_db)):
    count = db.query(URLItem).count()
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": "sqlite_connected",
        "persisted_records_count": count,
        "compute_instance": "local-simulation-node-1",
    }


# ==========================================
# 3. Echo / Test Endpoint (POST)
# ==========================================
@app.post(
    "/api/echo",
    response_model=EchoResponse,
    tags=["Testing"],
    summary="Echo Test Endpoint",
    description="Accepts a JSON payload via HTTP POST and returns an enriched response with server timestamp.",
    status_code=status.HTTP_200_OK,
)
def echo_payload(payload: EchoRequest):
    return EchoResponse(
        status="success",
        received_message=payload.message,
        client_name=payload.client_name,
        timestamp=datetime.now(timezone.utc).isoformat(),
        cloud_region_simulation="us-east-1",
    )


# ==========================================
# 4. Store URL Through API (POST) - Lab 7 & Lab 11
# ==========================================
@app.post(
    "/api/shorten",
    response_model=URLShortenResponse,
    tags=["URL Shortener"],
    summary="Shorten and Store URL in SQLite with Optional Expiration",
    description=(
        "Validates long URL, supports optional custom vanity alias and expiration (TTL), "
        "and persists the record into the database."
    ),
    status_code=status.HTTP_201_CREATED,
)
def create_and_store_url(
    payload: URLShortenRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    now_utc = datetime.now(timezone.utc)

    # 1. Calculate expiration (TTL) if requested (Lab 11)
    expires_at = None
    if payload.expires_in_hours is not None:
        expires_at = now_utc + timedelta(hours=payload.expires_in_hours)
    elif payload.expires_in_days is not None:
        expires_at = now_utc + timedelta(days=payload.expires_in_days)

    # 2. Custom vanity alias check
    if payload.custom_code:
        code = payload.custom_code
        existing = db.query(URLItem).filter(URLItem.short_code == code).first()
        if existing:
            # Check if existing custom code is already expired
            if is_url_expired(existing):
                existing.is_active = False
                db.commit()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Custom short code '{code}' is already in use. Please select a different vanity alias.",
            )
        code_type = "custom_alias"
    else:
        # 3. Check for duplicate long URL (Idempotent cloud design)
        # Only reuse if no custom expiration was requested
        if payload.expires_in_hours is None and payload.expires_in_days is None:
            existing_url = db.query(URLItem).filter(
                URLItem.original_url == payload.url,
                URLItem.is_active == True,
            ).first()

            if existing_url:
                if is_url_expired(existing_url):
                    existing_url.is_active = False
                    db.commit()
                else:
                    base_url = str(request.base_url).rstrip("/")
                    return URLShortenResponse(
                        status="success (reused duplicate)",
                        short_code=existing_url.short_code,
                        short_url=f"{base_url}/{existing_url.short_code}",
                        original_url=existing_url.original_url,
                        created_at=existing_url.created_at.isoformat(),
                        expires_at=existing_url.expires_at.isoformat() if existing_url.expires_at else None,
                        code_type="reused_existing",
                    )

        # 4. Generate collision-resistant Base62 code
        code_type = "random_base62"
        max_attempts = 10
        code = None
        for _ in range(max_attempts):
            candidate = generate_short_code(length=6)
            exists = db.query(URLItem).filter(URLItem.short_code == candidate).first()
            if not exists:
                code = candidate
                break

        if not code:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate unique short code. Please try again.",
            )

    # 5. Create ORM instance and persist to SQLite
    new_url = URLItem(
        short_code=code,
        original_url=payload.url,
        click_count=0,
        created_at=now_utc,
        expires_at=expires_at,
        is_active=True,
    )
    db.add(new_url)
    db.commit()
    db.refresh(new_url)

    # 6. Construct complete short URL using request host
    base_url = str(request.base_url).rstrip("/")
    short_url = f"{base_url}/{code}"

    return URLShortenResponse(
        status="success",
        short_code=code,
        short_url=short_url,
        original_url=payload.url,
        created_at=new_url.created_at.isoformat(),
        expires_at=new_url.expires_at.isoformat() if new_url.expires_at else None,
        code_type=code_type,
    )


# ==========================================
# 5. Batch Store Multiple URLs (POST) - Lab 7 & Lab 11
# ==========================================
@app.post(
    "/api/shorten/batch",
    response_model=URLBatchResponse,
    tags=["URL Shortener"],
    summary="Batch Shorten and Store Multiple URLs with Optional TTL",
    description="Processes and saves multiple URLs into SQLite in a single atomic database transaction.",
    status_code=status.HTTP_201_CREATED,
)
def batch_store_urls(
    payload: URLBatchRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    base_url = str(request.base_url).rstrip("/")
    now_utc = datetime.now(timezone.utc)
    results = []

    expires_at = None
    if payload.expires_in_hours is not None:
        expires_at = now_utc + timedelta(hours=payload.expires_in_hours)
    elif payload.expires_in_days is not None:
        expires_at = now_utc + timedelta(days=payload.expires_in_days)

    for url_str in payload.urls:
        valid, _ = is_valid_url(url_str)
        if not valid:
            continue

        # Generate unique code
        code = None
        for _ in range(10):
            candidate = generate_short_code(length=6)
            if not db.query(URLItem).filter(URLItem.short_code == candidate).first():
                code = candidate
                break

        if code:
            item = URLItem(
                short_code=code,
                original_url=url_str.strip(),
                click_count=0,
                created_at=now_utc,
                expires_at=expires_at,
                is_active=True,
            )
            db.add(item)
            db.flush()

            results.append(
                URLShortenResponse(
                    status="success",
                    short_code=code,
                    short_url=f"{base_url}/{code}",
                    original_url=url_str.strip(),
                    created_at=now_utc.isoformat(),
                    expires_at=expires_at.isoformat() if expires_at else None,
                    code_type="batch_random_base62",
                )
            )

    db.commit()

    return URLBatchResponse(
        total_requested=len(payload.urls),
        successful_count=len(results),
        items=results,
    )


# ==========================================
# 6. Retrieve Stored URLs (GET) - Lab 7 & Lab 11
# ==========================================
@app.get(
    "/api/urls",
    tags=["URL Shortener"],
    summary="Retrieve All Stored URLs from SQLite",
    description="Queries and returns all persistent URL records from the SQLite database with expiration status.",
)
def retrieve_all_stored_urls(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    records = db.query(URLItem).offset(skip).limit(limit).all()
    total = db.query(URLItem).count()

    return {
        "total_records": total,
        "offset": skip,
        "limit": limit,
        "urls": [
            {
                "id": r.id,
                "short_code": r.short_code,
                "original_url": r.original_url,
                "click_count": r.click_count,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "expires_at": r.expires_at.isoformat() if r.expires_at else None,
                "is_expired": is_url_expired(r),
                "time_remaining_seconds": get_time_remaining_seconds(r),
                "is_active": r.is_active and not is_url_expired(r),
            }
            for r in records
        ],
    }


# ==========================================
# 7. Retrieve Stored URL by Short Code (GET) - Lab 7 & Lab 11
# ==========================================
@app.get(
    "/api/urls/{short_code}",
    tags=["URL Shortener"],
    summary="Retrieve Stored URL Record by Short Code",
    description="Queries SQLite for a specific short code and returns its full metadata and TTL status.",
)
def retrieve_stored_url_by_code(
    short_code: str,
    db: Session = Depends(get_db),
):
    record = db.query(URLItem).filter(URLItem.short_code == short_code).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Short code '{short_code}' not found in SQLite database.",
        )

    expired = is_url_expired(record)

    return {
        "id": record.id,
        "short_code": record.short_code,
        "original_url": record.original_url,
        "click_count": record.click_count,
        "created_at": record.created_at.isoformat() if record.created_at else None,
        "last_accessed_at": record.last_accessed_at.isoformat() if record.last_accessed_at else None,
        "expires_at": record.expires_at.isoformat() if record.expires_at else None,
        "is_expired": expired,
        "time_remaining_seconds": get_time_remaining_seconds(record),
        "is_active": record.is_active and not expired,
    }


# ==========================================
# 8. URL Redirection & Access Tracking (GET) - Lab 8, 10, & 11
# ==========================================
@app.get(
    "/{short_code}",
    response_class=RedirectResponse,
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    tags=["URL Redirection"],
    summary="Redirect Short Code to Original Website",
    description=(
        "Looks up the short code in SQLite, validates expiration (TTL), "
        "increments access counters, and issues an HTTP 307 Temporary Redirect."
    ),
)
def redirect_to_original_url(
    short_code: str,
    db: Session = Depends(get_db),
):
    """
    Lab 8, 10 & 11: URL Redirection + Access Tracking + Expiration Check
    1. Retrieve original URL from SQLite using indexed short_code.
    2. Check expiration (TTL): If expired, mark is_active=False and return HTTP 410 Gone.
    3. Check active status.
    4. Atomically increment click_count and record last_accessed_at timestamp.
    5. Issue HTTP 307 Temporary Redirect.
    """
    # Exclude system documentation paths
    if short_code in ("docs", "redoc", "openapi.json", "favicon.ico", "health"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")

    record = db.query(URLItem).filter(URLItem.short_code == short_code).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Short code '{short_code}' not found.",
        )

    # Lab 11: Expiration check (TTL)
    if is_url_expired(record):
        if record.is_active:
            record.is_active = False
            db.commit()
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail=f"This short URL has expired on {record.expires_at.isoformat()} and is no longer accessible.",
        )

    if not record.is_active:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="This short URL has been deactivated.",
        )

    # Lab 10: Access Tracking
    record.click_count += 1
    record.last_accessed_at = datetime.now(timezone.utc)
    db.commit()

    return RedirectResponse(
        url=record.original_url,
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    )


# ==========================================
# 9. Access Tracking & URL Statistics (GET) - Lab 10 & 11
# ==========================================
@app.get(
    "/api/urls/{short_code}/stats",
    response_model=URLStatsResponse,
    tags=["Analytics & Statistics"],
    summary="Get Access Tracking, Click Statistics, and TTL Status",
    description="Displays click count, creation date, last access timestamp, and TTL expiration for a short link.",
)
def get_url_statistics(
    short_code: str,
    db: Session = Depends(get_db),
):
    record = db.query(URLItem).filter(URLItem.short_code == short_code).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Short code '{short_code}' not found in database.",
        )

    expired = is_url_expired(record)
    status_str = "expired" if expired else ("active" if record.is_active else "inactive")

    return URLStatsResponse(
        short_code=record.short_code,
        original_url=record.original_url,
        click_count=record.click_count,
        created_at=record.created_at,
        last_accessed_at=record.last_accessed_at,
        expires_at=record.expires_at,
        is_active=record.is_active and not expired,
        is_expired=expired,
        time_remaining_seconds=get_time_remaining_seconds(record),
        status=status_str,
    )


# ==========================================
# 10. Global Analytics Summary (GET) - Lab 10
# ==========================================
@app.get(
    "/api/stats/summary",
    tags=["Analytics & Statistics"],
    summary="Service-Wide Analytics Summary",
    description="Displays total links stored, total clicks across all links, and the most clicked link.",
)
def get_global_statistics(db: Session = Depends(get_db)):
    total_links = db.query(URLItem).count()
    total_clicks = db.query(func.sum(URLItem.click_count)).scalar() or 0
    top_link = db.query(URLItem).order_by(URLItem.click_count.desc()).first()

    return {
        "total_short_links": total_links,
        "total_redirections_served": total_clicks,
        "most_clicked_link": {
            "short_code": top_link.short_code if top_link else None,
            "original_url": top_link.original_url if top_link else None,
            "clicks": top_link.click_count if top_link else 0,
        } if top_link else None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ==========================================
# 11. TTL Maintenance & Cleanup (POST/GET) - Lab 11
# ==========================================
@app.post(
    "/api/maintenance/cleanup-expired",
    tags=["Maintenance & TTL"],
    summary="Trigger Automated TTL Maintenance Cleanup",
    description=(
        "Simulates an AWS Lambda scheduled worker (triggered by Amazon EventBridge / CloudWatch) "
        "that scans the database and deactivates expired links."
    ),
)
def cleanup_expired_urls(db: Session = Depends(get_db)):
    """
    Simulates automated background TTL reaper in AWS:
    1. Scans for active links whose expiration timestamp is in the past.
    2. Marks is_active = False.
    3. Commits the transaction in bulk.
    """
    records = db.query(URLItem).filter(
        URLItem.is_active == True,
        URLItem.expires_at.isnot(None),
    ).all()

    deactivated_count = 0
    deactivated_codes = []
    for r in records:
        if is_url_expired(r):
            r.is_active = False
            deactivated_count += 1
            deactivated_codes.append(r.short_code)

    if deactivated_count > 0:
        db.commit()

    return {
        "status": "success",
        "deactivated_count": deactivated_count,
        "deactivated_codes": deactivated_codes,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cloud_architecture_simulation": "Amazon EventBridge -> AWS Lambda TTL Reaper",
    }


@app.get(
    "/api/urls/status/expired",
    tags=["Maintenance & TTL"],
    summary="List All Expired URLs",
    description="Queries all URLs that have passed their expiration timestamp.",
)
def list_expired_urls(db: Session = Depends(get_db)):
    records = db.query(URLItem).filter(URLItem.expires_at.isnot(None)).all()
    expired = [r for r in records if is_url_expired(r)]

    return {
        "total_expired": len(expired),
        "expired_urls": [
            {
                "short_code": r.short_code,
                "original_url": r.original_url,
                "expires_at": r.expires_at.isoformat() if r.expires_at else None,
                "is_active": r.is_active,
            }
            for r in expired
        ],
    }
