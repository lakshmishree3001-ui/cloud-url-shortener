# Lab 12: Analytics & Statistics Reporting API

## 1. Cloud Architecture & Enterprise Telemetry Context

In hyper-scale URL shorteners (e.g., bit.ly, TinyURL, AWS Link Management), tracking link redirection performance is fundamental. Organizations require real-time visibility into:
- **Campaign Leaderboards**: Identifying the highest-converting links and viral traffic sources.
- **Domain Distribution**: Auditing outbound target domains to detect phishing, spam, or high-traffic destinations.
- **Operational Health**: Continuous health monitoring, active vs. expired ratios, and average click yields.

### Enterprise AWS Cloud Architecture Mapping

```
                                      +------------------------------------+
                                      | Amazon CloudWatch Dashboard        |
                                      | - TotalShortLinksStored            |
                                      | - TotalRedirectionsServed          |
                                      | - ActiveShortLinksGauge            |
                                      +------------------+-----------------+
                                                         ^
                                                         | (Publishes Custom Metrics)
+------------------+              +----------------------+-----------------+
|  Client Browser  |              |        AWS ECS Fargate Container       |
|  or BI Dashboard |              |        (FastAPI Analytics Engine)      |
+--------+---------+              +----------------------+-----------------+
         |                                               |
         | (GET /api/stats/report)                       | (Streams Click Events)
         v                                               v
+------------------+                      +--------------------------------+
| Amazon Route 53  |                      | Amazon Kinesis Firehose        |
| & CloudFront CDN |                      | -> Amazon S3 Click Logs        |
+--------+---------+                      | -> Amazon Athena & QuickSight  |
         |                                +--------------------------------+
         v
+------------------+
|  AWS ALB Ingress |
+------------------+
```

1. **Amazon CloudWatch Metrics & Alarms**:
   - Every redirection access updates custom metrics published to CloudWatch namespace `AWS/URLShortener`.
   - CloudWatch Alarms can trigger Auto Scaling or alert engineers if error rates spike.
2. **Amazon Kinesis Data Firehose & Amazon S3**:
   - For terabyte-scale clickstream ingestion, every redirection event is buffered into Kinesis Firehose and delivered to Amazon S3 in partitioned Parquet format.
3. **Amazon Athena & Amazon QuickSight**:
   - Serverless SQL queries via Amazon Athena power interactive QuickSight business intelligence dashboards for marketing teams.

---

## 2. API Endpoints & Specification

### A. Top-N Most Clicked Links (`GET /api/stats/top`)
Returns an ordered leaderboard of the most popular short URLs.
- **Query Parameter**: `limit` (int, default=10, min=1, max=50).

**Sample Response (HTTP 200 OK):**
```json
{
  "limit": 2,
  "returned_count": 2,
  "top_links": [
    {
      "rank": 1,
      "short_code": "gold-link",
      "short_url": "http://65.0.80.41:8000/gold-link",
      "original_url": "https://aws.amazon.com/ec2/",
      "destination_domain": "aws.amazon.com",
      "click_count": 5,
      "created_at": "2026-10-13T14:50:00.000000Z",
      "last_accessed_at": "2026-10-13T14:55:12.000000Z",
      "expires_at": null,
      "is_active": true,
      "is_expired": false,
      "status": "active"
    },
    {
      "rank": 2,
      "short_code": "silver-link",
      "short_url": "http://65.0.80.41:8000/silver-link",
      "original_url": "https://github.com/torvalds/linux",
      "destination_domain": "github.com",
      "click_count": 3,
      "created_at": "2026-10-13T14:51:00.000000Z",
      "last_accessed_at": "2026-10-13T14:56:00.000000Z",
      "expires_at": null,
      "is_active": true,
      "is_expired": false,
      "status": "active"
    }
  ]
}
```

---

### B. Destination Domain Distribution (`GET /api/stats/domains`)
Aggregates destination domains to analyze traffic distribution and link concentration.

**Sample Response (HTTP 200 OK):**
```json
{
  "total_unique_domains": 2,
  "total_tracked_clicks": 5,
  "domains": [
    {
      "domain": "aws.amazon.com",
      "link_count": 2,
      "total_clicks": 4,
      "percentage_of_all_clicks": 80.0
    },
    {
      "domain": "github.com",
      "link_count": 1,
      "total_clicks": 1,
      "percentage_of_all_clicks": 20.0
    }
  ]
}
```

---

### C. Comprehensive Telemetry & Observability Report (`GET /api/stats/report`)
Consolidates entire system telemetry into a single unified JSON document.

**Sample Response (HTTP 200 OK):**
```json
{
  "report_timestamp": "2026-10-13T15:00:00.000000Z",
  "cloud_region": "ap-south-1 (Mumbai)",
  "summary": {
    "total_links": 12,
    "active_links": 10,
    "expired_links": 2,
    "deactivated_links": 0,
    "total_clicks": 48,
    "average_clicks_per_link": 4.0,
    "health_status": "optimal"
  },
  "top_performing_links": [...],
  "recent_links": [...],
  "recent_accesses": [...],
  "domain_breakdown": [...],
  "cloudwatch_telemetry_metrics": [
    {"metric_name": "TotalShortLinksStored", "namespace": "AWS/URLShortener", "value": 12.0, "unit": "Count", "timestamp": "2026-10-13T15:00:00Z"},
    {"metric_name": "ActiveShortLinksGauge", "namespace": "AWS/URLShortener", "value": 10.0, "unit": "Count", "timestamp": "2026-10-13T15:00:00Z"},
    {"metric_name": "ExpiredShortLinksCount", "namespace": "AWS/URLShortener", "value": 2.0, "unit": "Count", "timestamp": "2026-10-13T15:00:00Z"},
    {"metric_name": "TotalRedirectionsServed", "namespace": "AWS/URLShortener", "value": 48.0, "unit": "Count", "timestamp": "2026-10-13T15:00:00Z"},
    {"metric_name": "AverageClicksPerLink", "namespace": "AWS/URLShortener", "value": 4.0, "unit": "Count/Instance", "timestamp": "2026-10-13T15:00:00Z"}
  ]
}
```

---

## 3. Verification & Automated Test Suite

- Total tests: **31/31 passing (100% green)**
- Includes validation for:
  - Leaderboard sorting and ranking (`rank = 1, 2, ...`)
  - Query parameter boundary validation (`1 <= limit <= 50`)
  - Domain extraction and percentage calculations
  - Complete CloudWatch telemetry metric format verification
