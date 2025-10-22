# راهنمای راه‌اندازی پروژه Writers

این راهنما مراحل کامل راه‌اندازی پروژه Writers را از صفر تا صد شرح می‌دهد.

## فهرست مطالب

1. [پیش‌نیازها](#پیش‌نیازها)
2. [نصب وابستگی‌ها](#نصب-وابستگی‌ها)
3. [پیکربندی پایگاه داده](#پیکربندی-پایگاه-داده)
4. [راه‌اندازی Backend](#راه‌اندازی-backend)
5. [راه‌اندازی Frontend](#راه‌اندازی-frontend)
6. [راه‌اندازی Worker](#راه‌اندازی-worker)
7. [پیکربندی Nginx](#پیکربندی-nginx)
8. [راه‌اندازی Monitoring](#راه‌اندازی-monitoring)
9. [تنظیم SSL](#تنظیم-ssl)
10. [استقرار Production](#استقرار-production)

---

## پیش‌نیازها

### سیستم‌عامل
- Ubuntu 20.04 LTS یا بالاتر
- حداقل 16GB RAM (32GB توصیه می‌شود)
- حداقل 50GB فضای دیسک
- GPU با CUDA support (اختیاری برای پردازش سریع‌تر)

### نرم‌افزارهای مورد نیاز
```bash
# به‌روزرسانی سیستم
sudo apt update && sudo apt upgrade -y

# نصب ابزارهای پایه
sudo apt install -y build-essential curl wget git vim

# نصب Python 3.10+
sudo apt install -y python3.10 python3.10-venv python3-pip

# نصب Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# نصب PostgreSQL 14+
sudo apt install -y postgresql postgresql-contrib

# نصب Redis
sudo apt install -y redis-server

# نصب Nginx
sudo apt install -y nginx
```

---

## نصب وابستگی‌ها

### 1. کلون کردن پروژه

```bash
git clone https://github.com/yourusername/writers.git
cd writers
```

### 2. ایجاد فایل محیطی

```bash
cp .env.example .env
```

فایل `.env` را ویرایش کنید و مقادیر زیر را تنظیم کنید:

```env
# Database
DATABASE_URL=postgresql://writers_user:YOUR_PASSWORD@localhost:5432/writers_db
POSTGRES_PASSWORD=YOUR_PASSWORD

# JWT Secret (یک رشته تصادفی قوی)
SECRET_KEY=$(openssl rand -hex 32)

# Domain (در production)
DOMAIN=yourdomain.com
ADMIN_EMAIL=admin@yourdomain.com
```

---

## پیکربندی پایگاه داده

### 1. راه‌اندازی PostgreSQL

```bash
# اجرای اسکریپت راه‌اندازی
cd infrastructure
sudo bash setup_postgresql.sh

# یا راه‌اندازی دستی:
sudo -u postgres psql <<EOF
CREATE USER writers_user WITH PASSWORD 'YOUR_PASSWORD';
CREATE DATABASE writers_db OWNER writers_user;
GRANT ALL PRIVILEGES ON DATABASE writers_db TO writers_user;
EOF
```

### 2. راه‌اندازی Redis

```bash
# اجرای اسکریپت راه‌اندازی
sudo bash setup_redis.sh

# یا راه‌اندازی دستی:
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

### 3. اجرای Migrations

```bash
cd ../backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# اجرای migrations
alembic upgrade head
```

---

## راه‌اندازی Backend

### محیط Development

```bash
cd backend
source venv/bin/activate

# اجرای سرور
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### محیط Production با Systemd

```bash
# ایجاد فایل سرویس
sudo nano /etc/systemd/system/writers-backend.service
```

محتوای فایل:
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
ExecStart=/var/www/writers/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

فعال‌سازی سرویس:
```bash
sudo systemctl daemon-reload
sudo systemctl enable writers-backend
sudo systemctl start writers-backend
```

---

## راه‌اندازی Frontend

### محیط Development

```bash
cd frontend
npm install

# اجرای سرور
npm run dev
```

### محیط Production

```bash
cd frontend
npm install
npm run build

# اجرای با PM2
npm install -g pm2
pm2 start npm --name "writers-frontend" -- start
pm2 save
pm2 startup
```

یا با Systemd:
```bash
sudo nano /etc/systemd/system/writers-frontend.service
```

محتوای فایل:
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
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## راه‌اندازی Worker

### محیط Development

```bash
cd worker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# اجرای worker
celery -A tasks worker --loglevel=info
```

### محیط Production

```bash
sudo nano /etc/systemd/system/writers-worker.service
```

محتوای فایل:
```ini
[Unit]
Description=Writers Celery Worker
After=network.target redis.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/writers/worker
Environment="PATH=/var/www/writers/worker/venv/bin"
ExecStart=/var/www/writers/worker/venv/bin/celery -A tasks worker --loglevel=info --concurrency=4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## پیکربندی Nginx

### 1. کپی فایل پیکربندی

#### برای Development (بدون SSL):
```bash
sudo cp infrastructure/nginx/nginx-local.conf /etc/nginx/sites-available/writers
```

#### برای Production (با SSL):
```bash
sudo cp infrastructure/nginx/nginx.conf /etc/nginx/sites-available/writers
```

### 2. فعال‌سازی سایت

```bash
# حذف پیکربندی پیش‌فرض
sudo rm /etc/nginx/sites-enabled/default

# فعال‌سازی سایت Writers
sudo ln -s /etc/nginx/sites-available/writers /etc/nginx/sites-enabled/

# تست پیکربندی
sudo nginx -t

# راه‌اندازی مجدد Nginx
sudo systemctl restart nginx
```

### 3. استفاده از اسکریپت استقرار امن

```bash
cd infrastructure/scripts
sudo bash deploy-nginx.sh ../nginx/nginx.conf
```

---

## راه‌اندازی Monitoring

### نصب Docker و Docker Compose

```bash
# نصب Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# نصب Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### راه‌اندازی Monitoring Stack

```bash
cd infrastructure
sudo bash scripts/setup-monitoring.sh
```

یا راه‌اندازی دستی:
```bash
# ایجاد شبکه Docker
docker network create app-network

# راه‌اندازی سرویس‌های monitoring
docker-compose -f docker-compose.monitoring.yml up -d
```

### دسترسی به Dashboard‌ها

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin)
- **Alertmanager**: http://localhost:9093

### پیکربندی Grafana

1. وارد Grafana شوید
2. رمز عبور پیش‌فرض را تغییر دهید
3. Datasource‌های Prometheus و Loki به‌صورت خودکار تنظیم شده‌اند
4. Dashboard‌ها در بخش Dashboards > Browse قابل مشاهده هستند

---

## تنظیم SSL

### استفاده از Let's Encrypt (توصیه می‌شود)

```bash
cd infrastructure/scripts
sudo bash setup-ssl.sh yourdomain.com admin@yourdomain.com
```

این اسکریپت:
- Certbot را نصب می‌کند
- گواهی SSL دریافت می‌کند
- Nginx را پیکربندی می‌کند
- تمدید خودکار را راه‌اندازی می‌کند

### استفاده از گواهی سفارشی

اگر گواهی SSL خودتان را دارید:

```bash
# کپی فایل‌های گواهی
sudo cp your-certificate.crt /etc/ssl/certs/writers.crt
sudo cp your-private-key.key /etc/ssl/private/writers.key

# به‌روزرسانی پیکربندی Nginx
sudo nano /etc/nginx/sites-available/writers
```

در فایل Nginx، مسیرهای گواهی را به‌روز کنید:
```nginx
ssl_certificate /etc/ssl/certs/writers.crt;
ssl_certificate_key /etc/ssl/private/writers.key;
```

---

## استقرار Production

### 1. آماده‌سازی سرور

```bash
# ایجاد کاربر deployment
sudo useradd -m -s /bin/bash deploy
sudo usermod -aG sudo deploy

# ایجاد دایرکتوری پروژه
sudo mkdir -p /var/www/writers
sudo chown deploy:deploy /var/www/writers

# کلون پروژه
cd /var/www/writers
git clone https://github.com/yourusername/writers.git .
```

### 2. راه‌اندازی سرویس‌ها

```bash
# Backend
cd /var/www/writers/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head

# Frontend
cd /var/www/writers/frontend
npm install
npm run build

# Worker
cd /var/www/writers/worker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. راه‌اندازی Systemd Services

```bash
# فعال‌سازی تمام سرویس‌ها
sudo systemctl daemon-reload
sudo systemctl enable writers-backend writers-frontend writers-worker
sudo systemctl start writers-backend writers-frontend writers-worker

# بررسی وضعیت
sudo systemctl status writers-backend
sudo systemctl status writers-frontend
sudo systemctl status writers-worker
```

### 4. پیکربندی Nginx و SSL

```bash
cd /var/www/writers/infrastructure/scripts
sudo bash deploy-nginx.sh ../nginx/nginx.conf
sudo bash setup-ssl.sh yourdomain.com admin@yourdomain.com
```

### 5. راه‌اندازی Monitoring

```bash
sudo bash setup-monitoring.sh
```

### 6. بررسی سلامت سیستم

```bash
sudo bash health-check.sh
```

---

## بررسی و عیب‌یابی

### بررسی Logs

```bash
# Backend logs
sudo journalctl -u writers-backend -f

# Frontend logs
sudo journalctl -u writers-frontend -f

# Worker logs
sudo journalctl -u writers-worker -f

# Nginx logs
sudo tail -f /var/log/nginx/writers_access.log
sudo tail -f /var/log/nginx/writers_error.log
```

### مشکلات رایج

#### Backend در دسترس نیست
```bash
# بررسی وضعیت
sudo systemctl status writers-backend

# بررسی لاگ‌ها
sudo journalctl -u writers-backend --since "10 minutes ago"

# راه‌اندازی مجدد
sudo systemctl restart writers-backend
```

#### خطای دیتابیس
```bash
# بررسی PostgreSQL
sudo systemctl status postgresql
sudo -u postgres psql -c "SELECT version();"

# بررسی اتصال
psql -U writers_user -d writers_db -h localhost
```

#### خطای Redis
```bash
# بررسی Redis
sudo systemctl status redis-server
redis-cli ping

# بررسی لاگ‌ها
sudo journalctl -u redis-server -f
```

---

## مقیاس‌پذیری

### ارتقای RAM

برای سیستم‌های با بار بالا:

- **16GB RAM**: مناسب برای تا 100 کاربر همزمان
- **32GB RAM**: مناسب برای تا 500 کاربر همزمان
- **64GB RAM**: مناسب برای تا 1000+ کاربر همزمان

پیکربندی‌های توصیه شده:

```bash
# برای 32GB RAM
# Backend workers: 8
# Celery workers: 8
# Nginx worker_connections: 2048

# برای 64GB RAM
# Backend workers: 16
# Celery workers: 16
# Nginx worker_connections: 4096
```

### افزایش Worker‌ها

```bash
# ویرایش فایل سرویس Backend
sudo nano /etc/systemd/system/writers-backend.service

# تغییر workers از 4 به 8
ExecStart=.../uvicorn app.main:app --workers 8

# ویرایش فایل سرویس Worker
sudo nano /etc/systemd/system/writers-worker.service

# تغییر concurrency از 4 به 8
ExecStart=.../celery -A tasks worker --concurrency=8

# راه‌اندازی مجدد
sudo systemctl daemon-reload
sudo systemctl restart writers-backend writers-worker
```

### استفاده از Load Balancer

برای چند سرور، از Nginx به عنوان Load Balancer استفاده کنید:

```nginx
upstream backend_servers {
    least_conn;
    server 192.168.1.10:8000 weight=1;
    server 192.168.1.11:8000 weight=1;
    server 192.168.1.12:8000 weight=1;
}
```

---

## پشتیبان‌گیری

### پشتیبان‌گیری از دیتابیس

```bash
# اسکریپت پشتیبان‌گیری روزانه
sudo crontab -e

# اضافه کردن:
0 2 * * * pg_dump -U writers_user writers_db | gzip > /backup/db_$(date +\%Y\%m\%d).sql.gz
```

### پشتیبان‌گیری از فایل‌های آپلود

```bash
# پشتیبان‌گیری هفتگی
0 3 * * 0 tar -czf /backup/uploads_$(date +\%Y\%m\%d).tar.gz /var/lib/writers/uploads
```

---

## امنیت

### توصیه‌های امنیتی

1. **Firewall**: فقط پورت‌های 80، 443 و SSH را باز نگه دارید
```bash
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

2. **SSH**: غیرفعال کردن ورود با password
```bash
sudo nano /etc/ssh/sshd_config
# PasswordAuthentication no
sudo systemctl restart sshd
```

3. **به‌روزرسانی منظم**
```bash
sudo apt update && sudo apt upgrade -y
```

4. **Fail2ban**: محافظت در برابر حملات brute-force
```bash
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

---

## پشتیبانی

برای مشکلات یا سوالات:
- GitHub Issues: https://github.com/yourusername/writers/issues
- Documentation: https://writers-docs.yourdomain.com
- Email: support@yourdomain.com
