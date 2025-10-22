# راهنمای نصب سیستم Writers

این سند مراحل کامل نصب و پیکربندی سیستم Writers را شرح می‌دهد.

## 📋 قبل از شروع

اطمینان حاصل کنید که تمام [پیش‌نیازها](REQUIREMENTS.md) را نصب کرده‌اید.

## 🚀 روش‌های نصب

سیستم Writers را می‌توانید به دو روش نصب کنید:

1. **نصب Manual**: برای محیط Development و کنترل بیشتر
2. **نصب با Docker**: برای راه‌اندازی سریع و محیط Production

## 📦 نصب Manual

### مرحله 1: دریافت کد

```bash
# کلون کردن repository
git clone https://github.com/yourusername/writers.git
cd writers
```

### مرحله 2: پیکربندی پایگاه داده PostgreSQL

```bash
# ورود به PostgreSQL
sudo -u postgres psql

# اجرای دستورات زیر:
```

```sql
-- ایجاد کاربر
CREATE USER writers_user WITH PASSWORD 'your_strong_password_here';

-- ایجاد دیتابیس
CREATE DATABASE writers_db OWNER writers_user;

-- اعطای دسترسی‌ها
GRANT ALL PRIVILEGES ON DATABASE writers_db TO writers_user;

-- خروج
\q
```

یا استفاده از اسکریپت آماده:

```bash
cd infrastructure
sudo bash setup_postgresql.sh
```

### مرحله 3: پیکربندی Redis

```bash
# ویرایش فایل پیکربندی Redis
sudo nano /etc/redis/redis.conf

# اضافه کردن یا ویرایش موارد زیر:
requirepass your_redis_password_here
maxmemory 512mb
maxmemory-policy allkeys-lru
```

یا استفاده از اسکریپت:

```bash
sudo bash setup_redis.sh
```

راه‌اندازی مجدد Redis:

```bash
sudo systemctl restart redis-server
sudo systemctl enable redis-server
```

### مرحله 4: ایجاد فایل Environment Variables

```bash
# کپی فایل نمونه
cp .env.example .env

# ویرایش فایل
nano .env
```

محتوای فایل `.env`:

```env
# =============================================================================
# تنظیمات پایگاه داده
# =============================================================================
POSTGRES_DB=writers_db
POSTGRES_USER=writers_user
POSTGRES_PASSWORD=your_strong_password_here
DATABASE_URL=postgresql://writers_user:your_strong_password_here@localhost:5432/writers_db

# =============================================================================
# تنظیمات Redis
# =============================================================================
REDIS_PASSWORD=your_redis_password_here
REDIS_URL=redis://:your_redis_password_here@localhost:6379/0
REDIS_CACHE_DB=0
REDIS_QUEUE_DB=2

# =============================================================================
# تنظیمات JWT و امنیت
# =============================================================================
# SECRET_KEY را با دستور زیر بسازید:
# openssl rand -hex 32
SECRET_KEY=your_generated_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# =============================================================================
# تنظیمات Backend
# =============================================================================
BACKEND_PORT=8000
BACKEND_HOST=0.0.0.0
BACKEND_WORKERS=4

# =============================================================================
# تنظیمات Frontend
# =============================================================================
FRONTEND_PORT=3000
NEXT_PUBLIC_API_URL=http://localhost:8000
APP_URL=http://localhost:3000

# =============================================================================
# تنظیمات Worker
# =============================================================================
WORKER_CONCURRENCY=4
WORKER_MAX_RETRIES=3

# =============================================================================
# تنظیمات Storage
# =============================================================================
STORAGE_ROOT=/var/lib/writers/storage
UPLOAD_MAX_SIZE=10485760  # 10MB

# =============================================================================
# محیط اجرا
# =============================================================================
NODE_ENV=development

# =============================================================================
# تنظیمات Domain (برای Production)
# =============================================================================
# DOMAIN=yourdomain.com
# ADMIN_EMAIL=admin@yourdomain.com
```

تولید SECRET_KEY:

```bash
openssl rand -hex 32
```

### مرحله 5: نصب Backend

```bash
cd backend

# ایجاد Virtual Environment
python3 -m venv venv

# فعال‌سازی Virtual Environment
source venv/bin/activate  # Linux/Mac
# یا
venv\Scripts\activate     # Windows

# ارتقای pip
pip install --upgrade pip

# نصب وابستگی‌ها
pip install -r requirements.txt

# اجرای Migrations
alembic upgrade head

# بررسی نصب
python -c "import fastapi; print('FastAPI:', fastapi.__version__)"
```

### مرحله 6: نصب Frontend

```bash
cd ../frontend

# نصب وابستگی‌ها
npm install

# یا با yarn
yarn install

# بررسی نصب
npm list next
```

### مرحله 7: نصب Worker

```bash
cd ../worker

# ایجاد Virtual Environment
python3 -m venv venv

# فعال‌سازی Virtual Environment
source venv/bin/activate

# نصب وابستگی‌ها
pip install -r requirements.txt

# بررسی نصب
celery --version
```

### مرحله 8: ایجاد دایرکتوری Storage

```bash
# ایجاد دایرکتوری
sudo mkdir -p /var/lib/writers/storage
sudo mkdir -p /var/lib/writers/uploads

# تنظیم مالکیت
sudo chown -R $USER:$USER /var/lib/writers

# تنظیم دسترسی‌ها
chmod -R 755 /var/lib/writers
```

### مرحله 9: اجرای اولیه (Development)

در سه ترمینال جداگانه:

**ترمینال 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**ترمینال 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**ترمینال 3 - Worker:**
```bash
cd worker
source venv/bin/activate
celery -A tasks worker --loglevel=info
```

### مرحله 10: بررسی نصب

دسترسی به آدرس‌های زیر:

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## 🐳 نصب با Docker

### مرحله 1: دریافت کد

```bash
git clone https://github.com/yourusername/writers.git
cd writers
```

### مرحله 2: تنظیم Environment Variables

```bash
cp .env.example .env
nano .env
```

مقادیر ضروری را تنظیم کنید (مشابه بخش قبل).

### مرحله 3: ساخت Docker Images

```bash
cd infrastructure

# ساخت تمام images
docker-compose build

# یا ساخت جداگانه
docker-compose build backend
docker-compose build frontend
docker-compose build worker
```

### مرحله 4: راه‌اندازی سرویس‌ها

```bash
# ایجاد network
docker network create app-network

# راه‌اندازی تمام سرویس‌ها
docker-compose up -d

# یا راه‌اندازی گام به گام
docker-compose up -d postgres redis
sleep 10  # انتظار برای آماده شدن
docker-compose up -d backend
docker-compose up -d worker
docker-compose up -d frontend
```

### مرحله 5: اجرای Migrations

```bash
# اجرای migrations در container
docker-compose exec backend alembic upgrade head
```

### مرحله 6: بررسی وضعیت

```bash
# بررسی وضعیت سرویس‌ها
docker-compose ps

# بررسی logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f worker
```

### مرحله 7: دسترسی به سیستم

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📊 نصب Monitoring Stack

### با Docker (توصیه شده)

```bash
cd infrastructure

# راه‌اندازی monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d

# یا استفاده از اسکریپت
sudo bash scripts/setup-monitoring.sh
```

### دسترسی به داشبوردها

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (username: admin, password: admin)
- Alertmanager: http://localhost:9093

### پیکربندی اولیه Grafana

1. به Grafana وارد شوید: http://localhost:3001
2. رمز عبور پیش‌فرض (admin/admin) را تغییر دهید
3. Datasource‌ها به صورت خودکار تنظیم شده‌اند
4. Dashboardها در بخش Dashboards موجود هستند

## 🔧 پیکربندی Nginx (برای Production)

### نصب Nginx

```bash
sudo apt update
sudo apt install -y nginx
```

### کپی فایل پیکربندی

برای محیط local (بدون SSL):
```bash
sudo cp infrastructure/nginx/nginx-local.conf /etc/nginx/sites-available/writers
```

برای Production (با SSL):
```bash
sudo cp infrastructure/nginx/nginx.conf /etc/nginx/sites-available/writers

# ویرایش فایل و تنظیم domain
sudo nano /etc/nginx/sites-available/writers
```

### فعال‌سازی سایت

```bash
# حذف پیکربندی پیش‌فرض
sudo rm /etc/nginx/sites-enabled/default

# فعال‌سازی سایت Writers
sudo ln -s /etc/nginx/sites-available/writers /etc/nginx/sites-enabled/

# تست پیکربندی
sudo nginx -t

# راه‌اندازی مجدد
sudo systemctl restart nginx
```

## 🔐 تنظیم SSL/TLS (برای Production)

### استفاده از Let's Encrypt

```bash
cd infrastructure/scripts

# اجرای اسکریپت setup SSL
sudo bash setup-ssl.sh yourdomain.com admin@yourdomain.com
```

این اسکریپت:
- Certbot را نصب می‌کند
- گواهی SSL دریافت می‌کند
- Nginx را پیکربندی می‌کند
- تمدید خودکار را راه‌اندازی می‌کند

### تنظیم دستی SSL

```bash
# نصب Certbot
sudo apt install -y certbot python3-certbot-nginx

# دریافت گواهی
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# تست تمدید خودکار
sudo certbot renew --dry-run
```

## 🔄 تنظیم Systemd Services (برای Production)

### Backend Service

```bash
sudo nano /etc/systemd/system/writers-backend.service
```

محتوا:
```ini
[Unit]
Description=Writers FastAPI Backend
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/writers/backend
Environment="PATH=/var/www/writers/backend/venv/bin"
Environment="DATABASE_URL=postgresql://writers_user:password@localhost:5432/writers_db"
Environment="REDIS_URL=redis://:password@localhost:6379/0"
ExecStart=/var/www/writers/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Frontend Service

```bash
sudo nano /etc/systemd/system/writers-frontend.service
```

محتوا:
```ini
[Unit]
Description=Writers Next.js Frontend
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/writers/frontend
Environment="PATH=/usr/bin:/usr/local/bin"
Environment="NODE_ENV=production"
Environment="PORT=3000"
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Worker Service

```bash
sudo nano /etc/systemd/system/writers-worker.service
```

محتوا:
```ini
[Unit]
Description=Writers Celery Worker
After=network.target redis.service postgresql.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/writers/worker
Environment="PATH=/var/www/writers/worker/venv/bin"
Environment="DATABASE_URL=postgresql://writers_user:password@localhost:5432/writers_db"
Environment="REDIS_URL=redis://:password@localhost:6379/2"
ExecStart=/var/www/writers/worker/venv/bin/celery -A tasks worker --loglevel=info --concurrency=4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### فعال‌سازی و اجرای Services

```bash
# بارگذاری مجدد Systemd
sudo systemctl daemon-reload

# فعال‌سازی سرویس‌ها (برای اجرای خودکار در بوت)
sudo systemctl enable writers-backend
sudo systemctl enable writers-frontend
sudo systemctl enable writers-worker

# شروع سرویس‌ها
sudo systemctl start writers-backend
sudo systemctl start writers-frontend
sudo systemctl start writers-worker

# بررسی وضعیت
sudo systemctl status writers-backend
sudo systemctl status writers-frontend
sudo systemctl status writers-worker
```

## ✅ بررسی نهایی نصب

اسکریپت زیر را اجرا کنید:

```bash
cd infrastructure/scripts
sudo bash health-check.sh
```

یا بررسی دستی:

```bash
# بررسی Backend
curl http://localhost:8000/health

# بررسی Frontend
curl http://localhost:3000

# بررسی Database
psql -U writers_user -d writers_db -c "SELECT version();"

# بررسی Redis
redis-cli -a your_password ping

# بررسی Nginx
curl http://localhost
```

## 🎯 مراحل بعد از نصب

1. **ایجاد کاربر Admin اولیه:**
```bash
cd backend
source venv/bin/activate
python -c "from app.auth.utils import create_user; create_user('admin@example.com', 'secure_password')"
```

2. **تنظیم Backup خودکار:**
```bash
# اضافه کردن به crontab
crontab -e

# پشتیبان‌گیری روزانه در ساعت 2 بامداد
0 2 * * * pg_dump -U writers_user writers_db | gzip > /backup/db_$(date +\%Y\%m\%d).sql.gz
```

3. **تنظیم Firewall:**
```bash
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

4. **تست کامل سیستم:**
- ثبت‌نام کاربر جدید
- ایجاد تسک
- آپلود فایل
- بررسی پردازش Worker
- بررسی Monitoring

## 🐛 عیب‌یابی مشکلات نصب

### مشکل: Backend اجرا نمی‌شود

```bash
# بررسی logs
cd backend
source venv/bin/activate
python -c "from app.db import engine; print(engine)"

# بررسی اتصال Database
psql -U writers_user -d writers_db -c "SELECT 1;"
```

### مشکل: Frontend build نمی‌شود

```bash
# پاک کردن cache و node_modules
cd frontend
rm -rf node_modules .next
npm cache clean --force
npm install
npm run build
```

### مشکل: Worker شروع نمی‌شود

```bash
# بررسی اتصال Redis
redis-cli -a your_password ping

# اجرای Worker با log بیشتر
cd worker
source venv/bin/activate
celery -A tasks worker --loglevel=debug
```

### مشکل: Nginx خطای 502 می‌دهد

```bash
# بررسی Backend
curl http://localhost:8000/health

# بررسی logs Nginx
sudo tail -f /var/log/nginx/error.log

# بررسی پیکربندی
sudo nginx -t
```

## 📚 مراحل بعدی

پس از نصب موفق:

1. [راهنمای اجرا](RUNNING.md) - نحوه اجرا و مدیریت سیستم
2. [راهنمای استقرار](DEPLOYMENT.md) - استقرار در Production
3. [راهنمای توسعه](DEVELOPMENT.md) - شروع توسعه

---

برای مشکلات و سوالات، به بخش [عیب‌یابی](TROUBLESHOOTING.md) مراجعه کنید.
