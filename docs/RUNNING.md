# راهنمای اجرای سیستم Writers

این سند نحوه اجرا، مدیریت و کنترل سیستم Writers در محیط‌های مختلف را توضیح می‌دهد.

## 🚀 محیط Development

### اجرای Manual (پیشنهاد شده برای Development)

برای اجرای سیستم در محیط Development، سه ترمینال جداگانه نیاز دارید.

#### ترمینال 1: Backend (FastAPI)

```bash
# رفتن به دایرکتوری backend
cd backend

# فعال‌سازی virtual environment
source venv/bin/activate  # Linux/Mac
# یا
venv\Scripts\activate     # Windows

# اجرای backend با hot-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# با تنظیمات سفارشی
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug
```

خروجی مورد انتظار:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

#### ترمینال 2: Frontend (Next.js)

```bash
# رفتن به دایرکتوری frontend
cd frontend

# اجرای development server
npm run dev

# یا با port سفارشی
PORT=3001 npm run dev

# یا با yarn
yarn dev
```

خروجی مورد انتظار:
```
ready - started server on 0.0.0.0:3000, url: http://localhost:3000
event - compiled client and server successfully
```

#### ترمینال 3: Worker (Celery)

```bash
# رفتن به دایرکتوری worker
cd worker

# فعال‌سازی virtual environment
source venv/bin/activate

# اجرای Celery worker
celery -A tasks worker --loglevel=info

# با تنظیمات بیشتر
celery -A tasks worker --loglevel=info --concurrency=4 --pool=prefork

# با autoreload برای development
watchmedo auto-restart --directory=./ --pattern=*.py --recursive -- celery -A tasks worker --loglevel=info
```

خروجی مورد انتظار:
```
 -------------- celery@hostname v5.3.4
---- **** -----
--- * ***  * -- Linux-x.x.x
-- * - **** ---
- ** ----------
- ** ----------
- *** --- * ---
celery@hostname v5.3.4

[tasks]
  . tasks.process_file
```

### بررسی اجرای صحیح

پس از اجرای تمام سرویس‌ها:

```bash
# بررسی Backend
curl http://localhost:8000/health
# انتظار: {"status":"healthy"}

# بررسی Frontend
curl http://localhost:3000
# انتظار: HTML صفحه اصلی

# بررسی API Docs
# مرورگر: http://localhost:8000/docs

# بررسی Redis
redis-cli ping
# انتظار: PONG

# بررسی PostgreSQL
psql -U writers_user -d writers_db -c "SELECT 1;"
# انتظار: 1
```

## 🐳 محیط Development با Docker

### اجرای کل سیستم

```bash
cd infrastructure

# راه‌اندازی تمام سرویس‌ها
docker-compose up

# یا در پس‌زمینه
docker-compose up -d

# بررسی logs
docker-compose logs -f

# بررسی logs یک سرویس خاص
docker-compose logs -f backend
```

### مدیریت سرویس‌ها

```bash
# بررسی وضعیت
docker-compose ps

# توقف سرویس‌ها
docker-compose stop

# شروع مجدد
docker-compose start

# راه‌اندازی مجدد یک سرویس
docker-compose restart backend

# توقف و حذف containers
docker-compose down

# توقف و حذف volumes (خطرناک!)
docker-compose down -v
```

### اجرای دستورات در Container

```bash
# اجرای migration
docker-compose exec backend alembic upgrade head

# اجرای shell در backend
docker-compose exec backend /bin/bash

# اجرای Python shell
docker-compose exec backend python

# اجرای دستورات Database
docker-compose exec postgres psql -U writers_user -d writers_db

# بررسی Redis
docker-compose exec redis redis-cli
```

## 🏭 محیط Production

### اجرا با Systemd (توصیه شده)

#### شروع تمام سرویس‌ها

```bash
# شروع Backend
sudo systemctl start writers-backend

# شروع Frontend
sudo systemctl start writers-frontend

# شروع Worker
sudo systemctl start writers-worker

# یا همه با هم
sudo systemctl start writers-backend writers-frontend writers-worker
```

#### بررسی وضعیت

```bash
# بررسی وضعیت Backend
sudo systemctl status writers-backend

# بررسی وضعیت Frontend
sudo systemctl status writers-frontend

# بررسی وضعیت Worker
sudo systemctl status writers-worker

# بررسی همه
for service in writers-backend writers-frontend writers-worker; do
    echo "=== $service ==="
    sudo systemctl status $service --no-pager
    echo ""
done
```

#### مدیریت سرویس‌ها

```bash
# توقف سرویس
sudo systemctl stop writers-backend

# راه‌اندازی مجدد
sudo systemctl restart writers-backend

# reload (بدون downtime)
sudo systemctl reload writers-backend

# غیرفعال کردن (اجرا نشود در بوت)
sudo systemctl disable writers-backend

# فعال کردن (اجرا شود در بوت)
sudo systemctl enable writers-backend
```

#### مشاهده Logs

```bash
# مشاهده logs Backend
sudo journalctl -u writers-backend -f

# مشاهده logs با محدودیت زمانی
sudo journalctl -u writers-backend --since "1 hour ago"

# مشاهده 100 خط آخر
sudo journalctl -u writers-backend -n 100

# مشاهده logs تمام سرویس‌ها
sudo journalctl -u writers-backend -u writers-frontend -u writers-worker -f
```

### اجرا با Docker Compose (Production)

```bash
cd infrastructure

# راه‌اندازی با profile production
docker-compose --env-file ../.env up -d

# بررسی سلامت
docker-compose ps

# مشاهده logs
docker-compose logs -f --tail=100

# راه‌اندازی مجدد
docker-compose restart

# به‌روزرسانی images
docker-compose pull
docker-compose up -d
```

### اجرا با PM2 (Alternative برای Frontend)

```bash
cd frontend

# نصب PM2
npm install -g pm2

# اجرا
pm2 start npm --name "writers-frontend" -- start

# مشاهده لیست
pm2 list

# مشاهده logs
pm2 logs writers-frontend

# راه‌اندازی مجدد
pm2 restart writers-frontend

# توقف
pm2 stop writers-frontend

# حذف
pm2 delete writers-frontend

# ذخیره برای اجرا در بوت
pm2 save
pm2 startup
```

## 📊 مانیتورینگ در حین اجرا

### Prometheus Metrics

دسترسی به متریک‌ها:
```bash
# متریک‌های Backend
curl http://localhost:8000/metrics

# متریک‌های System (Node Exporter)
curl http://localhost:9100/metrics
```

### Grafana Dashboards

دسترسی از مرورگر:
- URL: http://localhost:3001
- Username: admin
- Password: admin (تغییر دهید)

Dashboards آماده:
- System Overview
- Application Performance
- Database Metrics
- Redis Metrics

### Loki Logs

دسترسی از Grafana:
1. Explore > Loki
2. انتخاب Log Stream
3. اجرای Query

مثال Query:
```logql
{job="writers-backend"} |= "error"
```

## 🔧 دستورات مدیریتی

### مدیریت Database

```bash
# اجرای Migration
cd backend
source venv/bin/activate
alembic upgrade head

# Rollback Migration
alembic downgrade -1

# ایجاد Migration جدید
alembic revision -m "توضیحات"

# بررسی نسخه فعلی
alembic current

# بررسی تاریخچه
alembic history
```

### Backup و Restore

#### Backup Database

```bash
# Backup کامل
pg_dump -U writers_user -d writers_db -F c -f backup_$(date +%Y%m%d_%H%M%S).dump

# Backup با فشرده‌سازی
pg_dump -U writers_user -d writers_db | gzip > backup_$(date +%Y%m%d).sql.gz

# Backup خودکار (crontab)
0 2 * * * pg_dump -U writers_user -d writers_db | gzip > /backup/db_$(date +\%Y\%m\%d).sql.gz
```

#### Restore Database

```bash
# Restore از dump
pg_restore -U writers_user -d writers_db -c backup.dump

# Restore از SQL
gunzip -c backup.sql.gz | psql -U writers_user -d writers_db
```

#### Backup Files

```bash
# Backup دایرکتوری uploads
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz /var/lib/writers/storage

# Restore
tar -xzf uploads_backup.tar.gz -C /
```

### پاکسازی و نگهداری

#### پاکسازی Cache

```bash
# پاکسازی Redis Cache
redis-cli -a your_password FLUSHDB

# پاکسازی فقط کلیدهای خاص
redis-cli -a your_password --scan --pattern "session:*" | xargs redis-cli -a your_password DEL
```

#### پاکسازی Logs

```bash
# پاکسازی logs قدیمی (بیش از 7 روز)
sudo journalctl --vacuum-time=7d

# پاکسازی بر اساس حجم
sudo journalctl --vacuum-size=1G

# پاکسازی Nginx logs
sudo truncate -s 0 /var/log/nginx/access.log
sudo truncate -s 0 /var/log/nginx/error.log
```

#### پاکسازی Docker

```bash
# پاکسازی containers متوقف شده
docker container prune

# پاکسازی images استفاده نشده
docker image prune -a

# پاکسازی volumes
docker volume prune

# پاکسازی کامل
docker system prune -a --volumes
```

## 🔄 به‌روزرسانی سیستم

### به‌روزرسانی Manual

```bash
# 1. Pull کردن آخرین تغییرات
cd /var/www/writers
git pull origin main

# 2. به‌روزرسانی Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
sudo systemctl restart writers-backend

# 3. به‌روزرسانی Frontend
cd ../frontend
npm install
npm run build
sudo systemctl restart writers-frontend

# 4. به‌روزرسانی Worker
cd ../worker
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart writers-worker
```

### به‌روزرسانی Docker

```bash
cd infrastructure

# Pull کردن آخرین images
docker-compose pull

# راه‌اندازی مجدد با images جدید
docker-compose up -d

# پاکسازی images قدیمی
docker image prune
```

### استراتژی Zero-Downtime Update

```bash
# 1. راه‌اندازی نسخه جدید در port دیگر
# 2. بررسی سلامت نسخه جدید
# 3. تغییر Nginx upstream
# 4. reload Nginx (بدون downtime)
sudo nginx -s reload
# 5. توقف نسخه قدیمی
```

## 🚨 مدیریت خطاها

### خطاهای Backend

```bash
# بررسی logs با جزئیات
sudo journalctl -u writers-backend -n 100 --no-pager

# اجرای debug mode
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --log-level debug
```

### خطاهای Frontend

```bash
# بررسی logs
sudo journalctl -u writers-frontend -n 100

# اجرای در development mode
cd frontend
npm run dev
```

### خطاهای Worker

```bash
# بررسی logs
sudo journalctl -u writers-worker -n 100

# اجرای با log level بالا
cd worker
source venv/bin/activate
celery -A tasks worker --loglevel=debug
```

### بررسی سلامت سیستم

```bash
# استفاده از health check script
cd infrastructure/scripts
sudo bash health-check.sh

# یا بررسی دستی
curl http://localhost:8000/health
curl http://localhost:3000
redis-cli ping
psql -U writers_user -d writers_db -c "SELECT 1;"
```

## 📈 مقیاس‌پذیری

### افزایش Workers

```bash
# افزایش Backend workers
sudo nano /etc/systemd/system/writers-backend.service
# تغییر --workers 4 به --workers 8
sudo systemctl daemon-reload
sudo systemctl restart writers-backend

# افزایش Celery workers
sudo nano /etc/systemd/system/writers-worker.service
# تغییر --concurrency=4 به --concurrency=8
sudo systemctl daemon-reload
sudo systemctl restart writers-worker
```

### Scale با Docker

```bash
# افزایش تعداد worker containers
docker-compose up -d --scale worker=3

# بررسی
docker-compose ps
```

## 🛑 توقف سیستم

### توقف Development

در هر ترمینال: `Ctrl+C`

### توقف Production (Systemd)

```bash
# توقف تمام سرویس‌ها
sudo systemctl stop writers-backend writers-frontend writers-worker

# یا جداگانه
sudo systemctl stop writers-backend
sudo systemctl stop writers-frontend
sudo systemctl stop writers-worker
```

### توقف Docker

```bash
cd infrastructure

# توقف سرویس‌ها
docker-compose stop

# توقف و حذف containers
docker-compose down
```

## 📝 نکات مهم

1. **همیشه قبل از به‌روزرسانی، Backup بگیرید**
2. **Logs را به صورت منظم بررسی کنید**
3. **Monitoring را فعال نگه دارید**
4. **Health checks را تنظیم کنید**
5. **از Load Balancer برای High Availability استفاده کنید**

## 🔗 مراجع مرتبط

- [راهنمای نصب](INSTALLATION.md)
- [راهنمای استقرار](DEPLOYMENT.md)
- [عیب‌یابی](TROUBLESHOOTING.md)
- [مانیتورینگ](MONITORING.md)

---

برای سوالات و مشکلات، به بخش [عیب‌یابی](TROUBLESHOOTING.md) مراجعه کنید.
