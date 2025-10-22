# معماری سیستم Writers

این سند معماری کلی سیستم Writers، اجزای مختلف و نحوه ارتباط آنها با یکدیگر را توضیح می‌دهد.

## 📐 نمای کلی معماری

سیستم Writers با استفاده از معماری میکروسرویس طراحی شده است که امکان مقیاس‌پذیری، نگهداری آسان و جداسازی مسئولیت‌ها را فراهم می‌کند.

## 🏗️ دیاگرام معماری

```
┌─────────────────────────────────────────────────────────┐
│                        کاربر                            │
│                  (مرورگر / موبایل)                      │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTPS (443)
                        ▼
┌─────────────────────────────────────────────────────────┐
│                       Nginx                             │
│          (Reverse Proxy + Load Balancer)                │
│   - SSL/TLS Termination                                 │
│   - Rate Limiting                                       │
│   - Static File Serving                                 │
└────────┬───────────────────────┬────────────────────────┘
         │                       │
         │ /api/*               │ /*
         ▼                       ▼
┌─────────────────┐    ┌──────────────────┐
│   FastAPI       │    │    Next.js       │
│   Backend       │◄───│    Frontend      │
│   (Port 8000)   │    │   (Port 3000)    │
│                 │    │                  │
│ - Auth API      │    │ - API Proxy      │
│ - Tasks API     │    │ - SSR/CSR        │
│ - Metrics       │    │ - UI Components  │
└────────┬────────┘    └──────────────────┘
         │
         ├──────────┬──────────┬──────────┐
         ▼          ▼          ▼          ▼
    ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
    │Postgres│ │ Redis  │ │ Celery │ │Storage │
    │   DB   │ │ Cache  │ │ Worker │ │ Files  │
    └────────┘ └────────┘ └────────┘ └────────┘
         │          │          │
         └──────────┴──────────┘
                    │
                    ▼
         ┌────────────────────┐
         │    Monitoring      │
         │  - Prometheus      │
         │  - Grafana         │
         │  - Loki            │
         │  - Alertmanager    │
         └────────────────────┘
```

## 🧩 اجزای سیستم

### 1. Frontend (Next.js)

**مسئولیت‌ها:**
- رابط کاربری (UI/UX)
- Server-Side Rendering (SSR)
- Client-Side Rendering (CSR)
- API Proxy Routes
- مدیریت Authentication از سمت Client

**تکنولوژی‌ها:**
- Next.js 14 (App Router)
- TypeScript
- TailwindCSS
- TipTap Editor
- SWR for Data Fetching

**ساختار دایرکتوری:**
```
frontend/
├── app/
│   ├── api/              # Next.js API Proxy Routes
│   │   ├── auth/        # Proxy برای احراز هویت
│   │   └── tasks/       # Proxy برای وظایف
│   ├── dashboard/       # صفحات داشبورد
│   ├── login/          # صفحه ورود
│   └── register/       # صفحه ثبت‌نام
├── contexts/           # React Contexts
├── hooks/              # Custom Hooks
├── lib/                # کتابخانه‌های کمکی
└── types/              # TypeScript Types
```

**ویژگی‌های کلیدی:**
- API Proxy: تمام درخواست‌های API از طریق Next.js Route Handlers ارسال می‌شوند
- Cookie Management: مدیریت امن HttpOnly Cookies
- Type Safety: استفاده کامل از TypeScript

### 2. Backend (FastAPI)

**مسئولیت‌ها:**
- ارائه RESTful API
- احراز هویت و مجوزدهی
- مدیریت پایگاه داده
- ارسال تسک‌ها به Worker
- Metrics Collection

**تکنولوژی‌ها:**
- FastAPI
- SQLAlchemy (ORM)
- Alembic (Migrations)
- Pydantic (Validation)
- Python-JOSE (JWT)
- Celery Client

**ساختار دایرکتوری:**
```
backend/
├── app/
│   ├── auth/           # ماژول احراز هویت
│   │   ├── dependencies.py
│   │   ├── jwt.py
│   │   ├── router.py
│   │   └── utils.py
│   ├── models/         # Database Models
│   │   ├── user.py
│   │   └── task.py
│   ├── routers/        # API Endpoints
│   │   ├── tasks.py
│   │   └── schemas.py
│   ├── db.py          # تنظیمات Database
│   ├── main.py        # نقطه ورود
│   └── celery_app.py  # تنظیمات Celery
├── alembic/           # Database Migrations
└── tests/             # تست‌ها
```

**ویژگی‌های کلیدی:**
- Async/Await Support
- Automatic API Documentation (Swagger)
- Pydantic Validation
- JWT Authentication
- CORS Middleware

### 3. Worker (Celery)

**مسئولیت‌ها:**
- پردازش ناهمگام فایل‌ها
- تحلیل محتوا
- تسک‌های زمان‌بر
- پردازش دسته‌ای

**تکنولوژی‌ها:**
- Celery
- Redis (Message Broker)
- Python Libraries

**ساختار:**
```
worker/
├── tasks.py          # تعریف تسک‌ها
├── requirements.txt  # وابستگی‌ها
└── entrypoint.sh     # اسکریپت اجرا
```

**ویژگی‌های کلیدی:**
- Asynchronous Task Processing
- Task Retry Mechanism
- Task Result Storage
- Concurrency Control

### 4. Database (PostgreSQL)

**مسئولیت‌ها:**
- ذخیره‌سازی داده‌های اصلی
- مدیریت Transaction
- Relations بین داده‌ها

**جداول اصلی:**
- `users`: اطلاعات کاربران
- `tasks`: اطلاعات وظایف
- `alembic_version`: نسخه Migration

**ویژگی‌های پیکربندی:**
- Connection Pooling
- Query Optimization
- Index Management
- Backup Strategy

### 5. Cache & Message Broker (Redis)

**مسئولیت‌ها:**
- کش کردن داده‌های پرتکرار
- Message Queue برای Celery
- Session Storage
- Rate Limiting

**استفاده‌ها:**
- Database 0: General Cache
- Database 1: Session Storage
- Database 2: Celery Queue

### 6. Reverse Proxy (Nginx)

**مسئولیت‌ها:**
- SSL/TLS Termination
- Load Balancing
- Rate Limiting
- Static File Serving
- Request Routing

**پیکربندی:**
```nginx
# Route API requests to Backend
location /api/ {
    proxy_pass http://backend:8000;
}

# Route other requests to Frontend
location / {
    proxy_pass http://frontend:3000;
}
```

### 7. Monitoring Stack

#### Prometheus
- جمع‌آوری متریک‌های سیستم
- متریک‌های Application
- متریک‌های Database
- متریک‌های Redis

#### Grafana
- Visualization متریک‌ها
- داشبوردهای آماده
- Alert Configuration
- Multi-Source Dashboards

#### Loki
- Log Aggregation
- جمع‌آوری لاگ‌های تمام سرویس‌ها
- Query Language قدرتمند

#### Promtail
- Log Collection Agent
- ارسال لاگ‌ها به Loki

#### Alertmanager
- مدیریت هشدارها
- ارسال Notification
- Alert Grouping

## 🔄 جریان داده (Data Flow)

### 1. جریان احراز هویت

```
User → Frontend → API Proxy → Backend → Database
                                    ↓
                              JWT Token
                                    ↓
                              HttpOnly Cookie
                                    ↓
                                Frontend
```

### 2. جریان ایجاد تسک

```
User → Frontend → API Proxy → Backend → Database
                                    ↓
                              Celery Task
                                    ↓
                                  Redis
                                    ↓
                              Celery Worker
                                    ↓
                              Process Task
                                    ↓
                              Update Database
```

### 3. جریان مانیتورینگ

```
Application → Metrics Endpoint → Prometheus
                                      ↓
                                  Storage
                                      ↓
                                   Grafana
                                      ↓
                                Visualization
```

## 🔐 امنیت

### لایه‌های امنیتی

1. **Network Layer**
   - Firewall Rules
   - DDoS Protection
   - SSL/TLS Encryption

2. **Application Layer**
   - JWT Authentication
   - CORS Configuration
   - Rate Limiting
   - Input Validation

3. **Data Layer**
   - Encrypted Connections
   - Secure Password Hashing
   - SQL Injection Prevention

4. **Infrastructure Layer**
   - Container Isolation
   - Secret Management
   - Access Control

## 📈 مقیاس‌پذیری

### Horizontal Scaling

**Frontend:**
- چند instance با Load Balancer
- CDN برای static files

**Backend:**
- چند instance با Nginx Load Balancer
- Session Storage در Redis

**Worker:**
- چند instance همزمان
- Auto-scaling بر اساس Queue Size

**Database:**
- Master-Slave Replication
- Read Replicas

### Vertical Scaling

- افزایش CPU و RAM
- افزایش Workers
- بهینه‌سازی Query‌ها

## 🔌 نقاط اتصال (Integration Points)

### External Services (قابل اضافه کردن)
- Email Service (SMTP)
- SMS Gateway
- Cloud Storage (S3)
- Payment Gateway
- Third-party APIs

### Webhooks
- Task Completion Notifications
- User Activity Events
- System Alerts

## 📊 متریک‌های کلیدی

### Performance Metrics
- Response Time
- Throughput (requests/sec)
- Error Rate
- Database Query Time

### Resource Metrics
- CPU Usage
- Memory Usage
- Disk I/O
- Network Traffic

### Business Metrics
- Active Users
- Tasks Created/Completed
- Upload Size
- Processing Time

## 🏛️ معماری Deployment

### Development Environment
```
Developer Machine
├── Frontend (localhost:3000)
├── Backend (localhost:8000)
├── PostgreSQL (localhost:5432)
├── Redis (localhost:6379)
└── Worker (local process)
```

### Production Environment
```
Production Server(s)
├── Docker Network
│   ├── Frontend Container
│   ├── Backend Container
│   ├── Worker Container(s)
│   ├── PostgreSQL Container
│   └── Redis Container
├── Nginx (Host)
└── Monitoring Stack (Separate Docker Network)
```

## 🔄 CI/CD Pipeline (پیشنهادی)

```
Code Push → GitHub
    ↓
Run Tests → GitHub Actions
    ↓
Build Docker Images
    ↓
Push to Registry
    ↓
Deploy to Server
    ↓
Health Check
    ↓
Rollback if Failed
```

## 📝 نکات طراحی

### Design Principles
- **Separation of Concerns**: هر سرویس مسئولیت خاص خود را دارد
- **Loose Coupling**: وابستگی کم بین سرویس‌ها
- **High Cohesion**: عملکرد مرتبط در یک سرویس
- **Scalability**: قابلیت افزایش ظرفیت
- **Reliability**: مقاومت در برابر خطا
- **Security First**: امنیت در تمام لایه‌ها

### Best Practices
- استفاده از Environment Variables
- Logging منظم و ساختارمند
- Error Handling مناسب
- Documentation کامل
- Testing جامع
- Monitoring فعال

---

برای اطلاعات بیشتر درباره هر بخش، به مستندات مربوطه مراجعه کنید.
