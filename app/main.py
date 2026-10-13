"""
FastAPI application entrypoint for Cloud URL Shortener.
Lab 3: Basic Web API (GET & POST Endpoints)
Lab 4: Accept Long URLs & URL Validation
Lab 5: Generate Unique Short Codes & Batch Operations
Lab 6 & 7: SQLite Database Integration (Persistent Storage via API)
"""
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import List, Optional
from urllib.parse import urlparse

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db, init_db
from app.models import (
    URLBatchRequest,
    URLBatchResponse,
    URLDatabaseRecord,
    URLIntakeRequest,
    URLIntakeResponse,
    URLItem,
    URLShortenRequest,
    URLShortenResponse,
)
from app.utils import (
    generate_short_code,
    hash_url_to_code,
    is_valid_custom_code,
    is_valid_url,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager: initializes SQLite database schema on startup."""
    init_db()
    yield


# Initialize FastAPI application
app = FastAPI(
    title="Cloud-Based URL Shortener API",
    description="A cloud-native URL shortening service simulation. Connected to persistent SQLite database storage, featuring RESTful endpoints, health probes, and interactive OpenAPI documentation.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# Pydantic Schemas for Lab 3 Echo endpoints
class EchoRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500, description="Message to send to the server", examples=["Hello Cloud API!"])
    client_name: str = Field(default="Browser/Postman Client", max_length=100, description="Identifier of the client calling the API")


class EchoResponse(BaseModel):
    status: str
    received_message: str
    client_name: str
    timestamp: str
    cloud_region_simulation: str


# ==========================================
# 1. Root & Discovery Endpoint (GET)
# ==========================================
@app.get(
    "/",
    tags=["General"],
    summary="Root Service Info",
    description="Returns metadata about the URL Shortener service and available API documentation.",
)
def read_root(db: Session = Depends(get_db)):
    url_count = db.query(URLItem).count()
    return {
        "service": "Cloud-Based URL Shortener",
        "version": "1.0.0",
        "status": "online",
        "cloud_provider_simulation": "AWS (App Runner / ECS + RDS/DynamoDB)",
        "total_persisted_urls": url_count,
        "docs_url": "/docs",
        "redoc_url": "/redoc",
    }


# ==========================================
# 2. Cloud Health Check Endpoint (GET)
# ==========================================
@app.get(
    "/health",
    tags=["Monitoring"],
    summary="Application & Database Health Check",
    description="Used by Cloud Load Balancers (like AWS ALB) to monitor container and database connection health.",
    status_code=status.HTTP_200_OK,
)
def health_check(db: Session = Depends(get_db)):
    # Verify live database query execution
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
# 4. Store URL Through API (POST) - Lab 7
# ==========================================
@app.post(
    "/api/shorten",
    response_model=URLShortenResponse,
    tags=["URL Shortener"],
    summary="Shorten and Store URL in SQLite",
    description="Validates long URL, generates a unique Base62 code, and persists the record into SQLite database.",
    status_code=status.HTTP_201_CREATED,
)
def create_and_store_url(
    payload: URLShortenRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Connects API to SQLite:
    1. Validates custom code or generates random 6-character Base62 code.
    2. Enforces uniqueness constraint.
    3. Persists record to SQLite disk.
    """
    # 1. Custom vanity alias check
    if payload.custom_code:
        code = payload.custom_code
        existing = db.query(URLItem).filter(URLItem.short_code == code).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Custom short code '{code}' is already taken in database. Please choose another.",
            )
        code_type = "custom_alias"
    else:
        # 2. Generate collision-resistant Base62 code
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

    # 3. Create ORM instance and persist to SQLite
    now_utc = datetime.now(timezone.utc)
    new_url = URLItem(
        short_code=code,
        original_url=payload.url,
        click_count=0,
        created_at=now_utc,
        is_active=True,
    )
    db.add(new_url)
    db.commit()
    db.refresh(new_url)

    # 4. Construct complete short URL using request host
    base_url = str(request.base_url).rstrip("/")
    short_url = f"{base_url}/{code}"

    return URLShortenResponse(
        status="success",
        short_code=code,
        short_url=short_url,
        original_url=payload.url,
        created_at=new_url.created_at.isoformat(),
        code_type=code_type,
    )


# ==========================================
# 5. Batch Store Multiple URLs (POST) - Lab 7
# ==========================================
@app.post(
    "/api/shorten/batch",
    response_model=URLBatchResponse,
    tags=["URL Shortener"],
    summary="Batch Shorten and Store Multiple URLs",
    description="Processes and saves multiple URLs into SQLite in a single atomic database transaction.",
    status_code=status.HTTP_201_CREATED,
)
def batch_store_urls(
    payload: URLBatchRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    base_url = str(request.base_url).rstrip("/")
    results = []

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
            now_utc = datetime.now(timezone.utc)
            item = URLItem(
                short_code=code,
                original_url=url_str.strip(),
                click_count=0,
                created_at=now_utc,
                is_active=True,
            )
            db.add(item)
            db.flush()  # Stage in session

            results.append(
                URLShortenResponse(
                    status="success",
                    short_code=code,
                    short_url=f"{base_url}/{code}",
                    original_url=url_str.strip(),
                    created_at=now_utc.isoformat(),
                    code_type="batch_random_base62",
                )
            )

    # Commit entire batch transaction
    db.commit()

    return URLBatchResponse(
        total_requested=len(payload.urls),
        successful_count=len(results),
        items=results,
    )


# ==========================================
# 6. Retrieve Stored URLs (GET) - Lab 7
# ==========================================
@app.get(
    "/api/urls",
    tags=["URL Shortener"],
    summary="Retrieve All Stored URLs from SQLite",
    description="Queries and returns all persistent URL records from the SQLite database.",
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
                "is_active": r.is_active,
            }
            for r in records
        ],
    }


# ==========================================
# 7. Retrieve Stored URL by Short Code (GET) - Lab 7
# ==========================================
@app.get(
    "/api/urls/{short_code}",
    tags=["URL Shortener"],
    summary="Retrieve Stored URL Record by Short Code",
    description="Queries SQLite for a specific short code and returns its full metadata.",
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

    return {
        "id": record.id,
        "short_code": record.short_code,
        "original_url": record.original_url,
        "click_count": record.click_count,
        "created_at": record.created_at.isoformat() if record.created_at else None,
        "is_active": record.is_active,
    }


# ==========================================
# 8. URL Redirection Endpoint (GET) - Lab 8
# ==========================================
@app.get(
    "/{short_code}",
    response_class=RedirectResponse,
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    tags=["URL Redirection"],
    summary="Redirect Short Code to Original Website",
    description="Looks up the short code in SQLite and issues an HTTP 307 Temporary Redirect to the original destination URL.",
)
def redirect_to_original_url(
    short_code: str,
    db: Session = Depends(get_db),
):
    """
    Lab 8: URL Redirection
    1. Retrieve original URL from SQLite using indexed short_code.
    2. Validate active status.
    3. Issue HTTP 307 Temporary Redirect.
    """
    # Exclude system documentation paths if accessed
    if short_code in ("docs", "redoc", "openapi.json", "favicon.ico", "health"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")

    record = db.query(URLItem).filter(URLItem.short_code == short_code).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Short code '{short_code}' not found.",
        )

    if not record.is_active:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail=f"This short URL has been deactivated.",
        )

    return RedirectResponse(
        url=record.original_url,
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    )

