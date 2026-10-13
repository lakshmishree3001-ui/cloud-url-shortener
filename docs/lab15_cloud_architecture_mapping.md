# Lab 15: Cloud Architecture Mapping & AWS Production Deployment

## 1. Executive Summary & Project Completion

This document marks the final milestone of the **Cloud-Based URL Shortener Simulation** project (**Labs 1 through 15**). We have taken a bare-bones URL shortener concept, developed a high-performance, collision-resistant REST API in Python (FastAPI + SQLite), containerized it via Docker, deployed and verified it live on a cloud server (AWS EC2 in Mumbai, `ap-south-1`), and mapped every single component to enterprise-grade AWS Cloud Services.

```
+===================================================================================================+
|                                    AWS PRODUCTION ARCHITECTURE                                    |
+===================================================================================================+
                                            [Internet User]
                                                   |
                                                   v
                                        [Amazon Route 53 DNS]
                                     (Latency & Failover Routing)
                                                   |
                                                   v
                                      [Amazon CloudFront CDN]
                                  + [AWS WAF (Web App Firewall)]
                                   (Edge Caching & DDoS Shield)
                                                   |
                                                   v
                                 [AWS Application Load Balancer]
                                    (HTTPS Termination & Ingress)
                                                   |
                                                   v
                    +-------------------------------------------------------------+
                    |           Amazon ECS Cluster on AWS Fargate (Multi-AZ)       |
                    |   +-----------------------+     +-----------------------+   |
                    |   |  FastAPI Container 1  |     |  FastAPI Container 2  |   |
                    |   |  (uvicorn ASGI engine)|     |  (uvicorn ASGI engine)|   |
                    |   +-----------+-----------+     +-----------+-----------+   |
                    +---------------|-----------------------------|---------------+
                                    |                             |
                                    v                             v
                   +---------------------------------------------------------------+
                   |        Amazon ElastiCache for Redis (In-Memory Hot Cache)     |
                   |               Sub-millisecond Short-Code Lookups (<2ms)       |
                   +-------------------------------+-------------------------------+
                                                   |
                                                   | (Cache Miss / URL Creation)
                                                   v
                   +---------------------------------------------------------------+
                   |           Amazon DynamoDB (Global Table with Native TTL)      |
                   |               or Amazon Aurora Multi-AZ (PostgreSQL/MySQL)    |
                   +-------------------------------+-------------------------------+
                                                   |
                      +----------------------------+----------------------------+
                      |                                                         |
                      v                                                         v
        +----------------------------+                            +----------------------------+
        |  Amazon EventBridge Cron   |                            |  Amazon Kinesis Firehose   |
        |  -> AWS Lambda TTL Sweeper |                            |  -> Amazon S3 Click Logs   |
        |  (Purges Expired Links)    |                            |  -> Amazon Athena/QuickSight
        +----------------------------+                            +----------------------------+
```

---

## 2. Complete Component-by-Component Cloud Mapping

| Local Simulation Component | Project Implementation | AWS Production Equivalent | Production Functionality & Enterprise Benefit |
| :--- | :--- | :--- | :--- |
| **Domain Resolution** | `http://localhost:8000` / EC2 Public IP `65.0.80.41` | **Amazon Route 53** | Highly available DNS routing with latency-based, geolocation, and failover health checks. |
| **Edge CDN & DDoS Security** | FastAPI middleware | **Amazon CloudFront + AWS WAF** | Global edge PoPs caching HTTP 307 redirects; AWS WAF filtering malicious bots, rate limiting, and blocking SSRF attacks. |
| **Ingress & Load Balancing** | Single FastAPI port `8000` | **Application Load Balancer (ALB)** | Layer 7 load balancer distributing traffic across multi-AZ container targets with SSL/TLS offloading (ACM). |
| **Application Runtime** | Python 3.12 + FastAPI + uvicorn | **Amazon ECS on AWS Fargate** | Serverless container orchestration automatically scaling tasks based on CPU/RAM utilization without EC2 management. |
| **Container Engine** | Docker + `docker-compose.yml` | **Amazon Elastic Container Registry (ECR)** | Private, encrypted, vulnerability-scanned (Amazon Inspector) container repository integrated with CI/CD. |
| **Persistent Storage** | SQLite (`urls.db`) + SQLAlchemy | **Amazon DynamoDB** / **Amazon Aurora Serverless** | NoSQL database with single-digit millisecond latency, automated cross-region replication, and automated backups. |
| **Time-To-Live (TTL)** | Custom `expires_at` logic + sweeper | **DynamoDB Native TTL / Redis EXPIRE** | Automatic background item deletion based on UNIX epoch timestamp at zero read/write capacity cost. |
| **High-Speed Caching** | Local in-memory session | **Amazon ElastiCache (Redis)** | Caching hot short codes to serve 95% of redirection requests in under 2 milliseconds. |
| **Access Telemetry** | Click counter + `/api/stats/report` | **Amazon CloudWatch** | Unified operational telemetry: custom metrics (`AWS/URLShortener`), log groups, container insights, and alarm triggers. |
| **Analytics Pipeline** | Summary & Domain APIs (`/api/stats/*`) | **Amazon Kinesis Data Firehose + Amazon S3 + Athena** | Real-time clickstream ingestion into S3 data lakes; serverless SQL querying and QuickSight dashboards. |
| **Automated Tasks** | `/api/maintenance/cleanup-expired` | **Amazon EventBridge + AWS Lambda** | Serverless scheduled cron rules invoking Lambda functions to perform automated database maintenance. |
| **Secrets & Keys** | Local environment variables | **AWS Secrets Manager / Systems Manager Parameter Store** | Encrypted runtime credentials with automated credential rotation and IAM access audits. |

---

## 3. End-to-End Request Lifecycle in Production

### Flow A: URL Shortening Request (`POST /api/shorten`)
1. **User Client** submits long URL to `https://sho.rt/api/shorten`.
2. **Route 53** directs traffic to the nearest **CloudFront** edge location.
3. **AWS WAF** inspects payload: validates scheme, rate-limits per IP (e.g., max 100 requests/minute), and verifies against threat intelligence lists.
4. **ALB** terminates TLS using ACM certificates and forwards request to an **AWS Fargate** container.
5. **FastAPI Engine**:
   - Validates RFC format and prevents SSRF targeting internal AWS metadata IPs (`169.254.169.254`).
   - Generates collision-resistant Base62 code ($62^6 \approx 56.8$ billion namespace).
   - Writes record to **DynamoDB** with conditional write `attribute_not_exists(short_code)` and sets `ttl_timestamp`.
   - Seeds **ElastiCache Redis** cache with key `url:{short_code}` (read-through cache).
6. **Response**: Returns JSON containing `short_url` and `expires_at` (HTTP 201 Created).

### Flow B: URL Redirection Request (`GET /{short_code}`)
1. **User Client** requests `https://sho.rt/abc123`.
2. **CloudFront**: Checks edge cache. If present and TTL valid, returns `HTTP 307` immediately (< 10 ms).
3. **ALB -> Fargate Container**:
   - Queries **ElastiCache Redis**: Hits hot cache in ~1.2 ms.
   - If cache miss: Queries **DynamoDB** by partition key `short_code` (~4 ms) and populates Redis.
   - Validates expiration: If expired, returns `HTTP 410 Gone`.
4. **Clickstream Logging**: Asynchronously pushes click event (timestamp, IP hash, user-agent, referer) to **Amazon Kinesis Firehose** without blocking the user response.
5. **Response**: Returns `HTTP 307 Temporary Redirect` with `Location: <original_url>` header. Total origin round-trip: **< 15 ms**.

---

## 4. The 5 Pillars of the AWS Well-Architected Framework

### 1. Operational Excellence
- **Infrastructure as Code (IaC)**: Deploy entire AWS stack using AWS CDK (TypeScript/Python) or Terraform.
- **CI/CD Automation**: GitHub Actions triggers AWS CodeBuild for testing, pushes container image to Amazon ECR, and triggers AWS CodeDeploy for zero-downtime rolling ECS updates.
- **Observability**: CloudWatch Logs with metric filters tracking 4xx and 5xx anomalies.

### 2. Security
- **Defense in Depth**: Public ALB residing in public subnets; ECS containers running in private subnets with no public IPs; DynamoDB/Aurora accessed via AWS PrivateLink VPC Endpoints.
- **Least Privilege**: ECS Task Execution Role restricted strictly to pulling from ECR, writing to CloudWatch, and reading specific KMS-encrypted Secrets Manager items.
- **Data Protection**: Encryption in transit (TLS 1.3) and encryption at rest using customer-managed AWS KMS keys.

### 3. Reliability
- **Multi-AZ Resilience**: ECS Fargate tasks and DynamoDB tables distributed across 3 distinct Availability Zones (`ap-south-1a`, `ap-south-1b`, `ap-south-1c`).
- **Self-Healing Containers**: If a container fails its ALB `/health` probe, ECS automatically terminates it and spawns a fresh task.
- **Disaster Recovery**: Automated point-in-time recovery (PITR) enabled on DynamoDB/Aurora with cross-region replication to `us-east-1`.

### 4. Performance Efficiency
- **Sub-Millisecond Read Caching**: Redis caching absorbs >90% of all read traffic.
- **Graviton3 Compute**: AWS Fargate tasks running on ARM64 Graviton3 processors offering 25% better price-performance than x86.
- **HTTP/2 & HTTP/3 Support**: CloudFront and ALB terminate modern multiplexed HTTP connections to eliminate TCP head-of-line blocking.

### 5. Cost Optimization
- **Serverless Fargate & DynamoDB On-Demand**: Zero idle server costs; scales dynamically with traffic.
- **Fargate Spot**: Background maintenance workers (TTL sweeper) run on Fargate Spot at a 70% discount.
- **S3 Lifecycle Policies**: Clickstream logs automatically transition from S3 Standard to S3 Standard-IA at 30 days, and S3 Glacier Flexible Retrieval at 90 days.

---

## 5. Production AWS Cost Estimation Model

| AWS Service | Startup / Low Traffic (1M clicks/mo) | High Traffic Enterprise (100M clicks/mo) |
| :--- | :--- | :--- |
| **Amazon Route 53** | $0.50 (1 Hosted Zone) | $40.00 (Hosted zones + DNS queries) |
| **Amazon CloudFront** | $0.85 (10 GB transfer) | $85.00 (1 TB transfer + edge requests) |
| **AWS Application Load Balancer** | $16.00 (1 ALB + LCU hours) | $45.00 (High LCU usage) |
| **Amazon ECS on AWS Fargate** | $14.50 (0.5 vCPU, 1 GB RAM, 1 task) | $180.00 (Autoscaled 4-8 tasks) |
| **Amazon DynamoDB** | $1.25 (On-demand read/writes + storage)| $65.00 (Provisioned with Auto Scaling) |
| **Amazon ElastiCache (Redis)** | $0.00 (Optional / small t4g.micro: $12)| $68.00 (Cache cluster `cache.t4g.small`) |
| **Amazon CloudWatch** | $3.00 (Custom metrics + logs) | $35.00 (Detailed alarms & high logs) |
| **AWS WAF** | $5.00 (1 WebACL + basic rules) | $30.00 (Bot control + rate limiting) |
| **Total Estimated Monthly Cost** | **~$41.10 / month** | **~$548.00 / month** |

---

## 6. Complete Curriculum Milestone Summary (Labs 1–15)

- [x] **Lab 1**: Introduction to Cloud Computing, 4-Tier Architecture & AWS Ecosystem
- [x] **Lab 2**: Python 3.12 Development Setup, `uv` Package Management & Clean Project Structure
- [x] **Lab 3**: Core REST API (`GET /`, `GET /health` ALB Probe, `POST /api/echo`)
- [x] **Lab 4**: URL Intake, Strict RFC Validation & Anti-SSRF Domain Checks
- [x] **Lab 5**: Cryptographic Base62 Short Code Hashing ($62^6 \approx 56.8$ Billion Space)
- [x] **Lab 6**: SQLite Database Engine Design, SQLAlchemy ORM Models & Lifespan Migrations
- [x] **Lab 7**: Store & Retrieve URLs via API (`POST /api/shorten`, `GET /api/urls`)
- [x] **Lab 8**: URL Redirection Implementation (`GET /{short_code}` -> HTTP 307 Temporary Redirect)
- [x] **Lab 9**: Global Exception Handling (RFC 7807, HTTP 400, 404, 409, 410)
- [x] **Lab 10**: Access Tracking & Real-Time Click Counters (`click_count`, `last_accessed_at`)
- [x] **Lab 11**: URL Expiration & Time-To-Live (TTL) Management (DynamoDB TTL Mapping)
- [x] **Lab 12**: Comprehensive Analytics Reporting API (Top URLs, Domain Shares, CloudWatch Metrics)
- [x] **Lab 13**: Docker Containerization (`Dockerfile`, `.dockerignore`, `docker-compose.yml`, non-root user)
- [x] **Lab 14**: Comprehensive 35-Test Automated Suite, Live API Validator & OpenAPI 3.1.0 Export
- [x] **Lab 15**: Cloud Architecture Mapping & AWS Production Deployment Wrap-Up
