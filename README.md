# Writers - سیستم مدیریت وظایف با پردازش هوش مصنوعی

یک سیستم مدیریت وظایف پیشرفته با قابلیت پردازش و تحلیل محتوا از طریق هوش مصنوعی.

<div dir="rtl">

## 📋 فهرست مطالب

- [معرفی](#معرفی)
- [ویژگی‌های کلیدی](#ویژگی‌های-کلیدی)
- [معماری سیستم](#معماری-سیستم)
- [فناوری‌های استفاده شده](#فناوری‌های-استفاده-شده)
- [نصب و راه‌اندازی سریع](#نصب-و-راه‌اندازی-سریع)
- [ساختار پروژه](#ساختار-پروژه)
- [API Endpoints](#api-endpoints)
- [مانیتورینگ و لاگینگ](#مانیتورینگ-و-لاگینگ)
- [امنیت](#امنیت)
- [مقیاس‌پذیری](#مقیاس‌پذیری)
- [مستندات تکمیلی](#مستندات-تکمیلی)

---

## 🎯 معرفی

Writers یک پلتفرم کامل برای مدیریت وظایف است که با استفاده از معماری مدرن میکروسرویس‌ها طراحی شده است. این سیستم قابلیت پردازش فایل‌ها، تحلیل محتوا و مدیریت کاربران را با رابط کاربری مدرن و API RESTful فراهم می‌کند.

### مشخصات کلیدی

- ✅ معماری Microservices با جداسازی کامل Frontend و Backend
- ✅ احراز هویت امن با JWT و Cookie-based sessions
- ✅ پردازش ناهمزمان وظایف با Celery
- ✅ API Proxy در Next.js برای مدیریت بهتر کوکی‌ها و هدرها
- ✅ مانیتورینگ کامل با Prometheus و Grafana
- ✅ لاگینگ متمرکز با Loki و Promtail
- ✅ پیکربندی Nginx با SSL/TLS
- ✅ هشدارهای خودکار برای منابع سیستم (RAM، GPU، Disk)
- ✅ آماده برای محیط Production

---

## 🚀 ویژگی‌های کلیدی

### مدیریت کاربران
- ثبت‌نام و ورود امن
- احراز هویت مبتنی بر JWT
- مدیریت Session با Refresh Token
- نقش‌ها و دسترسی‌ها

### مدیریت وظایف
- ایجاد، ویرایش و حذف وظایف
- آپلود و مدیریت فایل‌ها
- پردازش ناهمزمان با Celery
- ردیابی وضعیت پردازش
- ویرایشگر متن پیشرفته با TipTap

### زیرساخت و عملیات
- Load Balancing با Nginx
- SSL/TLS با Let's Encrypt
- Health Check endpoints
- Rate Limiting
- CORS Configuration

### مانیتورینگ و لاگینگ
- جمع‌آوری متریک‌ها با Prometheus
- داشبوردهای Grafana
- لاگ‌های متمرکز با Loki
- هشدارهای خودکار با Alertmanager
- مانیتورینگ GPU و منابع سیستم

---

## 🏗️ معماری سیستم

```
┌─────────────────────────────────────────────────────────┐
│                        Client                           │
│                    (Browser/Mobile)                     │
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
    │ Postgres│ │ Redis │ │ Celery │ │ Storage│
    │   DB    │ │ Cache │ │ Worker │ │ Files  │
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

---

## 🛠️ فناوری‌های استفاده شده

### Backend
- **FastAPI** - فریمورک وب پرسرعت Python
- **SQLAlchemy** - ORM برای مدیریت دیتابیس
- **Alembic** - مدیریت Migration
- **Pydantic** - اعتبارسنجی داده‌ها
- **Python-JOSE** - JWT Token Management
- **Passlib** - Hash کردن رمزهای عبور
- **Celery** - پردازش ناهمزمان

### Frontend
- **Next.js 14** - React Framework با SSR/SSG
- **TypeScript** - Type Safety
- **TailwindCSS** - Styling
- **TipTap** - Rich Text Editor
- **Axios** - HTTP Client
- **SWR** - Data Fetching

### Database & Cache
- **PostgreSQL** - پایگاه داده اصلی
- **Redis** - Cache و Message Broker

### Infrastructure
- **Nginx** - Reverse Proxy و Load Balancer
- **Docker** - Containerization
- **Docker Compose** - Orchestration

### Monitoring & Logging
- **Prometheus** - Metrics Collection
- **Grafana** - Visualization
- **Loki** - Log Aggregation
- **Promtail** - Log Collection
- **Alertmanager** - Alert Management
- **Node Exporter** - System Metrics
- **PostgreSQL Exporter** - Database Metrics
- **Redis Exporter** - Cache Metrics
- **Nginx Exporter** - Web Server Metrics

---

## ⚡ نصب و راه‌اندازی سریع

### پیش‌نیازها

```bash
# Ubuntu/Debian
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+
- Nginx
```

### راه‌اندازی Development

#### 1. کلون کردن پروژه

```bash
git clone https://github.com/yourusername/writers.git
cd writers
```

#### 2. راه‌اندازی Backend

```bash
cd backend

# ایجاد محیط مجازی
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# یا
venv\Scripts\activate  # Windows

# نصب وابستگی‌ها
pip install -r requirements.txt

# تنظیم متغیرهای محیطی
cp ../.env.example .env
# ویرایش .env و تنظیم مقادیر

# اجرای migrations
alembic upgrade head

# راه‌اندازی سرور
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. راه‌اندازی Frontend

```bash
cd frontend

# نصب وابستگی‌ها
npm install

# راه‌اندازی سرور
npm run dev
```

#### 4. راه‌اندازی Worker

```bash
cd worker

# ایجاد محیط مجازی
python3 -m venv venv
source venv/bin/activate

# نصب وابستگی‌ها
pip install -r requirements.txt

# راه‌اندازی Celery worker
celery -A tasks worker --loglevel=info
```

#### 5. دسترسی به برنامه

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### راه‌اندازی Production

برای راه‌اندازی کامل در محیط Production، به [راهنمای راه‌اندازی](SETUP_GUIDE.md) مراجعه کنید.

#### نصب سریع با Docker

```bash
cd infrastructure

# راه‌اندازی تمام سرویس‌ها
docker-compose up -d

# راه‌اندازی monitoring
docker-compose -f docker-compose.monitoring.yml up -d
```

---

## 📁 ساختار پروژه

```
writers/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── auth/              # ماژول احراز هویت
│   │   ├── models/            # مدل‌های دیتابیس
│   │   ├── routers/           # API Endpoints
│   │   ├── db.py              # تنظیمات دیتابیس
│   │   └── main.py            # نقطه ورود
│   ├── alembic/               # Database Migrations
│   ├── tests/                 # تست‌ها
│   └── requirements.txt
│
├── frontend/                   # Next.js Frontend
│   ├── app/
│   │   ├── api/              # Next.js API Proxy Routes
│   │   │   ├── auth/         # Proxy برای احراز هویت
│   │   │   └── tasks/        # Proxy برای وظایف
│   │   ├── dashboard/        # صفحات Dashboard
│   │   ├── login/            # صفحه ورود
│   │   └── register/         # صفحه ثبت‌نام
│   ├── components/           # کامپوننت‌های React
│   ├── lib/                  # کتابخانه‌های کمکی
│   ├── __tests__/            # تست‌های یکپارچگی
│   └── package.json
│
├── worker/                     # Celery Worker
│   ├── tasks.py              # تعریف Task‌ها
│   └── requirements.txt
│
├── infrastructure/            # زیرساخت و DevOps
│   ├── nginx/
│   │   ├── nginx.conf        # پیکربندی Production با SSL
│   │   └── nginx-local.conf  # پیکربندی Local
│   ├── monitoring/
│   │   ├── prometheus/       # تنظیمات Prometheus
│   │   │   ├── prometheus.yml
│   │   │   └── alerts/       # قوانین هشدار
│   │   ├── grafana/          # داشبوردها و datasources
│   │   └── alertmanager/     # تنظیمات Alertmanager
│   ├── logging/
│   │   ├── loki/             # تنظیمات Loki
│   │   └── promtail/         # تنظیمات Promtail
│   ├── scripts/
│   │   ├── setup-ssl.sh      # نصب SSL با Certbot
│   │   ├── deploy-nginx.sh   # استقرار امن Nginx
│   │   ├── health-check.sh   # بررسی سلامت سرویس‌ها
│   │   └── setup-monitoring.sh
│   ├── docker-compose.yml
│   └── docker-compose.monitoring.yml
│
├── .env.example               # نمونه فایل محیطی
├── README.md                  # این فایل
└── SETUP_GUIDE.md            # راهنمای کامل راه‌اندازی
```

---

## 🔌 API Endpoints

### Authentication

```
POST   /api/auth/register      # ثبت‌نام کاربر جدید
POST   /api/auth/login         # ورود به سیستم
POST   /api/auth/logout        # خروج از سیستم
GET    /api/auth/me            # اطلاعات کاربر فعلی
POST   /api/auth/refresh       # تمدید توکن
```

### Tasks

```
GET    /api/tasks              # لیست وظایف
POST   /api/tasks              # ایجاد وظیفه جدید
GET    /api/tasks/{id}         # جزئیات وظیفه
PUT    /api/tasks/{id}         # به‌روزرسانی وظیفه
DELETE /api/tasks/{id}         # حذف وظیفه
```

### Health & Metrics

```
GET    /health                 # بررسی سلامت سرویس
GET    /metrics                # متریک‌های Prometheus
```

### مستندات کامل API

مستندات تعاملی Swagger در دسترس است:
- Production: https://yourdomain.com/docs
- Development: http://localhost:8000/docs

---

## 📊 مانیتورینگ و لاگینگ

### Prometheus Metrics

سیستم به‌صورت خودکار متریک‌های زیر را جمع‌آوری می‌کند:

- **System Metrics**: CPU, RAM, Disk, Network
- **Application Metrics**: Request count, Response time, Error rate
- **Database Metrics**: Connection pool, Query performance
- **Cache Metrics**: Hit rate, Memory usage
- **GPU Metrics**: Temperature, Memory, Utilization

### Grafana Dashboards

Dashboard‌های آماده:
- **System Overview**: نمای کلی منابع سیستم
- **Application Performance**: عملکرد API و Backend
- **Database Performance**: وضعیت PostgreSQL
- **Error Tracking**: ردیابی خطاها و استثناها

دسترسی: http://localhost:3001 (admin/admin)

### Log Aggregation

تمام لاگ‌ها در Loki جمع‌آوری می‌شوند:
- FastAPI application logs
- Nginx access/error logs
- Celery worker logs
- PostgreSQL logs
- System logs

دسترسی: از طریق Grafana > Explore > Loki

### Alert Rules

هشدارهای تعریف شده:

#### منابع سیستم
- ✅ RAM > 85% (Warning)
- ⚠️ RAM > 95% (Critical)
- ✅ Disk > 80% (Warning)
- ⚠️ Disk > 90% (Critical)
- ✅ GPU Temp > 80°C (Warning)
- ⚠️ GPU Temp > 90°C (Critical)

#### سرویس‌ها
- ⚠️ Service Down (Critical)
- ✅ High Error Rate > 5% (Warning)
- ✅ High Response Time > 2s (Warning)
- ✅ Database Connection Pool > 80% (Warning)

---

## 🔒 امنیت

### احراز هویت
- JWT-based authentication
- HttpOnly cookies برای جلوگیری از XSS
- Refresh token rotation
- Secure password hashing با Bcrypt

### HTTPS/SSL
- TLS 1.2/1.3
- Automatic certificate renewal با Let's Encrypt
- HSTS headers
- Secure cipher suites

### API Security
- Rate limiting (10 req/s for API, 5 req/s for auth)
- CORS configuration
- Input validation با Pydantic
- SQL injection protection با SQLAlchemy ORM

### Headers امنیتی
```
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000
```

---

## 📈 مقیاس‌پذیری

### توصیه‌های سخت‌افزاری

| کاربران همزمان | RAM    | CPU Cores | Storage |
|-----------------|--------|-----------|---------|
| < 100           | 16 GB  | 4         | 50 GB   |
| 100-500         | 32 GB  | 8         | 100 GB  |
| 500-1000        | 64 GB  | 16        | 200 GB  |
| 1000+           | 128 GB | 32+       | 500 GB+ |

### افزایش ظرفیت

#### Backend Workers
```bash
# در /etc/systemd/system/writers-backend.service
ExecStart=.../uvicorn app.main:app --workers 8
```

#### Celery Workers
```bash
# در /etc/systemd/system/writers-worker.service
ExecStart=.../celery -A tasks worker --concurrency=8
```

#### Horizontal Scaling

برای مقیاس‌پذیری افقی:

1. **Load Balancer**: استفاده از Nginx upstream
```nginx
upstream backend_servers {
    least_conn;
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}
```

2. **Database Replication**: تنظیم Master-Slave PostgreSQL
3. **Redis Cluster**: برای cache توزیع شده
4. **Shared Storage**: برای فایل‌های آپلود شده

---

## 🧪 تست

### Backend Tests

```bash
cd backend
pytest

# با coverage
pytest --cov=app --cov-report=html
```

### Frontend Tests

```bash
cd frontend
npm test

# با coverage
npm run test:coverage
```

### Integration Tests

```bash
# تست API proxy routes
cd frontend
npm test -- __tests__/api/proxy.test.ts
```

---

## 🚢 استقرار (Deployment)

### با Docker

```bash
# Build images
docker-compose build

# راه‌اندازی سرویس‌ها
docker-compose up -d

# مشاهده لاگ‌ها
docker-compose logs -f
```

### با Systemd

جزئیات کامل در [راهنمای راه‌اندازی](SETUP_GUIDE.md)

### CI/CD

پروژه آماده برای integration با:
- GitHub Actions
- GitLab CI
- Jenkins
- CircleCI

---

## 📚 مستندات تکمیلی

- **[راهنمای راه‌اندازی کامل](SETUP_GUIDE.md)** - مراحل دقیق نصب و پیکربندی
- **[API Documentation](http://localhost:8000/docs)** - مستندات تعاملی Swagger
- **Infrastructure Docs**:
  - [QUICK_START.md](infrastructure/QUICK_START.md)
  - [DEPLOYMENT.md](infrastructure/DEPLOYMENT.md)
  - [SYSTEMD_SERVICES.md](infrastructure/SYSTEMD_SERVICES.md)

---

## 🤝 مشارکت

برای مشارکت در پروژه:

1. Fork کردن پروژه
2. ایجاد branch برای feature جدید (`git checkout -b feature/AmazingFeature`)
3. Commit کردن تغییرات (`git commit -m 'Add some AmazingFeature'`)
4. Push به branch (`git push origin feature/AmazingFeature`)
5. ایجاد Pull Request

### استانداردهای کد

- **Python**: PEP 8
- **JavaScript/TypeScript**: ESLint + Prettier
- **Git Commits**: Conventional Commits

---

## 📝 لایسنس

این پروژه تحت لایسنس MIT منتشر شده است. برای جزئیات بیشتر فایل [LICENSE](LICENSE) را مطالعه کنید.

---

## 👥 تیم توسعه

- **Backend Development**: FastAPI + SQLAlchemy
- **Frontend Development**: Next.js + TypeScript
- **DevOps**: Docker + Nginx + Monitoring
- **UI/UX**: Modern React Components

---

## 📞 پشتیبانی

برای گزارش باگ یا درخواست feature:
- **GitHub Issues**: [Create an issue](https://github.com/yourusername/writers/issues)
- **Email**: support@yourdomain.com
- **Documentation**: [Full Documentation](https://writers-docs.yourdomain.com)

---

## 🎉 تشکر

از تمام کسانی که در توسعه این پروژه مشارکت داشته‌اند، تشکر می‌کنیم.

---

## 📊 وضعیت پروژه

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-85%25-green)
![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![Node](https://img.shields.io/badge/node-18+-green)

---

**ساخته شده با ❤️ در ایران**

</div>
