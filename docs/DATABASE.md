# مستندات پایگاه داده

این سند ساختار پایگاه داده، جداول، روابط و مدیریت Migration‌ها در سیستم Writers را شرح می‌دهد.

## 📊 نمای کلی

سیستم Writers از **PostgreSQL** به عنوان پایگاه داده اصلی استفاده می‌کند.

### اطلاعات اتصال

```env
DATABASE_URL=postgresql://writers_user:password@localhost:5432/writers_db
```

### ابزارهای مورد استفاده

- **SQLAlchemy**: ORM برای Python
- **Alembic**: مدیریت Migration
- **psycopg2**: PostgreSQL Adapter

## 🗄️ ساختار جداول

### جدول `users`

ذخیره اطلاعات کاربران سیستم

| ستون | نوع | توضیحات | قیدها |
|------|-----|---------|--------|
| id | Integer | شناسه یکتا | Primary Key, Auto Increment |
| email | String(255) | ایمیل کاربر | Unique, Not Null, Index |
| hashed_password | String(255) | رمز عبور هش شده | Not Null |
| full_name | String(255) | نام کامل | Nullable |
| is_active | Boolean | فعال بودن حساب | Default: True |
| is_superuser | Boolean | دسترسی مدیریتی | Default: False |
| created_at | DateTime | تاریخ ایجاد | Default: now() |
| updated_at | DateTime | تاریخ به‌روزرسانی | Default: now(), On Update |

**Indexes:**
```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);
```

**Model Definition:**
```python
class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    hashed_password: str = Field(max_length=255)
    full_name: Optional[str] = Field(default=None, max_length=255)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    tasks: List["Task"] = Relationship(back_populates="owner")
```

---

### جدول `tasks`

ذخیره وظایف کاربران

| ستون | نوع | توضیحات | قیدها |
|------|-----|---------|--------|
| id | Integer | شناسه یکتا | Primary Key, Auto Increment |
| title | String(500) | عنوان تسک | Not Null |
| description | Text | توضیحات تسک | Nullable |
| status | String(50) | وضعیت تسک | Default: 'pending' |
| file_path | String(1000) | مسیر فایل آپلود شده | Nullable |
| processing_status | String(50) | وضعیت پردازش | Nullable |
| processing_result | JSON | نتیجه پردازش | Nullable |
| owner_id | Integer | شناسه کاربر | Foreign Key, Not Null, Index |
| created_at | DateTime | تاریخ ایجاد | Default: now() |
| updated_at | DateTime | تاریخ به‌روزرسانی | Default: now(), On Update |

**Foreign Keys:**
```sql
ALTER TABLE tasks 
ADD CONSTRAINT fk_tasks_owner 
FOREIGN KEY (owner_id) REFERENCES users(id) 
ON DELETE CASCADE;
```

**Indexes:**
```sql
CREATE INDEX idx_tasks_owner_id ON tasks(owner_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);
CREATE INDEX idx_tasks_processing_status ON tasks(processing_status);
```

**Status Values:**
- `pending`: در انتظار
- `in_progress`: در حال انجام
- `completed`: تکمیل شده
- `cancelled`: لغو شده

**Processing Status Values:**
- `pending`: در انتظار پردازش
- `processing`: در حال پردازش
- `success`: پردازش موفق
- `failed`: پردازش ناموفق

**Model Definition:**
```python
class Task(SQLModel, table=True):
    __tablename__ = "tasks"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=500)
    description: Optional[str] = Field(default=None)
    status: str = Field(default="pending", max_length=50)
    file_path: Optional[str] = Field(default=None, max_length=1000)
    processing_status: Optional[str] = Field(default=None, max_length=50)
    processing_result: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    owner_id: int = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    owner: Optional[User] = Relationship(back_populates="tasks")
```

---

### جدول `alembic_version`

مدیریت نسخه Migration‌ها (ایجاد خودکار توسط Alembic)

| ستون | نوع | توضیحات |
|------|-----|---------|
| version_num | String(32) | شماره نسخه Migration | Primary Key |

## 🔗 روابط بین جداول

### دیاگرام ERD

```
┌─────────────────┐
│     users       │
├─────────────────┤
│ id (PK)         │
│ email           │
│ hashed_password │
│ full_name       │
│ is_active       │
│ is_superuser    │
│ created_at      │
│ updated_at      │
└────────┬────────┘
         │ 1
         │
         │ has many
         │
         │ N
┌────────┴────────┐
│     tasks       │
├─────────────────┤
│ id (PK)         │
│ title           │
│ description     │
│ status          │
│ file_path       │
│ processing_*    │
│ owner_id (FK)   │
│ created_at      │
│ updated_at      │
└─────────────────┘
```

### توضیح روابط

- **User ↔ Task**: رابطه یک به چند (One-to-Many)
  - هر کاربر می‌تواند چندین تسک داشته باشد
  - هر تسک متعلق به یک کاربر است
  - با حذف کاربر، تمام تسک‌های او نیز حذف می‌شوند (CASCADE)

## 🔄 مدیریت Migration

### Alembic Configuration

فایل `alembic.ini`:
```ini
[alembic]
script_location = alembic
sqlalchemy.url = postgresql://writers_user:password@localhost:5432/writers_db

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic
```

### دستورات Migration

#### ایجاد Migration جدید

```bash
cd backend

# ایجاد migration خالی
alembic revision -m "توضیحات تغییرات"

# ایجاد migration با تشخیص خودکار تغییرات
alembic revision --autogenerate -m "توضیحات"
```

#### اجرای Migration

```bash
# اجرای همه migration‌های pending
alembic upgrade head

# اجرای یک migration خاص
alembic upgrade +1

# اجرا تا revision خاص
alembic upgrade <revision_id>
```

#### بازگشت Migration

```bash
# بازگشت یک migration
alembic downgrade -1

# بازگشت تا revision خاص
alembic downgrade <revision_id>

# بازگشت کامل
alembic downgrade base
```

#### بررسی وضعیت

```bash
# نمایش revision فعلی
alembic current

# نمایش تاریخچه
alembic history

# نمایش تاریخچه با جزئیات
alembic history --verbose
```

### نمونه فایل Migration

```python
"""add file_path to tasks

Revision ID: 002
Revises: 001
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # اضافه کردن ستون جدید
    op.add_column('tasks', 
        sa.Column('file_path', sa.String(length=1000), nullable=True)
    )
    
    # اضافه کردن index
    op.create_index('idx_tasks_file_path', 'tasks', ['file_path'])

def downgrade() -> None:
    # حذف index
    op.drop_index('idx_tasks_file_path', table_name='tasks')
    
    # حذف ستون
    op.drop_column('tasks', 'file_path')
```

## 📝 Query‌های مفید

### کاربران

```sql
-- دریافت تمام کاربران فعال
SELECT * FROM users WHERE is_active = true;

-- کاربران با بیشترین تسک
SELECT u.email, COUNT(t.id) as task_count
FROM users u
LEFT JOIN tasks t ON u.id = t.owner_id
GROUP BY u.id, u.email
ORDER BY task_count DESC;

-- کاربران بدون تسک
SELECT * FROM users u
WHERE NOT EXISTS (
    SELECT 1 FROM tasks t WHERE t.owner_id = u.id
);
```

### تسک‌ها

```sql
-- تسک‌های یک کاربر خاص
SELECT * FROM tasks 
WHERE owner_id = 1
ORDER BY created_at DESC;

-- تسک‌های در حال پردازش
SELECT * FROM tasks
WHERE processing_status = 'processing';

-- آمار تسک‌ها بر اساس وضعیت
SELECT status, COUNT(*) as count
FROM tasks
GROUP BY status;

-- تسک‌های با خطا در پردازش
SELECT t.*, u.email
FROM tasks t
JOIN users u ON t.owner_id = u.id
WHERE t.processing_status = 'failed';
```

### آمار کلی

```sql
-- تعداد کل کاربران و تسک‌ها
SELECT 
    (SELECT COUNT(*) FROM users) as total_users,
    (SELECT COUNT(*) FROM tasks) as total_tasks;

-- میانگین تسک به ازای هر کاربر
SELECT AVG(task_count) as avg_tasks_per_user
FROM (
    SELECT COUNT(*) as task_count
    FROM tasks
    GROUP BY owner_id
) subquery;
```

## 🔧 بهینه‌سازی

### Indexes توصیه شده

```sql
-- بهبود performance جستجو
CREATE INDEX idx_tasks_title ON tasks USING gin(to_tsvector('english', title));

-- Index برای فیلتر ترکیبی
CREATE INDEX idx_tasks_owner_status ON tasks(owner_id, status);

-- Index برای sorting بر اساس تاریخ
CREATE INDEX idx_tasks_created_desc ON tasks(created_at DESC);
```

### تنظیمات PostgreSQL

در فایل `postgresql.conf`:

```ini
# Connection Settings
max_connections = 100
shared_buffers = 4GB

# Query Performance
work_mem = 64MB
maintenance_work_mem = 512MB
effective_cache_size = 12GB

# Write Performance
wal_buffers = 16MB
checkpoint_completion_target = 0.9

# Vacuum Settings
autovacuum = on
autovacuum_max_workers = 3
```

### تحلیل Performance

```sql
-- فعال‌سازی query timing
\timing

-- تحلیل query plan
EXPLAIN ANALYZE
SELECT * FROM tasks WHERE owner_id = 1;

-- بررسی اندازه جداول
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- بررسی indexes استفاده نشده
SELECT
    schemaname,
    tablename,
    indexname
FROM pg_indexes
WHERE schemaname = 'public'
AND indexname NOT IN (
    SELECT indexname
    FROM pg_stat_user_indexes
    WHERE idx_scan > 0
);
```

## 🔐 امنیت

### Password Hashing

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash password
hashed = pwd_context.hash("plain_password")

# Verify password
is_valid = pwd_context.verify("plain_password", hashed)
```

### SQL Injection Prevention

SQLAlchemy به صورت خودکار از SQL injection محافظت می‌کند:

```python
# امن - استفاده از parameter binding
session.query(User).filter(User.email == user_input).first()

# ناامن - استفاده از string concatenation
session.execute(f"SELECT * FROM users WHERE email = '{user_input}'")
```

### Row Level Security (RLS)

```sql
-- فعال‌سازی RLS
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;

-- Policy: کاربران فقط تسک‌های خودشان را ببینند
CREATE POLICY task_owner_policy ON tasks
    FOR ALL
    TO authenticated_user
    USING (owner_id = current_user_id());
```

## 💾 Backup و Restore

### Backup

```bash
# Backup کامل
pg_dump -U writers_user -d writers_db -F c -f backup.dump

# Backup فشرده
pg_dump -U writers_user -d writers_db | gzip > backup.sql.gz

# Backup فقط schema
pg_dump -U writers_user -d writers_db --schema-only > schema.sql

# Backup فقط data
pg_dump -U writers_user -d writers_db --data-only > data.sql
```

### Restore

```bash
# Restore از dump
pg_restore -U writers_user -d writers_db -c backup.dump

# Restore از SQL
gunzip -c backup.sql.gz | psql -U writers_user -d writers_db

# Restore با drop cascade
pg_restore -U writers_user -d writers_db --clean --if-exists backup.dump
```

### Backup خودکار

```bash
# اضافه به crontab
crontab -e

# Backup روزانه در ساعت 2 بامداد
0 2 * * * pg_dump -U writers_user -d writers_db | gzip > /backup/writers_$(date +\%Y\%m\%d).sql.gz

# حذف backup‌های قدیمی‌تر از 30 روز
0 3 * * * find /backup -name "writers_*.sql.gz" -mtime +30 -delete
```

## 📊 Monitoring

### Connection Pool

```python
from sqlalchemy import create_engine

engine = create_engine(
    DATABASE_URL,
    pool_size=20,          # تعداد connection‌های دائمی
    max_overflow=10,       # تعداد connection‌های اضافی
    pool_pre_ping=True,    # بررسی connection قبل از استفاده
    pool_recycle=3600,     # recycle هر ساعت
)
```

### Query‌های مانیتورینگ

```sql
-- بررسی active connections
SELECT * FROM pg_stat_activity 
WHERE datname = 'writers_db';

-- بررسی slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
WHERE mean_time > 1000
ORDER BY mean_time DESC
LIMIT 10;

-- بررسی table bloat
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
    n_dead_tup,
    n_live_tup
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC;
```

## 🔗 مراجع مرتبط

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

برای سوالات و مشکلات، به بخش [عیب‌یابی](TROUBLESHOOTING.md) مراجعه کنید.
