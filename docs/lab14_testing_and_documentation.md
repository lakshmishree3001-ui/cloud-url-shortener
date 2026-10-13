# Lab 14: Comprehensive Testing, Validation & Documentation

## 1. Overview & Cloud Testing Architecture

In enterprise cloud software development, rigorous testing and up-to-date documentation are paramount. Prior to promoting microservices into production (e.g., via AWS CodePipeline, GitHub Actions, or AWS CodeBuild), systems must pass multi-layered validation:
1. **Unit Testing**: Verifying deterministic functions, algorithms, and models in isolation (e.g., Base62 encoding, URL validation regexes, SQLAlchemy models).
2. **Integration Testing**: Testing API endpoint interactions against an in-memory database simulation without network boundaries.
3. **End-to-End (E2E) Live Validation**: Executing real HTTP requests against the live running container service on AWS EC2 or AWS ECS to measure response latency, header fidelity, and database persistence.
4. **API Documentation & Schema Integrity**: Exposing OpenAPI / Swagger interactive documentation (`/docs`, `/redoc`) and exporting standard machine-readable `openapi.json` for client SDK generation.

### Enterprise AWS CI/CD & Testing Pipeline

```
+--------------------+
|  GitHub Repository | (git push origin main)
+---------+----------+
          |
          v
+--------------------+
|   AWS CodeBuild /  | 1. Install dependencies (uv / pip)
|   GitHub Actions   | 2. Run unit & integration tests (`pytest -v`)
+---------+----------+ 3. Export & validate OpenAPI schema (`export_openapi.py`)
          |
          | (On 100% Green Tests)
          v
+--------------------+
| AWS CodeDeploy /   | Build Docker container -> Push to Amazon ECR -> Launch on EC2/ECS
| Live EC2 Server    |
+---------+----------+
          |
          | (Post-Deployment Smoke Test)
          v
+--------------------+
| validate_api_live  | Executes 22 live automated probes against http://<HOST>:8000
| (E2E Test Runner)  | Measures P95 latency, validates HTTP 200/201/307/400/404/409/410
+--------------------+
```

---

## 2. Test Suite Breakdown

### Total Automated Tests: **35 Tests (100% Pass Rate)**

| Category | Test File | Scope Covered | Test Count |
| :--- | :--- | :--- | :---: |
| **Core & Health** | `tests/test_api.py` | `GET /`, `GET /health`, `POST /api/echo` | 3 |
| **Persistence & Storage** | `tests/test_api.py` | `POST /api/shorten`, `POST /api/shorten/batch`, `GET /api/urls`, `GET /api/urls/{code}` | 5 |
| **Redirection Engine** | `tests/test_api.py` | `GET /{short_code}` (HTTP 307 Temporary Redirect) | 2 |
| **Error Handling (RFC)** | `tests/test_api.py` | HTTP 400 (Bad URL), 404 (Missing), 409 (Conflict), 410 (Deactivated/Expired) | 5 |
| **Access Tracking** | `tests/test_api.py` | Real-time click counters, access timestamps, global summary | 2 |
| **URL Expiration (TTL)** | `tests/test_api.py` | TTL calculations in hours/days, HTTP 410 Gone on expired, maintenance sweeper | 6 |
| **Analytics & Leaderboards** | `tests/test_api.py` | Top-N ranking, domain distribution, CloudWatch telemetry report | 5 |
| **Edge Cases & OpenAPI** | `tests/test_api.py` | Pagination (`skip`/`limit`), system path guards, OpenAPI schema | 4 |
| **SQLAlchemy ORM Model** | `tests/test_database.py` | Table constraints, uniqueness, click increments | 3 |
| **Total** | | | **35** |

---

## 3. Live End-to-End Validation Script (`scripts/validate_api_live.py`)

A standalone automated test runner is included in `scripts/validate_api_live.py`. It executes 22 live HTTP probes against any target server (localhost or your live AWS EC2 server) and generates a formatted execution summary:

### How to Run:
```bash
# Against your live AWS server
python scripts/validate_api_live.py --base-url http://65.0.80.41:8000

# Or locally inside EC2
python scripts/validate_api_live.py --base-url http://localhost:8000
```

### Probes Executed:
1. `GET /` - Service identity & cloud tier
2. `GET /health` - Application Load Balancer probe
3. `POST /api/echo` - Message round-trip latency
4. `POST /api/shorten` - Cryptographic Base62 code generation
5. `POST /api/shorten` - Custom vanity alias creation
6. `POST /api/shorten` - Expiration TTL timestamp calculation
7. `POST /api/shorten` - Idempotent reuse of duplicate URLs
8. `POST /api/shorten/batch` - Atomic transaction batch insertion
9. `GET /api/urls` - Paginated record query
10. `GET /api/urls/{code}` - Specific record retrieval
11. `GET /{code}` - HTTP 307 Temporary Redirect validation
12. `GET /api/urls/{code}/stats` - Real-time access counter verification
13. `GET /api/stats/top?limit=5` - Leaderboard rank ordering
14. `GET /api/stats/domains` - Destination domain aggregation
15. `GET /api/stats/report` - Amazon CloudWatch metric telemetry extraction
16. `POST /api/maintenance/cleanup-expired` - Scheduled TTL sweeper execution
17. `GET /api/urls/status/expired` - Audit query for expired links
18. `POST /api/shorten` (Invalid URL) -> Validates HTTP 400 Bad Request
19. `POST /api/shorten` (Empty Payload) -> Validates HTTP 400 Bad Request
20. `POST /api/shorten` (Duplicate Alias) -> Validates HTTP 409 Conflict
21. `GET /missing-code` -> Validates HTTP 404 Not Found
22. `POST /api/shorten` (Conflicting TTL) -> Validates HTTP 400 Bad Request

---

## 4. OpenAPI Specification Export (`docs/openapi.json`)

The OpenAPI 3.1.0 specification has been exported to `docs/openapi.json` using `scripts/export_openapi.py`. It documents all 15 routes, request schemas, parameters, and response structures.
