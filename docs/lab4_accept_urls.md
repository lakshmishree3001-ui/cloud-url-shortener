# Lab 4: Accept Long URLs & Validation

## 1. Overview
In this lab, we build the URL intake gateway for the URL Shortener service:
- Endpoint: `POST /api/shorten`
- Request Schema: JSON body containing the `url` field
- Comprehensive validation: Strict HTTP/HTTPS scheme check, valid hostname resolution pattern, length restriction (RFC 2048 characters), and whitespace sanitization.

---

## 2. Why URL Validation Matters in Cloud Architecture

In enterprise cloud applications (e.g., deployed on **AWS ECS**, **AWS App Runner**, or **EC2**), strict ingress validation is an essential security defense:

1. **SSRF (Server-Side Request Forgery) Defense**:
   - Cloud instances host internal metadata services (e.g., AWS Instance Metadata Service at `http://169.254.169.254/`).
   - If an unvalidated URL was processed or fetched without protocol and domain filtering, attackers could attempt to extract cloud IAM role credentials.
2. **Database Resource Protection**:
   - Every write operation in the cloud incurs I/O and storage costs (e.g., DynamoDB Write Capacity Units or RDS storage IOPS).
   - Validating at the API layer rejects malformed data immediately, protecting the cloud database from garbage data.
3. **Canonical Normalization**:
   - Ensures URLs are stripped of leading/trailing spaces and have uniform formatting before hash generation in Lab 5.

---

## 3. Implemented Endpoint & Validation Rules

### Endpoint Specification
- **Method**: `POST`
- **Path**: `/api/shorten`
- **Request Body (JSON)**:
  ```json
  {
    "url": "https://aws.amazon.com/architecture/well-architected/"
  }
  ```

### Validation Matrix
| Input URL | Validation Result | HTTP Status | Response Details |
| :--- | :--- | :--- | :--- |
| `https://aws.amazon.com/solutions/` | **VALID** | `200 OK` | Accepted, returns domain & scheme |
| `http://sub.domain.org/path?q=1` | **VALID** | `200 OK` | Accepted, preserves query strings |
| `ftp://files.example.com/archive.zip` | **INVALID** | `422 Unprocessable` | Rejected: Scheme must be `http` or `https` |
| `not-a-valid-url` | **INVALID** | `422 Unprocessable` | Rejected: Missing protocol and domain |
| `https://` | **INVALID** | `422 Unprocessable` | Rejected: Missing hostname |
| `""` (Empty string) | **INVALID** | `422 Unprocessable` | Rejected: Cannot be empty |

---

## 4. How to Test (Where to Go & What to Click)

### Option A: Interactive Swagger UI
1. If your server is running, go to: [**http://127.0.0.1:8000/docs**](http://127.0.0.1:8000/docs)  
   *(If not running, start with: `.\venv\Scripts\uvicorn.exe app.main:app --reload`)*
2. Find the green **`POST /api/shorten`** block under the **URL Shortener** section.
3. Click **Try it out**.
4. Test Case 1 (Valid URL):
   ```json
   {
     "url": "https://docs.aws.amazon.com/ecs/"
   }
   ```
   Click **Execute** ➔ Verify `200 OK` with `status: "valid"`.
5. Test Case 2 (Invalid URL):
   ```json
   {
     "url": "ftp://malformed.example.com"
   }
   ```
   Click **Execute** ➔ Verify `422 Unprocessable Entity` with error message.

---

### Option B: PowerShell Command Line
```powershell
# Valid test
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/shorten" -Method Post -ContentType "application/json" -Body '{"url":"https://aws.amazon.com"}'

# Invalid test
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/shorten" -Method Post -ContentType "application/json" -Body '{"url":"ftp://invalid.com"}'
```

---

## 5. Verification Checklist

- [x] URL intake endpoint `POST /api/shorten` established.
- [x] Implemented domain and scheme validation in `app/utils.py`.
- [x] Enforced Pydantic schema validation in `app/models.py`.
- [x] Created and passed 6 automated tests for valid and malformed URLs in `tests/test_api.py`.
