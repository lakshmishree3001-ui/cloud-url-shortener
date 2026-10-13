# Lab 13: Docker Containerization

## 1. Overview & Cloud Containerization Architecture

Containerization packages an application, its dependencies, runtime, and configuration into a standardized, lightweight executable container. In enterprise cloud deployments, containers ensure:
- **Portability**: Guarantees identical execution across developer laptops, CI/CD runners, and production AWS cloud environments.
- **Resource Efficiency**: Multiple isolated containers share the Linux host kernel without the heavyweight overhead of full virtual machines.
- **Microservices Orchestration**: Seamless scaling, rolling deployments, and automated self-healing via container orchestrators.

### Enterprise AWS Cloud Architecture Mapping

```
                                  +---------------------------------------+
                                  | Amazon Elastic Container Registry     |
                                  | (Amazon ECR) - Secure Docker Images   |
                                  +-------------------+-------------------+
                                                      |
                                                      | (Pulls Image)
                                                      v
+------------------+              +-------------------+-------------------+
| Internet User /  |              | Amazon ECS on AWS Fargate             |
| Client API       |              | (Serverless Container Orchestration)  |
+--------+---------+              +-------------------+-------------------+
         |                                            |
         | (HTTPS Port 443)                           | (Container Port 8000)
         v                                            v
+------------------+              +---------------------------------------+
|  AWS Application | -----------> | Running Docker Container              |
|  Load Balancer   |              | - Non-root user (UID 1000)            |
|     (ALB)        |              | - FastAPI ASGI Engine (uvicorn)       |
+------------------+              | - Docker HEALTHCHECK Probe            |
                                  +-------------------+-------------------+
                                                      |
                                                      | (Persistent Storage)
                                                      v
                                  +---------------------------------------+
                                  | Amazon EFS / Docker Volume            |
                                  | Persistent Volume: /app/data/urls.db  |
                                  +---------------------------------------+
```

1. **Amazon Elastic Container Registry (ECR)**:
   - High-performance, fully managed container registry that hosts, scans (Amazon Inspector), and encrypts Docker images.
2. **Amazon Elastic Container Service (ECS) & AWS Fargate**:
   - Serverless container engine that launches containers on-demand without provisioning or managing EC2 instances. Fargate handles OS patching, scaling, and hardware lifecycle automatically.
3. **AWS Application Load Balancer (ALB)**:
   - Routes incoming public traffic to ECS target groups and continuously executes health check probes against `GET /health`.
4. **Persistent Volumes (Amazon EFS / Docker Volumes)**:
   - Stateful containers mount network-attached storage (Amazon EFS or persistent volume `url-shortener-data:/app/data`) so data persists across container restarts and redeployments.

---

## 2. Container Configuration Details

### A. Dockerfile Highlights
- **Base Image**: `python:3.12-slim` for minimal image size and reduced attack surface.
- **Security**: Creates an unprivileged non-root user `appuser` (UID 1000) to adhere to the AWS Well-Architected Security Pillar.
- **Layer Caching**: Copies `requirements.txt` independently prior to application code.
- **Healthcheck**: Built-in `HEALTHCHECK` probe running `curl -f http://localhost:8000/health || exit 1` every 30 seconds.
- **12-Factor Configuration**: `DATABASE_URL` defaults to `/app/data/urls.db` and can be overridden dynamically at container launch.

### B. `.dockerignore` Highlights
Prevents local artifacts from polluting the container image:
- Virtual environments (`venv/`, `.venv/`)
- Python bytecode (`__pycache__/`, `*.pyc`)
- Test caches (`.pytest_cache/`, `.coverage`)
- Local development databases (`urls.db`)
- Git history (`.git/`)

### C. Docker Compose Orchestration (`docker-compose.yml`)
Enables one-command stack management:
```yaml
version: "3.8"
services:
  url-shortener:
    build: .
    image: cloud-url-shortener:latest
    container_name: url-shortener-app
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:////app/data/urls.db
    volumes:
      - url-shortener-data:/app/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
volumes:
  url-shortener-data:
    name: url-shortener-data
```

---

## 3. How to Build & Run on AWS EC2

### Option 1: Automated Setup Script (Recommended)
```bash
./setup_docker.sh
```

### Option 2: Manual Step-by-Step Commands
1. Install Docker:
   ```bash
   sudo apt-get update && sudo apt-get install -y docker.io docker-compose
   sudo systemctl start docker
   sudo usermod -aG docker $USER
   ```
2. Build Image:
   ```bash
   sudo docker build -t cloud-url-shortener:latest .
   ```
3. Run Container:
   ```bash
   sudo docker run -d \
     -p 8000:8000 \
     -v url-shortener-data:/app/data \
     --name url-shortener-app \
     --restart unless-stopped \
     cloud-url-shortener:latest
   ```
4. Verify Health & Logs:
   ```bash
   sudo docker ps
   sudo docker logs -f url-shortener-app
   ```
