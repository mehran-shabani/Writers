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

## Dependencies

- **FastAPI**: Modern web framework
- **SQLModel**: SQL database library with Pydantic integration
- **Alembic**: Database migration tool
- **PostgreSQL**: Database (via psycopg2-binary)
- **Uvicorn**: ASGI server
