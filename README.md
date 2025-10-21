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
│   │   └── 001_initial_migration.py
│   ├── env.py             # Alembic environment
│   └── script.py.mako     # Migration template
├── app/
│   ├── models/            # Database models
│   │   ├── __init__.py
│   │   ├── user.py        # User model
│   │   └── task.py        # Task model
│   ├── api/               # API routes
│   ├── db.py              # Database configuration
│   └── __init__.py
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

## Dependencies

- **FastAPI**: Modern web framework
- **SQLModel**: SQL database library with Pydantic integration
- **Alembic**: Database migration tool
- **PostgreSQL**: Database (via psycopg2-binary)
- **Uvicorn**: ASGI server
- **Passlib**: Password hashing with bcrypt
- **Python-JOSE**: JWT token handling
- **Pytest**: Testing framework
