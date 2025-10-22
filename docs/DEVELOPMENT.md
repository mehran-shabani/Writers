# راهنمای توسعه

این سند راهنمای کامل برای توسعه‌دهندگانی که می‌خواهند روی پروژه Writers کار کنند یا به آن contribute کنند را ارائه می‌دهد.

## 🚀 شروع به کار

### پیش‌نیازها

مطمئن شوید که این ابزارها را نصب کرده‌اید:

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+
- Git
- یک IDE مناسب (VSCode، PyCharm، یا Cursor)

### Clone و Setup

```bash
# Clone repository
git clone https://github.com/yourusername/writers.git
cd writers

# ایجاد branch جدید
git checkout -b feature/your-feature-name
```

### تنظیم Backend

```bash
cd backend

# ایجاد virtual environment
python3 -m venv venv
source venv/bin/activate

# نصب dependencies
pip install -r requirements.txt

# نصب dev dependencies
pip install pytest pytest-cov black flake8 mypy

# اجرای migrations
alembic upgrade head

# اجرای backend
uvicorn app.main:app --reload
```

### تنظیم Frontend

```bash
cd frontend

# نصب dependencies
npm install

# اجرای development server
npm run dev
```

### تنظیم Worker

```bash
cd worker

# ایجاد virtual environment
python3 -m venv venv
source venv/bin/activate

# نصب dependencies
pip install -r requirements.txt

# اجرای worker
celery -A tasks worker --loglevel=info
```

## 📁 ساختار پروژه

### Backend Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # نقطه ورود اصلی
│   ├── db.py                   # تنظیمات database
│   ├── celery_app.py          # تنظیمات Celery
│   │
│   ├── auth/                   # ماژول احراز هویت
│   │   ├── __init__.py
│   │   ├── dependencies.py    # Dependency injection
│   │   ├── jwt.py             # JWT utilities
│   │   ├── router.py          # API endpoints
│   │   ├── schemas.py         # Pydantic schemas
│   │   └── utils.py           # Helper functions
│   │
│   ├── models/                 # Database models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── task.py
│   │
│   └── routers/                # API routers
│       ├── __init__.py
│       ├── tasks.py
│       └── schemas.py
│
├── alembic/                    # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│
├── tests/                      # تست‌ها
│   ├── conftest.py
│   ├── auth/
│   └── ...
│
├── requirements.txt
└── pytest.ini
```

### Frontend Structure

```
frontend/
├── app/
│   ├── api/                    # Next.js API Routes (Proxy)
│   │   ├── auth/
│   │   └── tasks/
│   │
│   ├── dashboard/              # Dashboard pages
│   │   ├── page.tsx
│   │   ├── tasks/
│   │   └── upload/
│   │
│   ├── login/
│   ├── register/
│   ├── layout.tsx              # Root layout
│   └── page.tsx                # Home page
│
├── contexts/                   # React Contexts
│   └── AuthContext.tsx
│
├── hooks/                      # Custom hooks
│   └── useAuth.ts
│
├── lib/                        # Utilities
│   ├── api.ts
│   └── auth.ts
│
├── types/                      # TypeScript types
│   ├── auth.ts
│   └── task.ts
│
├── __tests__/                  # تست‌ها
├── package.json
└── tsconfig.json
```

## 🛠️ راهنمای توسعه Backend

### ایجاد API Endpoint جدید

#### 1. تعریف Schema (Pydantic)

```python
# backend/app/routers/schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    owner_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
```

#### 2. ایجاد Router

```python
# backend/app/routers/tasks.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from ..db import get_session
from ..models.task import Task
from ..auth.dependencies import get_current_user
from .schemas import TaskCreate, TaskResponse

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

@router.post("/", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    """ایجاد تسک جدید"""
    task = Task(
        title=task_data.title,
        description=task_data.description,
        owner_id=current_user.id
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    """دریافت لیست تسک‌ها"""
    statement = select(Task).where(
        Task.owner_id == current_user.id
    ).offset(skip).limit(limit)
    tasks = session.exec(statement).all()
    return tasks
```

#### 3. اضافه کردن به Main App

```python
# backend/app/main.py
from .routers.tasks import router as tasks_router

app.include_router(tasks_router)
```

### ایجاد Database Model جدید

```python
# backend/app/models/comment.py
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from datetime import datetime

class Comment(SQLModel, table=True):
    __tablename__ = "comments"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str = Field(max_length=1000)
    task_id: int = Field(foreign_key="tasks.id")
    user_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    task: Optional["Task"] = Relationship(back_populates="comments")
    user: Optional["User"] = Relationship(back_populates="comments")
```

### ایجاد Migration

```bash
# ایجاد migration با autogenerate
alembic revision --autogenerate -m "add comments table"

# بررسی migration
cat alembic/versions/xxx_add_comments_table.py

# اجرای migration
alembic upgrade head
```

### ایجاد Celery Task

```python
# worker/tasks.py
from celery import Celery
import time

celery_app = Celery('tasks', broker='redis://localhost:6379/2')

@celery_app.task(name='tasks.process_file')
def process_file(file_path: str, task_id: int):
    """پردازش فایل به صورت async"""
    try:
        # پردازش فایل
        time.sleep(5)  # Simulate processing
        
        # به‌روزرسانی وضعیت در database
        # ...
        
        return {
            'status': 'success',
            'task_id': task_id,
            'processed_at': datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e)
        }
```

### نوشتن تست

```python
# backend/tests/test_tasks.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_task(auth_headers):
    """تست ایجاد تسک"""
    response = client.post(
        "/api/tasks/",
        json={
            "title": "Test Task",
            "description": "Test Description"
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert "id" in data

def test_get_tasks(auth_headers):
    """تست دریافت لیست تسک‌ها"""
    response = client.get("/api/tasks/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

## 🎨 راهنمای توسعه Frontend

### ایجاد صفحه جدید

```tsx
// app/dashboard/profile/page.tsx
'use client';

import { useAuth } from '@/hooks/useAuth';

export default function ProfilePage() {
  const { user } = useAuth();

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">پروفایل کاربری</h1>
      {user && (
        <div>
          <p>ایمیل: {user.email}</p>
          <p>نام: {user.full_name}</p>
        </div>
      )}
    </div>
  );
}
```

### ایجاد API Route (Proxy)

```typescript
// app/api/profile/route.ts
import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function GET(request: NextRequest) {
  try {
    const cookies = request.cookies;
    const accessToken = cookies.get('access_token')?.value;

    const response = await fetch(`${BACKEND_URL}/api/profile`, {
      headers: {
        'Cookie': `access_token=${accessToken}`,
      },
    });

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to fetch profile' },
      { status: 500 }
    );
  }
}

export async function PUT(request: NextRequest) {
  try {
    const body = await request.json();
    const cookies = request.cookies;
    const accessToken = cookies.get('access_token')?.value;

    const response = await fetch(`${BACKEND_URL}/api/profile`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Cookie': `access_token=${accessToken}`,
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to update profile' },
      { status: 500 }
    );
  }
}
```

### ایجاد Custom Hook

```typescript
// hooks/useTasks.ts
import useSWR from 'swr';
import { Task } from '@/types/task';

const fetcher = (url: string) => fetch(url).then(res => res.json());

export function useTasks() {
  const { data, error, mutate } = useSWR<Task[]>('/api/tasks', fetcher);

  return {
    tasks: data,
    isLoading: !error && !data,
    isError: error,
    mutate,
  };
}

export function useTask(id: number) {
  const { data, error, mutate } = useSWR<Task>(
    id ? `/api/tasks/${id}` : null,
    fetcher
  );

  return {
    task: data,
    isLoading: !error && !data,
    isError: error,
    mutate,
  };
}
```

### ایجاد Component

```tsx
// components/TaskCard.tsx
import { Task } from '@/types/task';

interface TaskCardProps {
  task: Task;
  onDelete?: (id: number) => void;
}

export function TaskCard({ task, onDelete }: TaskCardProps) {
  return (
    <div className="border rounded-lg p-4 shadow hover:shadow-lg transition">
      <h3 className="text-lg font-semibold">{task.title}</h3>
      <p className="text-gray-600 mt-2">{task.description}</p>
      
      <div className="mt-4 flex justify-between items-center">
        <span className={`px-2 py-1 rounded text-sm ${
          task.status === 'completed' ? 'bg-green-100 text-green-800' :
          task.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
          'bg-gray-100 text-gray-800'
        }`}>
          {task.status}
        </span>
        
        {onDelete && (
          <button
            onClick={() => onDelete(task.id)}
            className="text-red-600 hover:text-red-800"
          >
            حذف
          </button>
        )}
      </div>
    </div>
  );
}
```

### نوشتن تست

```typescript
// __tests__/components/TaskCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { TaskCard } from '@/components/TaskCard';

describe('TaskCard', () => {
  const mockTask = {
    id: 1,
    title: 'Test Task',
    description: 'Test Description',
    status: 'pending',
    owner_id: 1,
    created_at: new Date().toISOString(),
  };

  it('renders task information', () => {
    render(<TaskCard task={mockTask} />);
    
    expect(screen.getByText('Test Task')).toBeInTheDocument();
    expect(screen.getByText('Test Description')).toBeInTheDocument();
  });

  it('calls onDelete when delete button clicked', () => {
    const handleDelete = jest.fn();
    render(<TaskCard task={mockTask} onDelete={handleDelete} />);
    
    const deleteButton = screen.getByText('حذف');
    fireEvent.click(deleteButton);
    
    expect(handleDelete).toHaveBeenCalledWith(1);
  });
});
```

## 🧪 تست‌نویسی

### اجرای تست‌ها

#### Backend

```bash
cd backend

# اجرای تمام تست‌ها
pytest

# اجرای با coverage
pytest --cov=app --cov-report=html

# اجرای یک فایل خاص
pytest tests/test_auth.py

# اجرای با verbose output
pytest -v

# اجرای فقط تست‌های mark شده
pytest -m "slow"
```

#### Frontend

```bash
cd frontend

# اجرای تست‌ها
npm test

# اجرای با coverage
npm run test:coverage

# اجرای در watch mode
npm run test:watch
```

### Coverage Target

- Backend: حداقل 80% coverage
- Frontend: حداقل 70% coverage

## 📝 Code Style Guide

### Python (Backend)

استفاده از **Black** برای formatting:

```bash
# Format کردن تمام فایل‌ها
black backend/app

# بررسی بدون تغییر
black --check backend/app
```

استفاده از **Flake8** برای linting:

```bash
flake8 backend/app
```

استفاده از **mypy** برای type checking:

```bash
mypy backend/app
```

#### قوانین کدنویسی Python

- استفاده از Type Hints
- نام‌گذاری واضح و معنادار
- Docstrings برای توابع و کلاس‌ها
- Maximum line length: 88 کاراکتر (Black default)

```python
from typing import Optional, List

def get_user_tasks(
    user_id: int,
    status: Optional[str] = None,
    limit: int = 100
) -> List[Task]:
    """دریافت تسک‌های یک کاربر
    
    Args:
        user_id: شناسه کاربر
        status: فیلتر بر اساس وضعیت (اختیاری)
        limit: حداکثر تعداد نتایج
        
    Returns:
        لیست تسک‌ها
    """
    # Implementation
    pass
```

### TypeScript/JavaScript (Frontend)

استفاده از **ESLint** و **Prettier**:

```bash
# Lint
npm run lint

# Fix
npm run lint:fix

# Format
npm run format
```

#### قوانین کدنویسی TypeScript

- استفاده کامل از TypeScript Types
- استفاده از Functional Components
- استفاده از Hooks
- Naming conventions: camelCase برای متغیرها، PascalCase برای Components

```typescript
interface User {
  id: number;
  email: string;
  fullName?: string;
}

interface UserCardProps {
  user: User;
  onEdit?: (user: User) => void;
}

export function UserCard({ user, onEdit }: UserCardProps): JSX.Element {
  const handleEdit = () => {
    if (onEdit) {
      onEdit(user);
    }
  };

  return (
    <div className="user-card">
      {/* ... */}
    </div>
  );
}
```

## 🔀 Git Workflow

### Branch Strategy

```
main                    - Production-ready code
├── develop            - Development branch
    ├── feature/*      - Feature branches
    ├── bugfix/*       - Bug fix branches
    └── hotfix/*       - Urgent fixes
```

### Commit Messages

استفاده از **Conventional Commits**:

```
feat: اضافه کردن قابلیت آپلود فایل
fix: رفع مشکل احراز هویت
docs: به‌روزرسانی مستندات API
style: اصلاح formatting کد
refactor: بازنویسی تابع get_tasks
test: اضافه کردن تست برای auth
chore: به‌روزرسانی dependencies
```

### Pull Request Process

1. ایجاد branch از `develop`
2. انجام تغییرات
3. نوشتن/به‌روزرسانی تست‌ها
4. اطمینان از pass شدن تمام تست‌ها
5. ایجاد Pull Request
6. بررسی Code Review
7. Merge به `develop`

### PR Template

```markdown
## توضیحات
[توضیح مختصر تغییرات]

## نوع تغییرات
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## چک‌لیست
- [ ] تست‌ها pass می‌شوند
- [ ] Coverage کاهش نیافته
- [ ] مستندات به‌روز شده
- [ ] Code review انجام شده

## تست
[نحوه تست تغییرات]

## Screenshots
[در صورت نیاز]
```

## 🐛 Debug Tips

### Backend Debugging

```python
# استفاده از pdb
import pdb; pdb.set_trace()

# Logging
import logging
logger = logging.getLogger(__name__)
logger.debug("Debug message")

# FastAPI debug mode
uvicorn app.main:app --reload --log-level debug
```

### Frontend Debugging

```typescript
// Console logging
console.log('Debug:', variable);

// React DevTools
// نصب React Developer Tools extension

// Network debugging
// استفاده از Browser DevTools > Network tab
```

## 📚 منابع یادگیری

### Backend
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Celery Documentation](https://docs.celeryproject.org/)

### Frontend
- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev/)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)

### Best Practices
- [Python PEP 8](https://peps.python.org/pep-0008/)
- [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- [Clean Code principles](https://github.com/ryanmcdermott/clean-code-javascript)

## 🤝 Contribution Guidelines

1. Fork the repository
2. Create feature branch
3. Make your changes
4. Write/update tests
5. Ensure all tests pass
6. Update documentation
7. Submit pull request

---

برای سوالات یا کمک، به [GitHub Discussions](https://github.com/yourusername/writers/discussions) مراجعه کنید.
