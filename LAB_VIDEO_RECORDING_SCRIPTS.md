# Full 2-Minute Video Recording Guide & Scripts: Labs 1 to 15
## Cloud-Based URL Shortener Application

Every lab below is structured as a **standalone 2-minute video** (120 to 130 seconds) with timestamps starting at `00:00` for each recording. 

Strict professional standards are enforced with **zero emojis** in all visual demonstrations and narration scripts.

---

## Lab 1: Project Architecture & Cloud Service Mapping
- **Target Duration**: 02:05 (125 seconds)
- **Pre-Recording Setup**: Open `README.md` in VS Code and have the project file explorer visible.

### On-Screen Visual Actions (00:00 - 02:05)
| Timestamp | What to Show on Screen |
| :--- | :--- |
| `00:00 - 00:20` | Display `README.md` at the project title *Cloud-Based URL Shortener*. Hover over the executive overview and system goals. |
| `00:20 - 00:45` | Scroll to the **AWS Cloud Architecture Mapping** table. Slowly highlight the five operational tiers: DNS (Route 53), CDN (CloudFront), Compute (ALB & ECS Fargate), Storage (SQLite simulating RDS/DynamoDB), and Observability (CloudWatch). |
| `00:45 - 01:10` | Scroll down to the request lifecycle architecture flow. Trace the path of an incoming HTTP request: client browser -> edge cache -> load balancer -> FastAPI service -> database lookup -> HTTP 307 redirect. |
| `01:10 - 01:35` | Open the VS Code sidebar file explorer. Expand `app/` (`main.py`, `models.py`, `database.py`, `utils.py`, `static/`) and `tests/`. Hover over each component to illustrate clean modular separation. |
| `01:35 - 01:50` | Open `requirements.txt` and `docker-compose.yml` briefly in the editor to demonstrate cloud-ready infrastructure as code. |
| `01:50 - 02:05` | Return to `README.md` curriculum checklist showing all 15 labs completed. Conclude Lab 1 demonstration. |

### Accompanying Narration / Subtitle Script
- `00:00 - 00:20`: Welcome to the demonstration for Lab 1, covering the Cloud-Based URL Shortener architecture and cloud service mapping. In this lab, we establish the foundational architectural blueprint for a production-grade link management platform designed to deliver high availability, low latency, and robust horizontal scalability across enterprise cloud environments.
- `00:20 - 00:45`: Examining our cloud service mapping table in the project documentation, every application component is mapped to an AWS counterpart. Amazon Route 53 directs global traffic, Amazon CloudFront accelerates delivery at edge locations, and an Application Load Balancer distributes incoming requests across containerized microservices hosted on Amazon ECS Fargate tasks.
- `00:45 - 01:10`: For the persistence tier, our localized SQLite engine provides ACID-compliant storage simulating Amazon RDS PostgreSQL and DynamoDB key-value stores. Observability is aligned with Amazon CloudWatch metrics. Incoming requests follow an optimized lifecycle, moving from edge cache to the FastAPI application layer for instant validation and low-overhead redirection.
- `01:10 - 01:35`: Looking at the project file tree in the IDE sidebar, we observe a clean modular organization. Application routing and lifecycle logic reside in main.py, data schemas and validation rules are encapsulated in models.py, database connection pooling is managed in database.py, and Base62 token utilities are isolated in utils.py.
- `01:35 - 01:50`: Declarative deployment assets including requirements.txt and docker-compose.yml ensure deterministic, environment-agnostic packaging ready for container registries and automated cloud deployment pipelines.
- `01:50 - 02:05`: Our project roadmap confirms that all foundational design specifications have been met. This concludes Lab 1, with the core cloud architectural patterns fully planned and ready for implementation.

---

## Lab 2: Development Environment Setup & Project Initialization
- **Target Duration**: 02:05 (125 seconds)
- **Pre-Recording Setup**: Open terminal in `C:\cloud-url-shortener` and have `requirements.txt` open in VS Code.

### On-Screen Visual Actions (00:00 - 02:05)
| Timestamp | What to Show on Screen |
| :--- | :--- |
| `00:00 - 00:20` | In the terminal, run `python --version` showing Python 3.12. Run `Get-Command python` to show the active binary path. |
| `00:20 - 00:45` | Run `.\venv\Scripts\activate` to activate the virtual environment. Prompt prefix changes to `(venv)`. Show directory tree with `dir` or `ls`. |
| `00:45 - 01:10` | Switch to editor showing `requirements.txt`. Highlight each major dependency: `fastapi==0.115.6`, `uvicorn==0.34.0`, `sqlalchemy==2.0.36`, `pydantic==2.10.4`, `pytest==8.3.4`, `httpx==0.28.1`. |
| `01:10 - 01:35` | Return to terminal and run `pip list`. Scroll through installed packages to verify exact version alignment with `requirements.txt`. |
| `01:35 - 01:50` | Run `git status` confirming clean branch `main`. Run `git log --oneline -n 3` demonstrating version-controlled commits. |
| `01:50 - 02:05` | Show `.gitignore` in VS Code, confirming `venv/`, `.pytest_cache/`, `urls.db`, and `__pycache__/` are correctly excluded from git tracking. |

### Accompanying Narration / Subtitle Script
- `00:00 - 00:20`: Demonstration for Lab 2: Development Environment Setup and Project Initialization. We begin by verifying our local runtime environment, confirming Python 3.12 is active and properly registered in our system PATH to ensure compatibility with modern asynchronous libraries.
- `00:20 - 00:45`: Next, we activate our dedicated virtual environment. This isolates all third-party project dependencies from global system libraries, preventing version conflicts and guaranteeing reproducible behavior. The terminal prompt displays the active virtual environment indicator, signaling a clean isolated workspace ready for development.
- `00:45 - 01:10`: In requirements.txt, we review our pinned enterprise technology stack. This includes FastAPI for asynchronous API routing, Uvicorn as our ASGI web server, SQLAlchemy 2.0 for robust object-relational database mapping, Pydantic 2 for high-performance schema validation, and Pytest alongside HTTPX for end-to-end automated testing.
- `01:10 - 01:35`: Executing pip list in the terminal verifies that all declared dependencies and their underlying sub-packages, such as Starlette and AnyIO, are installed in exact version lockstep. No unapproved packages or version discrepancies exist within this verified development runtime.
- `01:35 - 01:50`: We review our Git repository configuration. Checking git status confirms a clean working directory on branch main, with descriptive conventional commit messages documenting progressive development milestones.
- `01:50 - 02:05`: Our gitignore file ensures cache artifacts, virtual environment directories, and physical database files remain excluded from version control. Lab 2 environment setup is verified and complete.

---

## Lab 3: Core API Endpoints & Health Check Infrastructure
- **Target Duration**: 02:05 (125 seconds)
- **Pre-Recording Setup**: Uvicorn server running on port 8000. Open browser tabs for `/health`, `/docs`, and VS Code with `app/main.py`.

### On-Screen Visual Actions (00:00 - 02:05)
| Timestamp | What to Show on Screen |
| :--- | :--- |
| `00:00 - 00:25` | Open `app/main.py` in VS Code. Highlight FastAPI app initialization with title, version 2.0.0, and metadata. Highlight `@app.get("/")`, `@app.get("/health")`, and `@app.post("/api/echo")`. |
| `00:25 - 00:50` | Open terminal and show Uvicorn server running: `uvicorn app.main:app --host 127.0.0.1 --port 8000`. Point out clean startup logs with zero errors. |
| `00:50 - 01:15` | Switch to browser at `http://localhost:8000/health`. Show JSON response: `{"status": "healthy", "timestamp": "...", "database": "sqlite_connected", "persisted_records_count": ...}`. |
| `01:15 - 01:40` | Switch to Swagger UI at `http://localhost:8000/docs`. Expand `POST /api/echo`. Click "Try it out". Enter request body `{"message": "Cloud-Native URL Shortener Verification", "client_name": "QA-Runner"}`. Click Execute. |
| `01:40 - 01:55` | Review the HTTP 200 response: verified status success, echoed message, client identifier, UTC timestamp, and simulated cloud region `us-east-1`. |
| `01:55 - 02:05` | Switch to `http://localhost:8000/` in browser or curl to show root service metadata payload confirming curriculum progress. |

### Accompanying Narration / Subtitle Script
- `00:00 - 00:25`: Demonstration for Lab 3: Core API Endpoints and Health Check Infrastructure. In app main.py, we instantiate the primary FastAPI application instance configured with custom OpenAPI title, versioning metadata, and asynchronous lifespan event handlers to supervise application startup and shutdown.
- `00:25 - 00:50`: Switching to the terminal, we observe the Uvicorn ASGI server actively running on localhost port 8000. The startup logs confirm clean socket binding, database connection initialization, and active asynchronous workers ready to ingest concurrent HTTP traffic without blocking the event loop.
- `00:50 - 01:15`: Navigating to slash health in our web browser invokes our diagnostic probe endpoint. The response returns an HTTP 200 OK status alongside a JSON payload reporting service health, active database connectivity, and record counts. In production, this probe binds to AWS Application Load Balancer target group health checks.
- `01:15 - 01:40`: In the interactive Swagger UI documentation, we execute a test request against the POST api echo endpoint. We supply a JSON payload specifying a diagnostic message and client identifier. FastAPI automatically deserializes the request body, executes schema validation, and processes the handler logic.
- `01:40 - 01:55`: The server response confirms successful transmission, returning the echoed message, validated client identity, an ISO-8601 UTC timestamp, and simulated us-east-1 cloud deployment region metadata.
- `01:55 - 02:05`: Querying the root endpoint returns foundational system metadata and architecture tier mapping. Lab 3 foundational endpoints are operating flawlessly.

---

## Lab 4: URL Intake & Syntactic Validation
- **Target Duration**: 02:05 (125 seconds)
- **Pre-Recording Setup**: Open `app/utils.py` and `app/models.py` in VS Code, and Swagger UI at `/docs`.

### On-Screen Visual Actions (00:00 - 02:05)
| Timestamp | What to Show on Screen |
| :--- | :--- |
| `00:00 - 00:25` | In `app/utils.py`, highlight the `is_valid_url()` function. Walk through the regular expression verifying protocol scheme (`http://` or `https://`), valid hostname syntax, domain TLD, and optional query parameters. |
| `00:25 - 00:50` | In `app/models.py`, review `URLIntakeRequest` and `URLShortenRequest`. Show Pydantic field validators with min/max length constraints and regex checks preventing XSS or invalid URI injections. |
| `00:50 - 01:15` | In Swagger UI, expand `POST /api/shorten`. Test Case 1: Enter valid URL `https://aws.amazon.com/architecture/best-practices/`. Click Execute. Show HTTP 201 Created response. |
| `01:15 - 01:40` | Test Case 2 (Syntax Violation): Enter `not-a-valid-url-format`. Click Execute. Show HTTP 400 Bad Request response with detailed error message explaining that the URL lacks a valid protocol scheme and domain. |
| `01:40 - 01:55` | Test Case 3 (Unsupported Protocol): Enter `ftp://files.example.com/data.tar`. Click Execute. Show rejection enforcing that only HTTP and HTTPS web destinations are permissible. |
| `01:55 - 02:05` | Test Case 4 (Empty Body): Submit empty JSON `{}` to demonstrate Pydantic automatic request body validation. |

### Accompanying Narration / Subtitle Script
- `00:00 - 00:25`: Demonstration for Lab 4: URL Intake and Syntactic Validation. To protect data integrity and avoid storing malformed or dangerous inputs, all incoming URLs must pass strict syntactic inspection before entering the application database.
- `00:25 - 00:50`: In app utils.py, we inspect our URL validation engine. The is_valid_url function executes a comprehensive regular expression checking for approved protocol schemes, valid domain syntax, and allowed URI query characters, while Pydantic schemas enforce length constraints and prevent script injections.
- `00:50 - 01:15`: In Swagger UI, we test our intake endpoint using a valid enterprise AWS architecture documentation URL. The system validates the protocol, confirms standard domain formatting, processes the request body, and returns an HTTP 201 Created response containing the shortened link details.
- `01:15 - 01:40`: Next, we submit a malformed input lacking a protocol and valid top-level domain. The validation filter intercepts the invalid string, rejecting the request with an HTTP 400 Bad Request error and returning a clear descriptive error message explaining why the input failed validation.
- `01:40 - 01:55`: We further test an unsupported FTP protocol address. The validator rejects the input immediately, confirming that only web-standard HTTP and HTTPS schemes are permitted into the system.
- `01:55 - 02:05`: Submitting an empty JSON payload triggers automated Pydantic schema rejection. Lab 4 intake validation logic is thoroughly verified.

---

## Lab 5: Base62 Short Code Generation Engine
- **Target Duration**: 02:05 (125 seconds)
- **Pre-Recording Setup**: Open `app/utils.py` in VS Code and terminal in `C:\cloud-url-shortener`.

### On-Screen Visual Actions (00:00 - 02:05)
| Timestamp | What to Show on Screen |
| :--- | :--- |
| `00:00 - 00:25` | In `app/utils.py`, highlight the definition of `BASE62_SET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"`. Explain why 62 characters are chosen (alphanumeric, URL-safe, no special escape characters needed). |
| `00:25 - 00:50` | Highlight `generate_short_code(length=6)`. Walk through the random selection algorithm and mathematical permutation space: 62 to the power of 6 equals over 56.8 billion possible unique codes. |
| `00:50 - 01:15` | Highlight `is_valid_custom_code()`. Walk through vanity alias constraints: minimum length 4 characters, maximum length 30 characters, allowed regex `^[a-zA-Z0-9_-]+$`. |
| `01:15 - 01:40` | Switch to terminal. Run interactive python command: `.\venv\Scripts\python -c "from app.utils import generate_short_code; print([generate_short_code() for _ in range(8)])"`. Point out 8 unique 6-character alphanumeric tokens generated. |
| `01:40 - 01:55` | In terminal, test custom code validation: test `valid-alias_2026` returning True, and test `invalid alias with spaces` or `alias@bad!` returning False. |
| `01:55 - 02:05` | Review collision avoidance design: database uniqueness constraints reject colliding tokens and trigger automatic regeneration. |

### Accompanying Narration / Subtitle Script
- `00:00 - 00:25`: Demonstration for Lab 5: Base62 Short Code Generation Engine. Short codes act as the compact primary lookup key for all stored URLs, requiring high entropy, URL safety, and an immense addressable namespace to eliminate collision risks.
- `00:25 - 00:50`: In app utils.py, we review the Base62 alphabet comprising numeric digits 0 through 9, lowercase letters a through z, and uppercase letters A through Z. Using a default token length of six characters yields 62 to the sixth power, providing over 56.8 billion unique permutations without requiring special characters.
- `00:50 - 01:15`: We also inspect custom vanity alias validation. To support branded marketing campaigns, custom codes are allowed between 4 and 30 characters, constrained strictly to alphanumeric characters, hyphens, and underscores to prevent URI encoding corruption.
- `01:15 - 01:40`: In the terminal, we execute an interactive Python script generating a batch of random short codes. Each invocation produces a unique, high-entropy 6-character token generated from a cryptographically sound randomness source suitable for direct database indexing.
- `01:40 - 01:55`: Testing custom vanity strings confirms that compliant names pass inspection, whereas strings containing spaces, illegal punctuation, or excessive length are promptly rejected by the validator.
- `01:55 - 02:05`: Coupled with database-level uniqueness constraints, this architecture guarantees collision-free short link generation. Lab 5 is complete.

---

## Lab 6: SQLite Database Engine & Lifespan Migrations
- **Target Duration**: 02:05 (125 seconds)
- **Pre-Recording Setup**: Open `app/database.py`, `app/models.py`, and `app/main.py` in VS Code.

### On-Screen Visual Actions (00:00 - 02:05)
| Timestamp | What to Show on Screen |
| :--- | :--- |
| `00:00 - 00:25` | In `app/database.py`, walk through `create_engine("sqlite:///./urls.db")`, `connect_args={"check_same_thread": False}`, `sessionmaker`, and `Base = declarative_base()`. |
| `00:25 - 00:50` | Highlight the dependency generator `get_db()`. Explain how FastAPI dependency injection yields a session per request and guarantees `db.close()` in a `finally` block to prevent connection leaks. |
| `00:50 - 01:15` | In `app/models.py`, inspect the `URLItem` table definition. Point out all 8 columns: `id` (primary key integer), `short_code` (indexed string), `original_url`, `click_count`, `created_at`, `expires_at`, `is_active`, and `last_accessed_at`. |
| `01:15 - 01:40` | In `app/main.py`, inspect the `lifespan(app)` context manager. Show `Base.metadata.create_all(bind=engine)` and the automated PRAGMA column migration logic that safely adds newly introduced columns on startup. |
| `01:40 - 01:55` | In terminal, run a brief SQLite inspection: `.\venv\Scripts\python -c "import sqlite3; conn = sqlite3.connect('urls.db'); print([c[1] for c in conn.execute('PRAGMA table_info(urls)').fetchall()])"`. Show all column names in the physical database file. |
| `01:55 - 02:05` | Explain how this local SQLite implementation directly translates to Amazon RDS PostgreSQL and Amazon DynamoDB in cloud deployments. |

### Accompanying Narration / Subtitle Script
- `00:00 - 00:25`: Demonstration for Lab 6: SQLite Database Engine and Persistent Lifespan Migrations. For durable local persistence simulating cloud data stores, we configure SQLAlchemy ORM with a persistent SQLite engine.
- `00:25 - 00:50`: In app database.py, we review the get_db dependency generator. Each incoming HTTP request receives an isolated database session that guarantees automatic commit on success, rollback on error, and session closure in a finally block to eliminate connection leakage under heavy traffic.
- `00:50 - 01:15`: In app models.py, the URLItem model defines the complete relational table schema. It includes an auto-incrementing primary key, a unique indexed short code, the destination URL, atomic click counters, UTC creation and access timestamps, and TTL expiration fields.
- `01:15 - 01:40`: In app main.py, our lifespan manager executes automatically during FastAPI startup. It inspects table structures and safely applies non-destructive PRAGMA column additions, allowing smooth database schema evolution without requiring external migration tooling.
- `01:40 - 01:55`: In the terminal, we run a direct SQLite PRAGMA table query. The output displays all active columns, confirming that the physical database on disk matches our ORM entity definition exactly.
- `01:55 - 02:05`: This persistence architecture mirrors enterprise cloud databases like Amazon RDS and DynamoDB. Lab 6 persistence infrastructure is verified.

---

## Lab 7: Persistent SQLite URL Storage & Retrieval API
- **Target Duration**: 02:05 (125 seconds)
- **Pre-Recording Setup**: Open Swagger UI at `/docs` and `app/main.py` in VS Code.

### On-Screen Visual Actions (00:00 - 02:05)
| Timestamp | What to Show on Screen |
| :--- | :--- |
| `00:00 - 00:25` | In `app/main.py`, review the implementation of `POST /api/shorten`, `GET /api/urls`, and `GET /api/urls/{short_code}`. Point out database query filtering and session management. |
| `00:25 - 00:50` | In Swagger UI, expand `POST /api/shorten`. Submit payload `{"url": "https://aws.amazon.com/s3/"}`. Click Execute. Show HTTP 201 Created response displaying `short_code`, full `short_url`, `created_at`, and `code_type: random_base62`. Copy the short code. |
| `00:50 - 01:15` | Test Idempotency: Click Execute again with the exact same URL. Show that rather than creating a redundant duplicate record, the service detects the existing active entry and returns the existing short link. |
| `01:15 - 01:40` | Expand `GET /api/urls`. Click Execute. Review the returned list of database records. Highlight pagination parameters `skip=0`, `limit=100`, total count, and individual record attributes. |
| `01:40 - 01:55` | Expand `GET /api/urls/{short_code}`. Paste the copied short code from step 1. Click Execute. Show HTTP 200 response returning the exact record metadata from SQLite. |
| `01:55 - 02:05` | Test 404 lookup: Query a non-existent code `fake-code-000` to show proper 404 response when a record is not found. |

### Accompanying Narration / Subtitle Script
- `00:00 - 00:25`: Demonstration for Lab 7: Persistent SQLite URL Storage and Retrieval API. In this lab, we connect our FastAPI intake endpoints to the persistent database, implementing full CRUD lifecycle operations for short link records.
- `00:25 - 00:50`: Using Swagger UI, we execute POST api shorten with a valid destination URL. The endpoint commits the new record to SQLite and returns an HTTP 201 Created response displaying the generated short code, absolute short URL, creation timestamp, and Base62 token type.
- `00:50 - 01:15`: Next, we test system idempotency by submitting the exact same destination URL again. The service detects the existing active entry in SQLite, avoids allocating redundant duplicate rows, and returns the existing short link metadata, optimizing database capacity.
- `01:15 - 01:40`: We now test the GET api urls listing endpoint. The response returns an array of cataloged URLs supporting pagination parameters skip and limit, complete with domain extraction, click counts, and lifecycle statuses.
- `01:40 - 01:55`: Querying GET api urls with our specific short code confirms instantaneous primary key lookup, retrieving complete metadata directly from disk.
- `01:55 - 02:05`: Testing a non-existent short code returns a properly structured HTTP 404 response. Lab 7 persistent URL storage and retrieval are verified.

---

## Lab 8: URL Redirection Engine (HTTP 307)
- **Target Duration**: 02:05 (125 seconds)
- **Pre-Recording Setup**: Open web browser, terminal, and `app/main.py` in VS Code.

### On-Screen Visual Actions (00:00 - 02:05)
| Timestamp | What to Show on Screen |
| :--- | :--- |
| `00:00 - 00:25` | In `app/main.py`, examine `@app.get("/{short_code}")`. Explain the lookup query on `URLItem.short_code`, active status check, and `RedirectResponse(url=record.original_url, status_code=307)`. |
| `00:25 - 00:50` | Explain the technical distinction: HTTP 307 Temporary Redirect is chosen over HTTP 301 Permanent Redirect so that client browsers do not permanently cache the target URL, ensuring every subsequent click routes through our server for real-time access logging. |
| `00:50 - 01:15` | In terminal, run `curl.exe -I http://localhost:8000/{short_code}` using an existing valid short code. Highlight `HTTP/1.1 307 Temporary Redirect` and the `Location: https://aws.amazon.com/s3/` header. |
| `01:15 - 01:40` | In browser address bar, paste `http://localhost:8000/{short_code}` and press Enter. Record the instantaneous redirect transition loading the original destination website. |
| `01:40 - 01:55` | Test non-existent code: In browser, navigate to `http://localhost:8000/does-not-exist`. Show clean HTTP 404 response. |
| `01:55 - 02:05` | Review reserved route protection: show that system paths such as `/docs`, `/health`, and `/dashboard` are exempted from short code matching. |

### Accompanying Narration / Subtitle Script
- `00:00 - 00:25`: Demonstration for Lab 8: URL Redirection Engine. The redirection route constitutes the primary high-throughput gateway of our URL shortener platform, transforming compact short codes into direct browser navigation.
- `00:25 - 00:50`: In app main.py, the redirection handler queries SQLite for the active short code. When found, it issues an HTTP 307 Temporary Redirect. We intentionally choose 307 over 301 Permanent Redirect so that client browsers do not cache the destination, forcing every click to hit our server for telemetry logging.
- `00:50 - 01:15`: In the terminal, we run curl with the -I flag against an active short link. The output confirms the HTTP/1.1 307 Temporary Redirect status and highlights the Location header pointing directly to the target destination URL.
- `01:15 - 01:40`: Entering the short URL into our browser address bar demonstrates seamless, instantaneous redirection, instantly resolving the short code and loading the remote destination webpage without any noticeable delay.
- `01:40 - 01:55`: Navigating to an invalid or unknown short code demonstrates proper error trapping, returning a clean HTTP 404 Not Found error page.
- `01:55 - 02:05`: Reserved system paths such as docs, health, and static dashboard assets are protected against short code collisions. Lab 8 redirection is fully verified.

---

## Lab 9: Global Exception Handling & Error Management
- **Target Duration**: 02:05 (125 seconds)
- **Pre-Recording Setup**: Open `app/main.py` showing exception handlers, and Swagger UI at `/docs`.

### On-Screen Visual Actions (00:00 - 02:05)
| Timestamp | What to Show on Screen |
| :--- | :--- |
| `00:00 - 00:25` | In `app/main.py`, highlight `@app.exception_handler(HTTPException)` and `@app.exception_handler(RequestValidationError)`. |
| `00:25 - 00:50` | Review the unified JSON error schema: `error: true`, `status_code`, `detail`, `path`, and ISO-8601 UTC `timestamp`. Explain the security advantage of preventing internal stack trace disclosure. |
| `00:50 - 01:15` | Error Case 1 (404 Not Found): In browser, query `http://localhost:8000/unknown-alias-999`. Show structured JSON response indicating short code not found. |
| `01:15 - 01:40` | Error Case 2 (409 Conflict): In Swagger UI, call `POST /api/shorten` with custom vanity alias `aws-arch`. Submit it twice. On second submission, show HTTP 409 Conflict response detailing that the alias is already in use. |
| `01:40 - 01:55` | Error Case 3 (400 Bad Request): Submit a request with negative expiration hours `expires_in_hours: -5`. Show HTTP 400 validation error response from Pydantic. |
| `01:55 - 02:05` | Review edge case: show that database connection failures and uncaught runtime errors are safely caught, ensuring high availability. |

### Accompanying Narration / Subtitle Script
- `00:00 - 00:25`: Demonstration for Lab 9: Global Exception Handling and Error Management. In production cloud applications, predictable error handling is essential for maintaining service reliability and preventing internal implementation leaks.
- `00:25 - 00:50`: In app main.py, we examine our global exception handlers intercepting HTTPExceptions and RequestValidationErrors. These handlers transform all system errors into a uniform JSON response structure containing an error boolean, status code, detailed message, request path, and UTC timestamp.
- `00:50 - 01:15`: Testing a non-existent short link in our browser triggers our 404 handler. Rather than a raw web server crash or default HTML page, the client receives an elegant, machine-readable JSON error payload.
- `01:15 - 01:40`: In Swagger UI, we test custom alias conflict handling by submitting an already-claimed custom short code. The application catches the uniqueness collision and returns an HTTP 409 Conflict status with clear guidance to select an alternate alias.
- `01:40 - 01:55`: Submitting invalid parameters, such as a negative expiration duration, immediately produces an HTTP 400 validation error describing the specific constraint violation.
- `01:55 - 02:05`: This standardized error architecture safeguards backend internals while providing consistent contracts for API consumers. Lab 9 is verified.

---

## Lab 10: Access Tracking & Real-Time Click Analytics
- **Target Duration**: 02:05 (125 seconds)
- **Pre-Recording Setup**: Open terminal and Swagger UI at `http://localhost:8000/docs`.

### On-Screen Visual Actions (00:00 - 02:05)
| Timestamp | What to Show on Screen |
| :--- | :--- |
| `00:00 - 00:25` | In `app/main.py`, highlight the access tracking logic within `redirect_to_original_url`: `record.click_count += 1` and `record.last_accessed_at = datetime.now(timezone.utc)`. Point out atomic commit. |
| `00:25 - 00:50` | In Swagger UI, expand `GET /api/urls/{short_code}/stats`. Submit a newly created short link. Point out baseline metrics: `click_count: 0` and `last_accessed_at: null`. |
| `00:50 - 01:15` | Generate live traffic: Open a new browser tab or run curl commands to hit the redirect URL `http://localhost:8000/{short_code}` three consecutive times. |
| `01:15 - 01:40` | Return to Swagger UI and re-execute `GET /api/urls/{short_code}/stats`. Highlight the updated response: `click_count` has atomically incremented from 0 to 3, and `last_accessed_at` records the exact UTC timestamp of the most recent redirection. |
| `01:40 - 01:55` | Expand `GET /api/stats/summary`. Click Execute. Review platform-wide totals: total links stored, total clicks across all links, and average clicks per link. |
| `01:55 - 02:05` | Review destination domain extraction in stats: show `destination_domain` correctly parsed from original URL. |

### Accompanying Narration / Subtitle Script
- `00:00 - 00:25`: Demonstration for Lab 10: Access Tracking and Real-Time Click Analytics. Measuring user engagement through real-time telemetry is a key operational capability of cloud link management platforms.
- `00:25 - 00:50`: In app main.py, our redirect handler increments the click_count integer atomically and stamps the current UTC datetime into last_accessed_at before returning the redirect response. In Swagger UI, we query link stats for a newly created URL, observing zero clicks and a null access timestamp.
- `00:50 - 01:15`: We now generate simulated user engagement by accessing the short link three consecutive times across separate browser requests. Each visit triggers the redirect handler, executing the atomic database update in real time.
- `01:15 - 01:40`: Re-querying the link statistics endpoint confirms that the click count has incremented to exactly three. The last accessed field accurately reflects the precise UTC timestamp of our most recent visit.
- `01:40 - 01:55`: Calling the global stats summary endpoint aggregates metrics across all database records, displaying total links stored, aggregate platform clicks, and average engagement per link.
- `01:55 - 02:05`: Destination hostnames are automatically parsed and cataloged for domain-level reporting. Lab 10 access tracking is completely verified.

---

## Lab 11: URL Expiration & Time-To-Live (TTL) Management
- **Target Duration**: 02:05 (125 seconds)
- **Pre-Recording Setup**: Open `app/models.py`, `app/main.py`, and Swagger UI at `/docs`.

### On-Screen Visual Actions (00:00 - 02:05)
| Timestamp | What to Show on Screen |
| :--- | :--- |
| `00:00 - 00:25` | In `app/models.py` and `app/main.py`, walk through TTL configuration: `expires_in_hours`, `expires_in_days`, helper `is_url_expired()`, and `get_time_remaining_seconds()`. |
| `00:25 - 00:50` | In Swagger UI, call `POST /api/shorten` with payload `{"url": "https://aws.amazon.com/dynamodb/", "expires_in_hours": 48}`. Show response displaying calculated `expires_at` ISO-8601 timestamp exactly 48 hours in the future. |
| `00:50 - 01:15` | Test validation constraint: Attempt to submit both `expires_in_hours: 24` and `expires_in_days: 7` in the same request. Show Pydantic validator rejecting the ambiguous request with HTTP 400 Bad Request. |
| `01:15 - 01:40` | Demonstrate Expired Access (HTTP 410 Gone): Attempt to access an expired link. Show HTTP 410 Gone response explaining that the URL expired and is no longer accessible. |
| `01:40 - 01:55` | In Swagger UI, execute `POST /api/maintenance/cleanup-expired`. Show maintenance worker output reporting total scanned records, count of deactivated expired links, and remaining active links. |
| `01:55 - 02:05` | Explain how this maintenance endpoint simulates an automated AWS EventBridge rule triggering a periodic Lambda or cron sweeper task. |

### Accompanying Narration / Subtitle Script
- `00:00 - 00:25`: Demonstration for Lab 11: URL Expiration and Time-To-Live Management. Link lifecycle policies ensure that temporary links expire automatically, freeing system resources and enforcing data governance policies.
- `00:25 - 00:50`: In Swagger UI, we shorten a URL providing an optional expiration window of 48 hours. The backend calculates the future UTC expiration timestamp and stores it alongside the record, setting the active status flag.
- `00:50 - 01:15`: We test conflicting TTL parameters by supplying both hourly and daily expiration values in the same request. Our Pydantic model validator detects the ambiguity and rejects the payload with an HTTP 400 Bad Request error.
- `01:15 - 01:40`: When an expired short link is accessed, our redirection engine checks the expiration threshold against the current time. If expired, it deactivates the record and returns an HTTP 410 Gone status code, explicitly communicating that the link has elapsed.
- `01:40 - 01:55`: We execute the maintenance cleanup endpoint, which scans the database, deactivates all elapsed links in bulk, and reports the count of updated records alongside remaining active URLs.
- `01:55 - 02:05`: In cloud production, this maintenance endpoint is triggered on a recurring schedule by AWS EventBridge. Lab 11 TTL management is verified.

---

## Lab 12: Comprehensive Analytics, Top URLs, & CloudWatch Telemetry
- **Target Duration**: 02:05 (125 seconds)
- **Pre-Recording Setup**: Open browser tabs for `/api/stats/top`, `/api/stats/domains`, `/api/stats/cloudwatch`, and `/api/stats/report`.

### On-Screen Visual Actions (00:00 - 02:05)
| Timestamp | What to Show on Screen |
| :--- | :--- |
| `00:00 - 00:25` | In `app/models.py`, review `RankedURLItem`, `TopURLsResponse`, `DomainStatsItem`, and `CloudWatchMetricItem`. Show how schemas enforce structured analytics contracts. |
| `00:25 - 00:50` | Switch to browser at `http://localhost:8000/api/stats/top?limit=10`. Review the Top 10 Leaderboard: links sorted descending by click volume, displaying rank badges (1, 2, 3), destination domain, click totals, and creation dates. |
| `00:50 - 01:15` | Switch to browser at `http://localhost:8000/api/stats/domains`. Review destination domain breakdown: unique hostnames cataloged, link count per domain, total clicks, and percentage of overall platform traffic. |
| `01:15 - 01:40` | Switch to browser at `http://localhost:8000/api/stats/cloudwatch`. Review simulated Amazon CloudWatch metric datapoints: `TotalShortLinksStored`, `TotalClicksLogged`, `ActiveRoutesRatio`. Explain metric namespace `AWS/URLShortener`. |
| `01:40 - 01:55` | Switch to browser at `http://localhost:8000/api/stats/report`. Review comprehensive enterprise observability report combining platform summaries, top links, domain analytics, and recent activity feeds. |
| `01:55 - 02:05` | Explain how these analytics endpoints integrate with Grafana dashboards and CloudWatch alarms for real-time operations monitoring. |

### Accompanying Narration / Subtitle Script
- `00:00 - 00:25`: Demonstration for Lab 12: Comprehensive Analytics, Top URLs, and CloudWatch Telemetry. Enterprise observability transforms raw link traffic into high-value operational and business intelligence.
- `00:25 - 00:50`: In our web browser, we query the top URLs leaderboard endpoint. The API returns the highest-performing links sorted descending by click volume, complete with rank indicators, destination domain names, and total engagement figures.
- `00:50 - 01:15`: Navigating to the domain breakdown endpoint displays traffic aggregated by external target hostnames. This provides clear visibility into external traffic distribution and domain popularity across the platform.
- `01:15 - 01:40`: Next, we view our simulated Amazon CloudWatch telemetry endpoint. It exports structured metric objects matching standard AWS CloudWatch formatting, including namespaces, metric names, units, and values ready for automated CloudWatch alarms.
- `01:40 - 01:55`: The comprehensive analytics report endpoint bundles platform totals, top performers, domain statistics, and recent activity into an executive telemetry stream.
- `01:55 - 02:05`: These standardized metric feeds integrate seamlessly with cloud monitoring dashboards like Grafana and AWS CloudWatch. Lab 12 telemetry is verified.

---

## Lab 13: Docker Containerization & Multi-Stage Deployment
- **Target Duration**: 02:05 (125 seconds)
- **Pre-Recording Setup**: Open `Dockerfile`, `docker-compose.yml`, and a terminal in VS Code.

### On-Screen Visual Actions (00:00 - 02:05)
| Timestamp | What to Show on Screen |
| :--- | :--- |
| `00:00 - 00:25` | Open `Dockerfile` in VS Code. Highlight `FROM python:3.12-slim`. Explain minimal attack surface and reduced container image size. Walk through non-root user creation `appuser`, `WORKDIR /app`, requirements installation with `--no-cache-dir`, and port exposure `EXPOSE 8000`. |
| `00:25 - 00:50` | Highlight the Dockerfile `HEALTHCHECK` directive: curling `http://localhost:8000/health` every 30 seconds with 5-second timeout and 3 retries, ensuring orchestration engines detect hung containers. |
| `00:50 - 01:15` | Open `docker-compose.yml`. Highlight service declaration `web`, port forwarding `8000:8000`, environment variables, restart policy `unless-stopped`, and persistent named volume `sqlite_data:/app/data` to preserve database state. |
| `01:15 - 01:40` | In terminal, demonstrate container status with `docker compose ps` or show container build process with `docker compose build`. Point out clean layers and build efficiency. |
| `01:40 - 01:55` | In terminal or browser, execute `curl http://localhost:8000/health` hitting the containerized application. Confirm HTTP 200 OK and database connectivity. |
| `01:55 - 02:05` | Explain how this container configuration deploys to AWS ECS Fargate or Amazon EKS without any code modification. |

### Accompanying Narration / Subtitle Script
- `00:00 - 00:25`: Demonstration for Lab 13: Docker Containerization and Multi-Stage Deployment. Packaging our application as an immutable Docker container guarantees identical runtime behavior across development, staging, and cloud production.
- `00:25 - 00:50`: In VS Code, we review our Dockerfile based on the lightweight Python 3.12 slim image. It implements container security best practices by creating a non-root application user, installing dependencies without cache overhead, exposing port 8000, and configuring an automated healthcheck probe.
- `00:50 - 01:15`: We inspect docker-compose.yml, which orchestrates local container execution. It maps container port 8000 to the host network and configures a persistent named volume for the SQLite database, ensuring persistent data survives container restarts.
- `01:15 - 01:40`: In the terminal, we inspect the running container with docker compose ps. The output confirms that the container built cleanly, launched within seconds, and is continuously reporting a healthy status via our internal healthcheck.
- `01:40 - 01:55`: Sending an HTTP request to the containerized service confirms that our endpoints, database operations, and static assets function flawlessly inside the container.
- `01:55 - 02:05`: This standardized Docker image is ready for seamless push to Amazon Elastic Container Registry and deployment onto AWS ECS Fargate. Lab 13 is verified.

---

## Lab 14: Comprehensive Automated Testing & API Documentation
- **Target Duration**: 02:05 (125 seconds)
- **Pre-Recording Setup**: Terminal open in `C:\cloud-url-shortener`. Open browser tabs for `/docs` and `/redoc`.

### On-Screen Visual Actions (00:00 - 02:05)
| Timestamp | What to Show on Screen |
| :--- | :--- |
| `00:00 - 00:25` | In `tests/test_api.py`, walk through test architecture: isolated in-memory SQLite database engine (`sqlite:///:memory:`), `StaticPool` sharing connection across threads, and FastAPI `dependency_overrides[get_db]`. |
| `00:25 - 00:55` | In terminal, execute `.\venv\Scripts\pytest -v`. Show test discovery and execution. Highlight all **39 automated unit and integration tests** executing and passing with 100% green checkmarks in approximately 2 seconds. |
| `00:55 - 01:20` | Walk through test coverage categories: core root/health, URL intake validation, Base62 uniqueness, redirection logic, access tracking increments, TTL expiration hours/days, 410 Gone deactivation, maintenance sweeper, CloudWatch metrics, and frontend static asset delivery. |
| `01:20 - 01:45` | Switch to browser at `http://localhost:8000/docs`. Scroll through Swagger UI showing all endpoint groups (Core, Monitoring, URL Shortener, URL Redirection, Analytics, Maintenance). Expand schema models. |
| `01:45 - 01:55` | Switch to browser at `http://localhost:8000/redoc`. Show formatted OpenAPI reference documentation, three-column layout, and payload examples. |
| `01:55 - 02:05` | Highlight `/openapi.json` endpoint providing machine-readable OpenAPI 3.1 specification for automated client SDK generation. |

### Accompanying Narration / Subtitle Script
- `00:00 - 00:25`: Demonstration for Lab 14: Comprehensive Automated Testing and Interactive API Documentation. Production code quality is maintained through an exhaustive automated test suite and standards-compliant documentation.
- `00:25 - 00:55`: In tests/test_api.py, we configure an in-memory SQLite database utilizing StaticPool connection management to guarantee isolated test execution without touching production data. In the terminal, we run pytest. All 39 unit and integration tests execute and pass with 100 percent green success in under two seconds.
- `00:55 - 01:20`: The test suite comprehensively covers all functional domains: health probes, URL validation, Base62 token generation, 307 redirection, atomic click tracking, TTL expiration, HTTP 410 enforcement, maintenance sweepers, and CloudWatch metrics.
- `01:20 - 01:45`: In our browser, we navigate to slash docs to explore the interactive Swagger UI. The documentation is auto-generated from our FastAPI route decorators and Pydantic schemas, supporting interactive in-browser testing.
- `01:45 - 01:55`: We also view slash redoc, which provides a clean, responsive reference manual formatted specifically for developer onboarding and client SDK integration.
- `01:55 - 02:05`: The openapi.json endpoint provides the complete OpenAPI 3.1 specification for automated client generation. Lab 14 testing and documentation standards are verified.

---

## Lab 15: Production Cloud Architecture & Live Enterprise Dashboard
- **Target Duration**: 02:10 (130 seconds)
- **Pre-Recording Setup**: Open browser to `http://localhost:8000/dashboard` (or public EC2 URL `http://65.0.80.41:8000/dashboard`).

### On-Screen Visual Actions (00:00 - 02:10)
| Timestamp | What to Show on Screen |
| :--- | :--- |
| `00:00 - 00:20` | Display the live web application (**CloudLink**). Highlight the Obsidian Slate and Electric Indigo dark aesthetic. Show top key metrics cards: Total Links, Total Clicks, Active Links, Expired Links. Point out the animated pulse status indicator and zero-emoji SVG iconography. |
| `00:20 - 00:45` | In "Shorten URL" tab: enter destination URL `https://aws.amazon.com/architecture/`, enter vanity alias `aws-cloud`, select 24h expiration, and click "Generate Short Link". Show result box appear with active badge, copy button, and visit link. Click Copy button and point out toast alert. |
| `00:45 - 01:10` | In "Batch Shorten" tab: enter 3 distinct URLs in multi-line textarea. Select 7 days expiration. Click "Process Batch Request". Show batch results table rendering generated short links with individual copy controls. |
| `01:10 - 01:30` | In "Link Explorer" tab: review live SQLite table showing all links. Type in search box to filter records in real time. Click test redirect icon to open the link in a new tab, verifying redirection. |
| `01:30 - 01:50` | In "Analytics & Leaderboard" tab: review Top 10 Most Visited Links leaderboard with gold/silver/bronze ranking badges. Review Destination Domain Breakdown distribution bars. |
| `01:50 - 02:00` | In "Cloud Observability" tab: view raw CloudWatch telemetry stream. Click "Trigger Expired Link Cleanup" button and show toast alert reporting deactivated links. |
| `02:00 - 02:10` | Conclude by showing the public AWS EC2 deployment at `http://65.0.80.41:8000/dashboard` and reviewing the final project summary. |

### Accompanying Narration / Subtitle Script
- `00:00 - 00:20`: Demonstration for Lab 15: Production Cloud Architecture and Live Enterprise Dashboard. In this final capstone, we demonstrate CloudLink, the fully realized enterprise web application integrating all 15 labs into an executive production interface.
- `00:20 - 00:45`: The interface features a sophisticated Obsidian Slate and Electric Indigo dark aesthetic with crisp typography, real-time status pulses, and vector SVG iconography. In the Shorten URL tab, we generate a short link with a custom vanity alias and a 24-hour expiration window, receiving instant feedback and clipboard copy controls.
- `00:45 - 01:10`: In the Batch Shorten tab, we submit multiple long URLs simultaneously. The backend processes the batch concurrently, returning a clean tabular breakdown with individual copy controls and expiration indicators for every generated link.
- `01:10 - 01:30`: Switching to the Link Explorer tab provides an interactive query interface into the persistent database. Operators can filter URLs in real time, inspect click counters, verify expiration statuses, and test direct redirection in a new tab.
- `01:30 - 01:50`: The Analytics and Leaderboard tab displays our top 10 most visited links with distinctive ranking badges, accompanied by interactive destination domain distribution bars illustrating platform traffic share.
- `01:50 - 02:00`: In the Cloud Observability tab, operators can monitor raw CloudWatch telemetry and trigger automated database maintenance sweepers with a single click.
- `02:00 - 02:10`: Deployed both locally and on public AWS EC2 infrastructure, this concludes the demonstration, marking 100 percent completion of the Cloud URL Shortener project.
