# Writers

A task management application with FastAPI backend and PostgreSQL database.

## Backend Structure

### Database Models

The application uses SQLModel (combination of SQLAlchemy and Pydantic) for database models.

#### User Model
- **id**: UUID (Primary Key)
- **email**: String (Unique, Indexed)
- **username**: String (Unique, Indexed)
- **hashed_password**: String
- **full_name**: String (Optional)
- **is_active**: Boolean
- **is_superuser**: Boolean
- **created_at**: DateTime (Auto-generated)
- **updated_at**: DateTime (Auto-generated)

#### Task Model
- **id**: UUID (Primary Key)
- **title**: String
- **description**: String (Optional)
- **status**: Enum (PENDING, IN_PROGRESS, COMPLETED, CANCELLED)
- **user_id**: UUID (Foreign Key to users)
- **file_path**: String (Optional) - مسیر فایل آپلود شده
- **due_date**: DateTime (Optional)
- **created_at**: DateTime (Auto-generated)
- **updated_at**: DateTime (Auto-generated)

### Database Configuration

Database connection and session management is configured in `backend/app/db.py`:
- PostgreSQL connection string
- SQLAlchemy engine with connection pooling
- Session dependency for FastAPI

### Database Migrations

The project uses Alembic for database migrations.

#### Initialize Database

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head
```

#### Create New Migration

```bash
cd backend

# Auto-generate migration from model changes
alembic revision --autogenerate -m "description of changes"

# Or create empty migration
alembic revision -m "description of changes"

# Apply migrations
alembic upgrade head
```

#### Rollback Migration

```bash
# Rollback one version
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# Rollback all
alembic downgrade base
```

### Configuration

Update database connection string in:
- `backend/alembic.ini` - for migrations
- `backend/app/db.py` - for application runtime

Default connection string:
```
postgresql://user:password@localhost:5432/writers_db
```

## Project Structure

```
backend/
├── alembic/                 # Database migrations
│   ├── versions/           # Migration scripts
│   │   ├── 001_initial_migration.py
│   │   └── 002_add_file_path_to_tasks.py
│   ├── env.py             # Alembic environment
│   └── script.py.mako     # Migration template
├── app/
│   ├── models/            # Database models
│   │   ├── __init__.py
│   │   ├── user.py        # User model
│   │   └── task.py        # Task model
│   ├── routers/           # API routes
│   │   ├── __init__.py
│   │   ├── tasks.py       # Task endpoints
│   │   └── schemas.py     # Task request/response schemas
│   ├── auth/              # Authentication module
│   ├── celery_app.py      # Celery configuration
│   ├── tasks.py           # Background tasks
│   ├── db.py              # Database configuration
│   └── main.py            # Application entry point
├── alembic.ini            # Alembic configuration
└── requirements.txt       # Python dependencies
```

## Authentication

The application implements JWT-based authentication with httpOnly cookies for secure token storage.

### Authentication Features

- User registration with email and username validation
- Secure password hashing using bcrypt (via passlib)
- JWT tokens with `python-jose`
  - Short-term access tokens (30 minutes)
  - Long-term refresh tokens (7 days)
- HttpOnly cookies for secure token storage
- Protected route authentication via dependency injection

### Auth Endpoints

#### Register
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "securepassword123",
  "full_name": "Full Name" (optional)
}
```

Returns user data and sets httpOnly cookies with access and refresh tokens.

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

Returns user data and sets httpOnly cookies with access and refresh tokens.

#### Logout
```http
POST /auth/logout
```

Clears authentication cookies.

### Using Authentication

To protect routes, use the `get_current_user` or `get_current_active_user` dependency:

```python
from fastapi import Depends
from app.auth.dependencies import get_current_user
from app.models.user import User

@app.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"user": current_user.email}
```

### Authentication Module Structure

```
backend/app/auth/
├── __init__.py           # Module exports
├── router.py            # Auth routes (register, login, logout)
├── jwt.py               # JWT token creation and validation
├── dependencies.py      # Authentication dependencies
├── schemas.py           # Pydantic models for requests/responses
└── utils.py             # Password hashing utilities
```

### Running Tests

```bash
cd backend

# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run auth tests only
pytest tests/auth/

# Run with coverage
pytest --cov=app tests/
```

## Task Management API

The application provides endpoints for managing tasks with file upload capabilities.

### Task Endpoints

#### Create Task with File Upload
```http
POST /api/v1/tasks
Content-Type: multipart/form-data
Authentication: Required (Cookie: access_token)

Form Data:
- title: string (required)
- description: string (optional)
- due_date: datetime (optional)
- file: file (optional)
```

Returns `202 Accepted` and creates a background job to process the uploaded file. The file is stored in `STORAGE_ROOT/uploads/` directory.

#### Get All Tasks
```http
GET /api/v1/tasks?skip=0&limit=100&status_filter=PENDING
Authentication: Required (Cookie: access_token)

Query Parameters:
- skip: int (default: 0) - Number of records to skip
- limit: int (default: 100) - Maximum number of records
- status_filter: TaskStatus (optional) - Filter by status
```

Returns list of tasks for the authenticated user.

#### Get Task by ID
```http
GET /api/v1/tasks/{task_id}
Authentication: Required (Cookie: access_token)
```

Returns a specific task by UUID. Returns `403 Forbidden` if the task doesn't belong to the authenticated user.

### Background Processing with Celery

When a file is uploaded with a task, the system:
1. Saves the file to `STORAGE_ROOT/uploads/`
2. Creates a task record in the database with status `PENDING`
3. Queues a Celery background job with task ID and file path
4. Updates the task status to `IN_PROGRESS`
5. Returns `202 Accepted` to the client

The background worker processes the file and updates the task status to `COMPLETED` or `CANCELLED` on error.

#### Starting Celery Worker

```bash
cd backend

# Set environment variables
export REDIS_URL=redis://localhost:6379
export STORAGE_ROOT=/var/app/storage

# Start Celery worker
celery -A app.celery_app worker --loglevel=info
```

### Configuration

Required environment variables:
- `STORAGE_ROOT`: Root directory for file storage (default: `/var/app/storage`)
- `REDIS_URL`: Redis connection URL (default: `redis://localhost:6379`)
- `REDIS_QUEUE_DB`: Redis database for Celery queue (default: `2`)

## Dependencies

- **FastAPI**: Modern web framework
- **SQLModel**: SQL database library with Pydantic integration
- **Alembic**: Database migration tool
- **PostgreSQL**: Database (via psycopg2-binary)
- **Uvicorn**: ASGI server
- **Passlib**: Password hashing with bcrypt
- **Python-JOSE**: JWT token handling
- **Celery**: Distributed task queue for background jobs
- **Redis**: Message broker and result backend for Celery
- **Python-Multipart**: File upload support
- **Pytest**: Testing framework
