"""
Data models and Pydantic validation schemas.
Lab 4: URL Intake and Validation Schemas
Lab 5: Short Code Generation and Batch Schemas
Lab 6: SQLAlchemy URLItem ORM Table Model
Lab 10: Access Tracking and Click Statistics Schemas
Lab 11: URL Expiration and TTL Schemas
"""
from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator
from sqlalchemy import Boolean, Column, DateTime, Integer, String

from app.database import Base
from app.utils import is_valid_custom_code, is_valid_url


# ==========================================
# SQLAlchemy ORM Model (Database Table: urls)
# ==========================================
class URLItem(Base):
    """
    SQLAlchemy ORM model representing the 'urls' table in SQLite.
    In AWS, this schema maps directly to Amazon RDS (PostgreSQL/MySQL)
    or Amazon DynamoDB items with native TTL attributes.
    """
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    short_code = Column(String(16), unique=True, index=True, nullable=False)
    original_url = Column(String(2048), nullable=False)
    click_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    last_accessed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    def __repr__(self):
        return f"<URLItem(short_code='{self.short_code}', original_url='{self.original_url[:30]}...', clicks={self.click_count})>"


# ==========================================
# Pydantic Schemas for API Serialization
# ==========================================
class URLIntakeRequest(BaseModel):
    """Payload schema for submitting a long URL."""
    url: str = Field(
        ...,
        description="The full long destination URL (must start with http:// or https://)",
        examples=["https://aws.amazon.com/architecture/well-architected/"],
    )

    @field_validator("url")
    @classmethod
    def validate_url_syntax(cls, v: str) -> str:
        clean = v.strip()
        valid, reason = is_valid_url(clean)
        if not valid:
            raise ValueError(reason)
        return clean


class URLIntakeResponse(BaseModel):
    """Response returned upon successful validation of long URL."""
    status: str = "valid"
    original_url: str
    scheme: str
    domain: str
    message: str = "URL successfully validated."


class URLShortenRequest(BaseModel):
    """Request schema for shortening a URL with optional custom alias and expiration (TTL)."""
    url: str = Field(
        ...,
        description="Target destination URL to shorten",
        examples=["https://aws.amazon.com/blogs/aws/"],
    )
    custom_code: Optional[str] = Field(
        default=None,
        description="Optional custom vanity code (4-16 alphanumeric characters)",
        examples=["aws-blog"],
    )
    expires_in_hours: Optional[int] = Field(
        default=None,
        ge=1,
        le=8760,
        description="Optional expiration in hours (1 to 8760 hours, e.g., 24 for 1 day)",
        examples=[24],
    )
    expires_in_days: Optional[int] = Field(
        default=None,
        ge=1,
        le=365,
        description="Optional expiration in days (1 to 365 days)",
        examples=[7],
    )

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        clean = v.strip()
        valid, reason = is_valid_url(clean)
        if not valid:
            raise ValueError(reason)
        return clean

    @field_validator("custom_code")
    @classmethod
    def validate_alias(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            clean = v.strip()
            valid, reason = is_valid_custom_code(clean)
            if not valid:
                raise ValueError(reason)
            return clean
        return None

    @model_validator(mode="after")
    def validate_expiration_options(self):
        if self.expires_in_hours is not None and self.expires_in_days is not None:
            raise ValueError("Specify either 'expires_in_hours' or 'expires_in_days', not both.")
        return self


class URLShortenResponse(BaseModel):
    """Response containing the generated short code, full short URL, and expiration."""
    status: str = "success"
    short_code: str
    short_url: str
    original_url: str
    created_at: str
    expires_at: Optional[str] = None
    code_type: str = "random_base62"  # or 'custom_alias'


class URLBatchRequest(BaseModel):
    """Request schema for batch shortening multiple URLs with optional expiration."""
    urls: List[str] = Field(
        ...,
        min_length=1,
        max_length=50,
        description="List of long URLs to shorten simultaneously",
        examples=[[
            "https://aws.amazon.com/ec2/",
            "https://aws.amazon.com/s3/",
            "https://aws.amazon.com/dynamodb/"
        ]]
    )
    expires_in_hours: Optional[int] = Field(
        default=None,
        ge=1,
        le=8760,
        description="Optional expiration in hours for all URLs in the batch",
    )
    expires_in_days: Optional[int] = Field(
        default=None,
        ge=1,
        le=365,
        description="Optional expiration in days for all URLs in the batch",
    )

    @model_validator(mode="after")
    def validate_expiration_options(self):
        if self.expires_in_hours is not None and self.expires_in_days is not None:
            raise ValueError("Specify either 'expires_in_hours' or 'expires_in_days', not both.")
        return self


class URLBatchResponse(BaseModel):
    """Response returned for batch URL shortening."""
    total_requested: int
    successful_count: int
    items: List[URLShortenResponse]


class URLDatabaseRecord(BaseModel):
    """Schema representing a persistent database record from SQLite."""
    id: int
    short_code: str
    original_url: str
    click_count: int
    created_at: datetime
    last_accessed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    is_active: bool
    is_expired: bool = False
    time_remaining_seconds: Optional[int] = None

    model_config = {"from_attributes": True}


class URLStatsResponse(BaseModel):
    """Schema representing URL access tracking and click statistics (Lab 10 & 11)."""
    short_code: str
    original_url: str
    click_count: int
    created_at: datetime
    last_accessed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    is_active: bool
    is_expired: bool = False
    time_remaining_seconds: Optional[int] = None
    status: str = "active"

    model_config = {"from_attributes": True}
