# Lab 3: Create a Basic Web API

## 1. Overview
In this lab, we develop and run a cloud-ready RESTful web API using **FastAPI** and **Uvicorn**. We implement standard HTTP methods:
- **`GET`**: Safe, idempotent read operations (Root service discovery, Application health check).
- **`POST`**: State-changing or payload-carrying operations (Echo test, data submission).

We also explore how cloud infrastructure (specifically **AWS Application Load Balancer** and **Amazon API Gateway**) interacts with these endpoints.

---

## 2. API Endpoints Developed

| Method | Endpoint | Description | HTTP Status Code | Cloud / AWS Equivalent Role |
| :--- | :--- | :--- | :--- | :--- |
| **GET** | `/` | Root service metadata & discovery | `200 OK` | Public domain root landing page |
| **GET** | `/health` | Cloud container liveness/readiness probe | `200 OK` | **AWS ALB Target Group Health Check** |
| **POST** | `/api/echo` | Accepts JSON body and returns enriched response | `200 OK` / `422 Unprocessable` | **API Gateway POST Route** with schema validation |

---

## 3. How to Run the API Server

In your VS Code terminal (or PowerShell window in `C:\cloud-url-shortener`):
Run:
```powershell
.\venv\Scripts\uvicorn.exe app.main:app --reload --host 127.0.0.1 --port 8000
```

### What do the parameters mean?
- `app.main:app`: Look in folder `app`, file `main.py`, for the FastAPI instance named `app`.
- `--reload`: Hot-reloading enabled; auto-restarts the server whenever code is saved.
- `--port 8000`: Listens on TCP port 8000.

The terminal will display:
```text
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [...]
INFO:     Application startup complete.
```

---

## 4. How to Test Your API (3 Different Ways)

### Method A: Interactive Swagger UI (Recommended — No Postman Installation Needed!)
FastAPI automatically generates an interactive API console:
1. Open your web browser (Chrome, Edge).
2. Navigate to: [**http://127.0.0.1:8000/docs**](http://127.0.0.1:8000/docs)
3. You will see all endpoints cleanly organized:
   - Click on **`POST /api/echo`** to expand it.
   - Click the **Try it out** button (top right of the route).
   - In the **Request body** JSON editor, change the message to:
     ```json
     {
       "message": "Testing my Cloud API!",
       "client_name": "My Browser Swagger UI"
     }
     ```
   - Click the big blue **Execute** button.
   - Scroll down to **Server response**; you will see:
     ```json
     {
       "status": "success",
       "received_message": "Testing my Cloud API!",
       "client_name": "My Browser Swagger UI",
       "timestamp": "2026-10-12T...",
       "cloud_region_simulation": "us-east-1"
     }
     ```

---

### Method B: Testing via Web Browser
Directly open the GET endpoints in any web browser tab:
- **Root**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

### Method C: Testing via Postman or PowerShell cURL

#### Testing GET `/health`:
In Postman:
- Method: `GET`
- URL: `http://127.0.0.1:8000/health`
- Click **Send**. Status will be `200 OK`.

In PowerShell:
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method Get
```

#### Testing POST `/api/echo`:
In Postman:
- Method: `POST`
- URL: `http://127.0.0.1:8000/api/echo`
- Click **Headers** tab: Add `Content-Type: application/json`
- Click **Body** tab ➔ Select **raw** ➔ choose **JSON**:
  ```json
  {
    "message": "Hello from Postman!",
    "client_name": "Postman Desktop"
  }
  ```
- Click **Send**. Status will be `200 OK`.

In PowerShell:
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/echo" -Method Post -ContentType "application/json" -Body '{"message":"Hello from PowerShell","client_name":"PS-CLI"}'
```

---

## 5. Cloud Architecture Mapping (AWS Connection)

### Why is the `/health` endpoint critical in AWS?
In AWS, when you deploy containers to **Amazon ECS (Elastic Container Service)** or **AWS App Runner** behind an **Application Load Balancer (ALB)**:
1. The ALB automatically sends an HTTP `GET /health` request to each container every 30 seconds.
2. If the container replies with `200 OK`, AWS marks the instance as **HEALTHY** and forwards user traffic to it.
3. If the container crashes or returns `500 Internal Error`, AWS automatically terminates the unhealthy container and spawns a fresh new container!

---

## 6. Verification Checklist

- [x] Implemented `GET /` and `GET /health`.
- [x] Implemented `POST /api/echo` with Pydantic payload validation.
- [x] Verified interactive documentation at `/docs` (Swagger UI) and `/redoc` (ReDoc).
- [x] Automated unit test suite executed (`pytest tests/test_api.py`) with 100% pass rate.
