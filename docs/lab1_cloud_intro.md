# Lab 1: Introduction to Cloud Applications

## 1. Overview
In this lab, we lay the conceptual and architectural foundation for building a **Cloud-Based URL Shortener**. URL shorteners (like Bitly or TinyURL) are classic cloud-scale applications: they must handle massive read traffic (redirections) with ultra-low latency, maintain high availability, and persist mapping records reliably.

---

## 2. Core Concepts Explained

### 2.1 What is Cloud Computing?
Cloud computing is the on-demand delivery of IT resources (computing power, storage, databases, networking) over the internet with pay-as-you-go pricing.

#### The Three Primary Cloud Service Models:
| Service Model | Definition | Responsibility (Provider vs You) | Example Services |
| :--- | :--- | :--- | :--- |
| **IaaS (Infrastructure as a Service)** | Raw virtualized hardware: virtual machines, raw storage, networks. | Provider manages physical hardware and virtualization; You manage OS, runtime, and app. | **AWS EC2**, Azure Virtual Machines, GCP Compute Engine |
| **PaaS (Platform as a Service)** | Managed application runtime environment where you simply upload code or containers. | Provider manages OS, patch cycles, scaling, and runtime; You manage code and configurations. | **AWS App Runner**, **AWS Elastic Beanstalk**, Heroku |
| **SaaS (Software as a Service)** | Fully managed end-user software accessible over web browsers or APIs. | Provider manages everything; You only consume the service. | Gmail, Google Drive, Microsoft 365, Dropbox |

#### Key Benefits of Cloud Hosting for URL Shorteners:
1. **Elastic Scalability**: Traffic spikes (e.g., a viral link posted on social media) can automatically trigger new server instances.
2. **High Availability (HA)**: Deployed across multiple Availability Zones (data centers) so if one fails, traffic reroutes seamlessly.
3. **Global Low Latency**: Through Content Delivery Networks (CDNs) and edge caching, link lookups happen in milliseconds globally.
4. **Pay-as-you-go**: Zero upfront server purchase costs.

---

### 2.2 Client, Server, API, and Database

A modern web application consists of 4 foundational tiers:

```text
[ Client (Browser / Postman / User) ]
                 │
                 ▼  HTTP Request (e.g., POST /shorten)
[ Web / API Server (FastAPI / Python) ]
                 │
                 ▼  SQL Query / Read / Write
[ Database Engine (SQLite / PostgreSQL / RDS) ]
```

1. **Client**:
   - The interface that the end user interacts with.
   - Examples: A web browser (Chrome, Edge), a mobile phone app, or API clients like Postman and cURL.
   - Role in URL shortener: Submits a long URL via a form/API call, or requests a short link (`http://sho.rt/xyz`).

2. **Server**:
   - The backend program running on a computer that listens for incoming network requests and executes application logic.
   - Role in URL shortener: Accepts incoming URLs, validates syntax, generates a compact hash/code, manages timestamps/expiration, and calculates analytics.

3. **API (Application Programming Interface)**:
   - The contract and communication protocol through which Client and Server exchange data.
   - Follows **REST (Representational State Transfer)** principles:
     - `POST /api/shorten`: Sends a long URL payload to generate a new short code.
     - `GET /{short_code}`: Requests redirection to the target destination.
     - `GET /api/stats/{short_code}`: Retrieves analytics (click count, creation date, expiry).
   - Responses are typically formatted in standard **JSON (JavaScript Object Notation)**.

4. **Database**:
   - The persistent storage engine that preserves data even if servers restart or crash.
   - For local development: **SQLite** (a lightweight file-based relational database).
   - For cloud production: **Amazon RDS (PostgreSQL/MySQL)** or **Amazon DynamoDB** (high-throughput NoSQL key-value store).

---

## 3. Cloud Application Architecture Flow

### 3.1 Step-by-Step Request Lifecycle
When a user clicks on a shortened URL (`https://link.example.com/abc12`):

```text
1. User clicks short link: https://link.example.com/abc12
                   │
                   ▼
2. DNS Resolution: Amazon Route 53 translates domain to IP address
                   │
                   ▼
3. Edge Routing / Cache: Amazon CloudFront CDN (checks for cached target)
                   │
                   ▼
4. Load Balancing: Application Load Balancer (ALB) distributes traffic
                   │
                   ▼
5. Backend Compute: AWS App Runner / ECS / EC2 container runs FastAPI
                   │
                   ▼
6. Query Database: SQLite locally, or Amazon DynamoDB / RDS in AWS
                   │
                   ▼
7. HTTP 307 / 301 Redirect: Returns "Location: https://original-destination.com"
                   │
                   ▼
8. User's browser automatically navigates to destination page
```

---

## 4. Local Simulation vs. AWS Cloud Mapping

| Architecture Layer | Local Simulation (Labs 2–13) | AWS Production Equivalent (Lab 15) | Purpose |
| :--- | :--- | :--- | :--- |
| **Client** | Web Browser / Postman / cURL | Web Browser / Mobile Apps / Third-party APIs | Initiates requests |
| **DNS / Domain** | `localhost:8000` | **Amazon Route 53** | Domain routing & DNS management |
| **API Gateway / Load Balancer**| Uvicorn internal server | **Amazon API Gateway** or **Application Load Balancer (ALB)** | SSL termination, rate limiting, traffic balancing |
| **Application Runtime (Compute)**| Python 3 virtual environment | **AWS App Runner**, **Amazon ECS (Fargate)**, or **AWS EC2** | Runs the containerized application |
| **Container Engine** | Docker Desktop | **Amazon Elastic Container Registry (ECR)** | Stores container images |
| **Database** | SQLite (`urls.db`) | **Amazon DynamoDB** or **Amazon RDS PostgreSQL** | Scalable, persistent storage |
| **Monitoring & Logs** | Console logs / Terminal output | **Amazon CloudWatch** | Centralized log ingestion and alarms |

---

## 5. Summary & Checklist for Lab 1

- [x] Defined Cloud Computing and identified IaaS, PaaS, and SaaS models.
- [x] Explored the 4 key building blocks: Client, Server, API, and Database.
- [x] Traced the complete lifecycle of a URL shortening and redirection request.
- [x] Understood how the local Python + SQLite architecture will translate to AWS cloud infrastructure.
