# Lab 11: URL Expiration & Time-To-Live (TTL) Management

## 1. Overview & Cloud Architecture Context

In enterprise URL shortener systems (e.g., bit.ly, TinyURL, AWS-native URL shorteners), links frequently require a **Time-To-Live (TTL)**. For example:
- **Temporary Marketing Campaigns**: Links valid only during a 48-hour promotional sale.
- **Security & Authentication**: One-time password (OTP) verification links or password reset tokens valid for 15 minutes.
- **Storage Optimization**: Preventing unbounded database growth by automatically expiring and purging stale links.

### Enterprise AWS Cloud Architecture Mapping

```
                                  +-----------------------------+
                                  | Amazon EventBridge (Cron)   |
                                  | e.g., rate(1 hour)          |
                                  +--------------+--------------+
                                                 | (triggers)
                                                 v
+------------------+              +--------------+--------------+
| Client / Browser |              |      AWS Lambda Worker      |
+--------+---------+              |     (Automated TTL Reaper)  |
         |                        +--------------+--------------+
         | (GET /{short_code})                   |
         v                                       | (Deactivates expired)
+------------------+                             |
|  AWS ALB / ECS   | <---------------------------+
| (FastAPI Engine) |
+--------+---------+
         |
         | (Queries item & checks TTL)
         v
+------------------+--------------------------------------------+
| Amazon DynamoDB  | Native TTL enabled on `expires_at`         |
| or Amazon RDS    | Periodic sweep: `UPDATE urls SET is_active |
|                  | = FALSE WHERE expires_at < NOW()`          |
+------------------+--------------------------------------------+
```

1. **Amazon DynamoDB Native TTL**:
   - DynamoDB offers native TTL support at zero extra charge.
   - Developers designate an attribute (e.g., `ttl_timestamp` in seconds since epoch).
   - DynamoDB's internal background reaper scans and deletes expired records within 48 hours without consuming Read/Write Capacity Units (RCUs/WCUs).
2. **Amazon ElastiCache (Redis) TTL**:
   - For high-throughput caching tiers, Redis handles sub-millisecond TTL eviction via the `EXPIRE` command. Expired keys are evicted automatically via passive lookups and active memory sampling.
3. **Amazon EventBridge + AWS Lambda Sweeper**:
   - For relational databases (Amazon RDS / Aurora PostgreSQL / SQLite simulation), an EventBridge scheduled rule invokes a serverless Lambda function hourly to deactivate expired records in bulk (`POST /api/maintenance/cleanup-expired`).

---

## 2. API Endpoints & Specification

### A. Shorten URL with TTL (`POST /api/shorten`)
Submit an optional `expires_in_hours` (1 to 8760) or `expires_in_days` (1 to 365).

```json
{
  "url": "https://aws.amazon.com/cloudtrail/",
  "custom_code": "trail-promo",
  "expires_in_hours": 24
}
```

**Response (HTTP 201 Created):**
```json
{
  "status": "success",
  "short_code": "trail-promo",
  "short_url": "http://65.0.80.41:8000/trail-promo",
  "original_url": "https://aws.amazon.com/cloudtrail/",
  "created_at": "2026-10-13T13:45:00.000000Z",
  "expires_at": "2026-10-14T13:45:00.000000Z",
  "code_type": "custom_alias"
}
```

### B. Accessing an Expired Link (`GET /{short_code}`)
When a user attempts to access an expired link, the application immediately updates `is_active = False` in SQLite and returns standard **HTTP 410 Gone**:

```json
{
  "error": true,
  "status_code": 410,
  "detail": "This short URL has expired on 2026-10-14T13:45:00.000000Z and is no longer accessible.",
  "path": "/trail-promo",
  "timestamp": "2026-10-14T14:00:00.000000Z"
}
```

### C. Access Tracking & TTL Statistics (`GET /api/urls/{short_code}/stats`)
Returns real-time expiration metadata and remaining lifespan:

```json
{
  "short_code": "trail-promo",
  "original_url": "https://aws.amazon.com/cloudtrail/",
  "click_count": 5,
  "created_at": "2026-10-13T13:45:00.000000Z",
  "last_accessed_at": "2026-10-13T14:10:22.000000Z",
  "expires_at": "2026-10-14T13:45:00.000000Z",
  "is_active": true,
  "is_expired": false,
  "time_remaining_seconds": 84878,
  "status": "active"
}
```

### D. Automated TTL Maintenance Sweeper (`POST /api/maintenance/cleanup-expired`)
Simulates the AWS EventBridge -> Lambda scheduled worker:

```json
{
  "status": "success",
  "deactivated_count": 2,
  "deactivated_codes": ["old-sale-1", "temp-pass-2"],
  "timestamp": "2026-10-13T14:00:00.000000Z",
  "cloud_architecture_simulation": "Amazon EventBridge -> AWS Lambda TTL Reaper"
}
```

---

## 3. Verification & Automated Test Suite

- Total tests: **26/26 passing (100% green)**
- Includes validation for:
  - Expiration in hours / days calculation
  - Mutually exclusive parameters (`expires_in_hours` vs `expires_in_days`)
  - Redirection deactivation upon reaching expiration (HTTP 410)
  - Scheduled maintenance cleanup endpoint
  - Batch shortening with TTL support
