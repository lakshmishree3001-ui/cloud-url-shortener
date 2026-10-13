# Lab 2: Development Environment Setup

## 1. Overview
In this lab, we establish a clean, isolated, and standardized Python development environment for the **Cloud-Based URL Shortener** application. Using a virtual environment prevents dependency conflicts and simulates cloud container boundaries where each application runs in its own isolated runtime.

---

## 2. Where to Go & What to Click (VS Code Step-by-Step)

### Step 1: Open the Project Folder in VS Code
1. Launch **Visual Studio Code**.
2. Click **File** in the top menu bar, then click **Open Folder...** (or press `Ctrl + K, Ctrl + O`).
3. Navigate to `C:\cloud-url-shortener` and click **Select Folder**.
4. If prompted with *"Do you trust the authors of the files in this folder?"*, click **Yes, I trust the authors**.

### Step 2: Open the Integrated Terminal
1. In the top menu bar, click **Terminal** ➔ **New Terminal** (or press `Ctrl + ~` / `Ctrl + Shift + \``).
2. The terminal will open at the bottom of your VS Code window pointing to `C:\cloud-url-shortener`.

### Step 3: Select the Python Interpreter
1. Press `Ctrl + Shift + P` to open the VS Code Command Palette.
2. Type: `Python: Select Interpreter` and press `Enter`.
3. Select the Python interpreter located inside your virtual environment:  
   `.\venv\Scripts\python.exe` (labeled *('venv': venv)*).
4. Notice the bottom status bar now confirms Python is using your isolated virtual environment!

---

## 3. Virtual Environment & Dependencies

### Why Use a Virtual Environment (`venv`)?
In cloud computing and professional engineering, you never install application packages globally. A virtual environment:
- Prevents version conflicts between different projects.
- Mirrors a clean Docker container where only required libraries exist.
- Allows deterministic installs using `requirements.txt`.

### Step-by-Step Commands Run Behind the Scenes:
```powershell
# 1. Create the virtual environment
python -m venv venv

# 2. Activate the virtual environment
.\venv\Scripts\Activate.ps1

# 3. Upgrade pip to the latest version
.\venv\Scripts\python.exe -m pip install --upgrade pip

# 4. Install all project dependencies
.\venv\Scripts\pip.exe install -r requirements.txt
```

---

## 4. Key Libraries Installed

| Package | Purpose in URL Shortener |
| :--- | :--- |
| **`fastapi`** | High-performance, modern web framework for building REST APIs with automatic OpenAPI/Swagger documentation. |
| **`uvicorn[standard]`** | Lightning-fast ASGI server to run and serve FastAPI in asynchronous event loops. |
| **`pydantic`** | Data validation and schema enforcement for incoming long URLs and responses. |
| **`sqlalchemy`** | SQL toolkit and Object Relational Mapper (ORM) for interacting with SQLite and cloud relational databases. |
| **`httpx`** | Asynchronous HTTP client used for automated API testing in `pytest`. |
| **`pytest`** | Unit and integration testing framework. |

---

## 5. Initial Project Structure

```text
cloud-url-shortener/
├── app/
│   ├── __init__.py      # Marks app as a Python module
│   ├── main.py          # FastAPI application entrypoint (Lab 3)
│   ├── models.py        # Database models & Pydantic schemas (Labs 4, 6)
│   ├── database.py      # SQLite connection engine (Lab 6)
│   └── utils.py         # Base62 encoding & URL validation (Labs 4, 5)
├── tests/
│   ├── __init__.py      # Marks tests as a Python module
│   └── test_api.py      # Automated test suites (Lab 14)
├── docs/
│   ├── lab1_cloud_intro.md
│   ├── lab2_dev_setup.md
│   └── architecture_diagram.jpg
├── venv/                # Isolated Python virtual environment
├── .gitignore           # Excludes venv, db, and cache from Git
├── requirements.txt     # Locked production & development dependencies
└── README.md            # Master project dashboard
```

---

## 6. Verification Checklist

To verify that your environment is 100% ready:
Run the following in your VS Code terminal:
```powershell
.\venv\Scripts\python.exe -c "import fastapi, uvicorn, sqlalchemy, pydantic; print('All core libraries successfully verified!')"
```

If it prints `All core libraries successfully verified!`, your development environment is fully operational!
