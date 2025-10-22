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
- **status**: Enum (PENDING, PROCESSING, IN_PROGRESS, COMPLETED, FAILED, CANCELLED)
- **user_id**: UUID (Foreign Key to users)
- **file_path**: String (Optional) - مسیر فایل آپلود شده
- **result_path**: String (Optional) - مسیر فایل نتیجه پردازش
- **due_date**: DateTime (Optional)
- **completed_at**: DateTime (Optional) - زمان تکمیل task
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
│   │   ├── 002_add_file_path_to_tasks.py
│   │   └── 003_add_processing_status_and_result_fields.py
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

worker/
├── __init__.py            # Worker module initialization
├── tasks.py               # Audio transcription worker tasks
└── requirements.txt       # Worker dependencies
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

#### Celery Configuration

The Celery application is configured with:
- **Broker**: Redis (database 2 by default)
- **Result Backend**: Redis (same as broker)
- **Serialization**: JSON format for security and compatibility
- **Timezone**: UTC (matching database timezone)
- **Task Routing**: Different queues for media and default tasks
- **Result Expiration**: 1 hour
- **Connection Retry**: Automatic retry on connection failures

#### Available Task Wrappers

The application provides several task wrappers for background processing:

##### 1. Audio Transcription
```python
from worker.tasks import transcribe_audio

# Queue audio transcription task
result = transcribe_audio.delay(task_id="uuid-string", audio_file_path="audio.mp3")
```

Features:
- **Singleton Model**: Uses optimized singleton pattern for warm start reduction
- **Resource Monitoring**: Real-time VRAM/RAM monitoring to prevent OOM
- Updates task status to PROCESSING during execution
- Reads audio file from `/storage/uploads/`
- Performs speech-to-text conversion with configurable model and precision
- Saves transcription result to `/storage/results/`
- Updates database with result_path, completed_at, and status=COMPLETED
- On error, sets status=FAILED with comprehensive logging and resource diagnostics
- Language detection (supports Persian/Farsi and auto-detection)
- Confidence scoring and duration calculation
- Thread-safe model loading with automatic memory optimization

Implementation details:
- File reading: Audio file is read from `/storage/uploads/` directory
- Result storage: JSON result is saved to `/storage/results/{task_id}_transcription.json`
- Database updates: Automatic status tracking (PROCESSING → COMPLETED/FAILED)
- Error handling: Comprehensive error logging and status updates

##### 2. Video Processing
```python
from app.tasks import process_video

# Queue video processing task
result = process_video.delay(task_id="uuid-string", video_file_path="/path/to/video.mp4")
```

Features:
- Thumbnail generation
- Format conversion
- Metadata extraction
- Resolution detection

##### 3. Text Analysis
```python
from app.tasks import analyze_text

# Queue text analysis task
result = analyze_text.delay(task_id="uuid-string", text_content="متن برای تحلیل")
```

Features:
- Sentiment analysis
- Keyword extraction
- Language detection
- Content summarization

##### 4. File Processing (Generic)
```python
from app.tasks import process_task_file

# Queue generic file processing task
result = process_task_file.delay(task_id="uuid-string", file_path="/path/to/file")
```

#### Starting Celery Workers

The worker includes optimized model initialization with singleton pattern for warm start reduction and comprehensive resource monitoring to prevent OOM errors.

##### Quick Start (Using Entrypoint Script)

```bash
# Set environment variables
export REDIS_URL=redis://localhost:6379
export REDIS_QUEUE_DB=2
export STORAGE_ROOT=/storage
export DATABASE_URL=postgresql://user:password@localhost:5432/writers_db

# Model configuration (for optimized performance)
export MODEL_DEVICE=cuda                    # cuda or cpu
export MODEL_DEVICE_INDEX=0                 # GPU index (0, 1, 2, ...)
export MODEL_COMPUTE_TYPE=float16           # float16, int8, or float32
export MODEL_NAME=base                      # tiny, base, small, medium, large

# Worker configuration
export WORKER_CONCURRENCY=2                 # Number of concurrent workers
export WORKER_QUEUE=media                   # Queue name(s)

# Resource monitoring configuration
export ENABLE_RESOURCE_MONITORING=true      # Enable VRAM/RAM monitoring
export VRAM_WARNING_THRESHOLD=0.85          # VRAM warning at 85%
export RAM_WARNING_THRESHOLD=0.90           # RAM warning at 90%

# Start worker with entrypoint script
cd /workspace/worker
./entrypoint.sh
```

##### Manual Start (Advanced)

```bash
# Start default queue worker (from backend directory)
cd backend
celery -A app.celery_app worker --loglevel=info -Q default

# Start media queue worker with optimized settings
cd backend
celery -A app.celery_app worker \
    --loglevel=info \
    --concurrency=2 \
    --queues=media \
    --max-tasks-per-child=100

# Start worker for all queues
cd backend
celery -A app.celery_app worker --loglevel=info -Q default,media
```

##### Worker Concurrency Guidelines

The `--concurrency` parameter controls how many worker processes run in parallel. Choosing the right value is critical for optimal performance and resource utilization:

**For Heavy Models (Large/Medium Whisper):**
- **GPU**: `concurrency=1` or `2`
- **Reason**: Large models consume significant GPU memory
- Higher concurrency increases OOM (Out of Memory) risk

**For Light Models (Tiny/Base Whisper):**
- **GPU**: `concurrency=2` to `4`
- **CPU**: `concurrency=(CPU cores) / 2`
- **Reason**: Smaller models require less memory

**For Multi-GPU Systems:**
- Run multiple workers with different `MODEL_DEVICE_INDEX`
- Example: worker1 on GPU:0, worker2 on GPU:1

**General Considerations:**
- **VRAM Available**: Ensure sufficient GPU memory
- **System RAM**: Each worker needs ~2-4GB RAM
- **I/O**: For large files, use lower concurrency
- **Formula**: `concurrency = min(GPU_VRAM_GB / MODEL_SIZE_GB, CPU_CORES / 2, MAX_CONCURRENT_TASKS)`

**Example Configurations:**
- GPU 8GB VRAM + Whisper Base: `concurrency=2`
- GPU 16GB VRAM + Whisper Medium: `concurrency=2`
- GPU 24GB VRAM + Whisper Large: `concurrency=1` or `2`
- CPU 16 cores + Whisper Base: `concurrency=4`

**Best Practice**: Start with low concurrency and gradually increase while monitoring resources to find optimal value.

#### Worker Directory

The `worker/` directory contains dedicated worker tasks for audio processing:

**Structure:**
- `worker/tasks.py`: Audio transcription task implementation
- `worker/requirements.txt`: Worker-specific dependencies

**Features:**
- Access to shared code (Pydantic models from `backend/app/models/`)
- Imports Celery configuration from `backend/app/celery_app.py`
- Proper database status tracking (PROCESSING, COMPLETED, FAILED)
- File handling from `/storage/uploads/` and `/storage/results/`
- Comprehensive error logging and handling

**Running Worker Tasks:**
```bash
# Ensure worker can access backend modules
export PYTHONPATH=/workspace:$PYTHONPATH

# Start worker from backend directory
cd backend
celery -A app.celery_app worker --loglevel=info -Q media
```

**Model Optimization (Singleton Pattern):**

The worker implements a singleton pattern for model initialization to significantly reduce warm start time and improve performance:

- **Lazy Loading**: Model is loaded only once on first use
- **Thread-Safe**: Uses locking mechanism for safe concurrent access
- **Memory Efficient**: Model is shared across all tasks in the same worker process
- **Configurable**: Supports device selection, compute type, and GPU index

Configuration options:
```python
MODEL_DEVICE=cuda          # Device: cuda or cpu
MODEL_DEVICE_INDEX=0       # GPU index for multi-GPU systems
MODEL_COMPUTE_TYPE=float16 # Computation precision: float16, int8, float32
MODEL_NAME=base           # Model size: tiny, base, small, medium, large
```

Benefits:
- Reduces cold start latency from ~10-30s to <1s for subsequent tasks
- Prevents redundant model loading in memory
- Better GPU utilization

**Resource Monitoring:**

The worker includes comprehensive VRAM and RAM monitoring to prevent OOM errors:

**Features:**
- Real-time GPU memory tracking via nvidia-smi
- System RAM monitoring via psutil
- Automatic warnings when usage exceeds thresholds
- Resource logging at key points (task start, before/after transcription, completion)

**Configuration:**
```bash
ENABLE_RESOURCE_MONITORING=true   # Enable/disable monitoring
VRAM_WARNING_THRESHOLD=0.85       # Warn at 85% VRAM usage
RAM_WARNING_THRESHOLD=0.90        # Warn at 90% RAM usage
```

**Monitoring Points:**
1. Task start - baseline resource usage
2. Before transcription - pre-processing check
3. After model initialization - verify model loaded successfully
4. After transcription - detect memory leaks
5. Task completion/error - final state

**Example Log Output:**
```
[Task start] RAM: 4096MB / 16384MB (25.0%)
[Task start] VRAM (GPU 0): 2048MB / 8192MB (25.0%) | GPU Utilization: 15.0%
[After model initialization] VRAM (GPU 0): 3500MB / 8192MB (42.7%)
[Before transcription] RAM: 4200MB / 16384MB (25.6%)
[After transcription] VRAM (GPU 0): 4096MB / 8192MB (50.0%)
[Task completed successfully] RAM: 4100MB / 16384MB (25.0%)
```

**OOM Prevention:**
- Warnings logged when thresholds exceeded
- Helps identify memory-hungry tasks
- Enables proactive scaling decisions
- Assists in debugging memory issues

#### Monitoring Celery Tasks

```bash
# Monitor Celery events in real-time
celery -A app.celery_app events

# Check worker status
celery -A app.celery_app inspect active

# Check registered tasks
celery -A app.celery_app inspect registered

# Purge all tasks from queue
celery -A app.celery_app purge
```

### Configuration

#### Required Environment Variables

**Database & Cache:**
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection URL (default: `redis://localhost:6379`)
- `REDIS_QUEUE_DB`: Redis database for Celery queue (default: `2`)

**Storage:**
- `STORAGE_ROOT`: Root directory for file storage (default: `/storage`)
  - Uploads directory: `${STORAGE_ROOT}/uploads/`
  - Results directory: `${STORAGE_ROOT}/results/`
  - Models directory: `${STORAGE_ROOT}/models/`

**Worker Configuration:**
- `WORKER_CONCURRENCY`: Number of concurrent worker processes (default: `2`)
  - See "Worker Concurrency Guidelines" section for selection guidance
- `WORKER_QUEUE`: Queue name(s) to process (default: `media`)
- `WORKER_LOG_LEVEL`: Logging level (default: `info`)
- `WORKER_MAX_TASKS_PER_CHILD`: Max tasks before worker restart (default: `100`)

**Model Configuration (Singleton Pattern):**
- `MODEL_DEVICE`: Computing device (default: `cuda`)
  - Options: `cuda`, `cpu`
- `MODEL_DEVICE_INDEX`: GPU index for multi-GPU systems (default: `0`)
  - For GPU 0: `0`, GPU 1: `1`, etc.
- `MODEL_COMPUTE_TYPE`: Computation precision (default: `float16`)
  - Options: `float16` (faster, less memory), `int8` (smallest), `float32` (highest quality)
- `MODEL_NAME`: Model size (default: `base`)
  - Options: `tiny`, `base`, `small`, `medium`, `large`
  - Larger models = better quality but more memory and slower

**Resource Monitoring:**
- `ENABLE_RESOURCE_MONITORING`: Enable VRAM/RAM monitoring (default: `true`)
  - Set to `false` to disable monitoring overhead
- `VRAM_WARNING_THRESHOLD`: VRAM usage threshold for warnings (default: `0.85`)
  - Value between 0.0 and 1.0 (0.85 = 85%)
- `RAM_WARNING_THRESHOLD`: RAM usage threshold for warnings (default: `0.90`)
  - Value between 0.0 and 1.0 (0.90 = 90%)

**Storage Directory Structure:**
```
/storage/
├── uploads/          # Uploaded audio files
│   └── {filename}    # Original uploaded files
├── results/          # Processing results
│   └── {task_id}_transcription.json  # Transcription results
└── models/           # Downloaded ML models
    └── {model_name}  # Cached model files
```

## Frontend (Next.js 14)

The application includes a modern frontend built with Next.js 14, TypeScript, and App Router.

### Frontend Structure

```
frontend/
├── app/                    # Next.js 14 App Router
│   ├── layout.tsx         # Root layout with AuthProvider
│   ├── page.tsx           # Home page (redirects to login/dashboard)
│   ├── globals.css        # Global styles
│   ├── login/             # Login page
│   │   └── page.tsx
│   ├── register/          # Register page
│   │   └── page.tsx
│   └── dashboard/         # Protected dashboard pages
│       ├── page.tsx       # Task list with real-time polling
│       ├── upload/        # Audio file upload
│       │   └── page.tsx
│       └── tasks/         # Task details
│           └── [taskId]/
│               └── page.tsx
├── contexts/              # React contexts
│   └── AuthContext.tsx    # Authentication context
├── hooks/                 # Custom React hooks
│   └── useAuth.ts         # Authentication hooks
├── lib/                   # Utility libraries
│   ├── api.ts             # Axios instance with interceptors
│   └── auth.ts            # Authentication service
├── types/                 # TypeScript type definitions
│   ├── auth.ts            # Auth-related types
│   └── task.ts            # Task-related types
├── middleware.ts          # Next.js middleware for route protection
├── package.json           # Dependencies and scripts
├── tsconfig.json          # TypeScript configuration
├── next.config.js         # Next.js configuration
└── .env.local             # Environment variables
```

### Authentication Features

The frontend implements custom JWT authentication with httpOnly cookies:

- **Custom JWT Implementation**: Direct integration with FastAPI backend
- **HttpOnly Cookies**: Secure token storage (access_token and refresh_token)
- **Protected Routes**: Middleware-based route protection for `/dashboard`
- **Authentication Context**: Global auth state management
- **Custom Hooks**: `useAuth()`, `useUser()`, `useRequireAuth()`
- **Automatic Redirects**: Login redirects, post-auth routing
- **Error Handling**: Automatic 401 handling and redirects

### Setup and Development

#### Install Dependencies

```bash
cd frontend
npm install
```

#### Configure Environment

Update `.env.local` with your backend URL:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### Run Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:3000`.

#### Build for Production

```bash
npm run build
npm start
```

### Authentication Flow

1. **Registration**: User submits form → POST `/auth/register` → Cookies set → Redirect to dashboard
2. **Login**: User submits credentials → POST `/auth/login` → Cookies set → Redirect to dashboard
3. **Protected Routes**: Middleware checks `access_token` cookie → Allow/Deny access
4. **Current User**: Frontend calls GET `/auth/me` to get user data
5. **Logout**: POST `/auth/logout` → Cookies cleared → Redirect to login

### Available Pages

- **`/`**: Home page (auto-redirects to `/login` or `/dashboard`)
- **`/login`**: Login page with email/password form
- **`/register`**: Registration page with user details form
- **`/dashboard`**: Protected dashboard page with task list and real-time updates (requires authentication)
- **`/dashboard/upload`**: Audio file upload page with drag-and-drop support
- **`/dashboard/tasks/[taskId]`**: Task details page with comprehensive information and status tracking

### Middleware Protection

The Next.js middleware (`middleware.ts`) automatically:

- Protects `/dashboard` routes (requires `access_token` cookie)
- Redirects unauthenticated users to `/login`
- Redirects authenticated users away from `/login` and `/register`
- Preserves original URL for post-login redirect

### Custom Hooks

#### `useAuth()`

Access full authentication context:

```typescript
const { user, loading, login, register, logout, refreshUser } = useAuth();
```

#### `useUser()`

Get current user and loading state:

```typescript
const { user, loading } = useUser();
```

#### `useRequireAuth()`

Require authentication (auto-redirect if not authenticated):

```typescript
const { user, loading } = useRequireAuth();
```

### API Integration

The frontend uses Axios with interceptors for API communication:

- **Base URL**: Configured via `NEXT_PUBLIC_API_URL`
- **Credentials**: `withCredentials: true` for cookie support
- **Error Handling**: Automatic 401 handling and redirect
- **Headers**: JSON content type by default

### Audio File Upload

The frontend includes a dedicated upload page (`/dashboard/upload`) for uploading audio files with the following features:

#### Features

- **Drag-and-Drop Support**: Intuitive dropzone interface for easy file selection
- **File Type Validation**: Accepts only audio files (MP3, WAV, M4A, AAC, OGG, FLAC)
- **File Size Limit**: Maximum 100MB per file
- **Real-time Upload Progress**: Visual progress bar showing upload percentage
- **Status Management**: Clear feedback for uploading, success, and error states
- **Auto-redirect**: Automatically redirects to dashboard after successful upload
- **Form Integration**: Title (required) and description (optional) fields
- **Auto-fill Title**: Automatically extracts filename as title suggestion

#### Usage

1. Navigate to `/dashboard/upload`
2. Drag and drop an audio file or click to browse
3. File is validated for type and size
4. Enter title (auto-filled from filename) and optional description
5. Click "آپلود فایل" to upload
6. Monitor upload progress
7. Automatically redirected to dashboard after successful upload

#### Technical Details

- **API Endpoint**: `POST /api/v1/tasks`
- **Content Type**: `multipart/form-data`
- **Request Format**:
  - `file`: Audio file (required)
  - `title`: Task title (required)
  - `description`: Task description (optional)
- **Response**: Returns task object with `202 Accepted` status
- **Background Processing**: File is queued for transcription via Celery

#### Validation Rules

- **Accepted Formats**: `.mp3`, `.wav`, `.m4a`, `.aac`, `.ogg`, `.flac`
- **Accepted MIME Types**: `audio/mpeg`, `audio/mp3`, `audio/wav`, `audio/wave`, `audio/x-wav`, `audio/aac`, `audio/m4a`, `audio/x-m4a`, `audio/ogg`, `audio/flac`
- **Maximum Size**: 100MB (104,857,600 bytes)
- **Title**: Required, 1-255 characters
- **Description**: Optional

### Task Dashboard

The dashboard page (`/dashboard`) provides a comprehensive task management interface with real-time updates:

#### Features

- **Real-time Task List**: Displays all user tasks with automatic polling every 10 seconds
- **Manual Refresh**: Button to manually refresh task list on demand
- **Task Cards**: Beautiful card-based layout with status badges and metadata
- **Status Indicators**: Color-coded badges for different task states:
  - **Pending** (در انتظار): Yellow badge for tasks waiting to be processed
  - **Processing** (در حال پردازش): Blue animated badge for tasks currently being processed
  - **Completed** (تکمیل شده): Green badge for successfully completed tasks
  - **Failed** (ناموفق): Red badge for tasks that encountered errors
  - **Cancelled** (لغو شده): Gray badge for cancelled tasks
- **Task Navigation**: Click on any task card to view detailed information
- **Metadata Display**: Shows creation time, completion time, file status, and result availability
- **Responsive Design**: Grid layout that adapts to different screen sizes
- **Empty State**: Helpful message when no tasks exist

#### Task Details Page

The task details page (`/dashboard/tasks/[taskId]`) provides comprehensive information about individual tasks:

**Features:**
- **Full Task Information**: Title, description, status, and all timestamps
- **Real-time Updates**: Polls every 10 seconds to show latest task status
- **Manual Refresh**: Button to manually refresh task details
- **File Information**: Shows input file and result file availability
- **Comprehensive Metadata**: Created time, updated time, due date, completion time
- **File Paths**: Displays full file paths for uploaded and result files
- **Task IDs**: Shows task ID and user ID for reference
- **Download Action**: Download button for completed tasks with results (ready for implementation)
- **Error Handling**: Graceful handling of missing or unauthorized tasks

#### Data Fetching with SWR

The frontend uses **SWR (Stale-While-Revalidate)** for efficient data fetching:

- **Automatic Polling**: Tasks are refreshed every 10 seconds (configurable)
- **Revalidation on Focus**: Automatically refreshes when user returns to the tab
- **Optimistic Updates**: Shows cached data immediately while fetching fresh data
- **Error Handling**: Graceful error messages when API requests fail
- **Manual Refresh**: `mutate()` function for on-demand data refresh

#### API Integration

- **Endpoint**: `GET /api/v1/tasks`
- **Response**: `TaskListResponse` with tasks array and total count
- **Authentication**: Automatic authentication via httpOnly cookies
- **Pagination**: Supports skip/limit parameters (default: 0/100)
- **Filtering**: Optional status filter for task states

### Styling

The application uses custom CSS with:

- Modern gradient backgrounds
- Card-based layouts with hover effects
- Responsive design with mobile optimization
- Persian/Farsi language support
- Clean and intuitive UI
- Drag-and-drop upload interface with visual feedback
- Animated status badges for processing tasks
- Color-coded status indicators
- Grid-based task layout

## Dependencies

### Backend

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

### Frontend

- **Next.js 14**: React framework with App Router
- **React 18**: UI library
- **TypeScript**: Type-safe JavaScript
- **Axios**: HTTP client for API requests
- **SWR**: React Hooks library for data fetching with caching and real-time updates
- **js-cookie**: Cookie manipulation (for client-side reading if needed)
