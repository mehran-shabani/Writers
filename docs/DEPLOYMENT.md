# راهنمای استقرار (Deployment)

این سند مراحل کامل استقرار سیستم Writers در محیط Production را شرح می‌دهد.

## 📋 قبل از شروع

### چک‌لیست پیش از استقرار

- [ ] سرور با مشخصات مناسب آماده است
- [ ] دامنه (Domain) تهیه و تنظیم شده
- [ ] SSL Certificate آماده است یا Let's Encrypt قابل استفاده است
- [ ] Backup Strategy تعریف شده
- [ ] Monitoring راه‌اندازی شده
- [ ] مستندات و runbook آماده است
- [ ] تیم پشتیبانی آماده است

### تنظیمات DNS

```
A     @           IP_ADDRESS       (yourdomain.com)
A     www         IP_ADDRESS       (www.yourdomain.com)
A     api         IP_ADDRESS       (api.yourdomain.com - اختیاری)
```

## 🚀 استقرار روی سرور مجازی (VPS)

### مرحله 1: آماده‌سازی سرور

```bash
# به‌روزرسانی سیستم
sudo apt update && sudo apt upgrade -y

# نصب ابزارهای پایه
sudo apt install -y git curl wget vim build-essential

# ایجاد کاربر deployment
sudo useradd -m -s /bin/bash deploy
sudo usermod -aG sudo deploy

# تنظیم SSH key برای کاربر deploy
sudo mkdir -p /home/deploy/.ssh
sudo cp ~/.ssh/authorized_keys /home/deploy/.ssh/
sudo chown -R deploy:deploy /home/deploy/.ssh
sudo chmod 700 /home/deploy/.ssh
sudo chmod 600 /home/deploy/.ssh/authorized_keys

# ورود به کاربر deploy
sudo su - deploy
```

### مرحله 2: نصب وابستگی‌ها

```bash
# Python 3.11
sudo apt install -y python3.11 python3.11-venv python3-pip

# Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# PostgreSQL 15
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget -qO- https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo tee /etc/apt/trusted.gpg.d/pgdg.asc
sudo apt update
sudo apt install -y postgresql-15 postgresql-contrib-15

# Redis 7
sudo apt install -y redis-server

# Nginx
sudo apt install -y nginx

# Certbot (برای SSL)
sudo apt install -y certbot python3-certbot-nginx
```

### مرحله 3: پیکربندی PostgreSQL

```bash
# اجرای اسکریپت راه‌اندازی
cd /tmp
wget https://raw.githubusercontent.com/yourusername/writers/main/infrastructure/setup_postgresql.sh
sudo bash setup_postgresql.sh

# یا دستی:
sudo -u postgres psql <<EOF
CREATE USER writers_user WITH PASSWORD 'STRONG_PASSWORD_HERE';
CREATE DATABASE writers_db OWNER writers_user;
GRANT ALL PRIVILEGES ON DATABASE writers_db TO writers_user;
EOF
```

### مرحله 4: پیکربندی Redis

```bash
# ویرایش پیکربندی
sudo nano /etc/redis/redis.conf

# تنظیمات امنیتی
requirepass YOUR_REDIS_PASSWORD
bind 127.0.0.1
maxmemory 512mb
maxmemory-policy allkeys-lru

# راه‌اندازی
sudo systemctl enable redis-server
sudo systemctl restart redis-server
```

### مرحله 5: دریافت کد

```bash
# ایجاد دایرکتوری
sudo mkdir -p /var/www/writers
sudo chown deploy:deploy /var/www/writers

# کلون repository
cd /var/www/writers
git clone https://github.com/yourusername/writers.git .

# یا با SSH key
git clone git@github.com:yourusername/writers.git .
```

### مرحله 6: تنظیم Environment Variables

```bash
# کپی و ویرایش .env
cp .env.example .env
nano .env
```

محتوای `.env` برای Production:

```env
# Database
DATABASE_URL=postgresql://writers_user:STRONG_PASSWORD@localhost:5432/writers_db
POSTGRES_PASSWORD=STRONG_PASSWORD

# Redis
REDIS_PASSWORD=YOUR_REDIS_PASSWORD
REDIS_URL=redis://:YOUR_REDIS_PASSWORD@localhost:6379/0

# JWT
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Production Settings
NODE_ENV=production
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
FRONTEND_PORT=3000

# Domain
DOMAIN=yourdomain.com
ADMIN_EMAIL=admin@yourdomain.com
APP_URL=https://yourdomain.com
NEXT_PUBLIC_API_URL=https://yourdomain.com/api

# Storage
STORAGE_ROOT=/var/lib/writers/storage
```

### مرحله 7: نصب و Build Backend

```bash
cd /var/www/writers/backend

# ایجاد virtual environment
python3 -m venv venv
source venv/bin/activate

# نصب وابستگی‌ها
pip install --upgrade pip
pip install -r requirements.txt

# اجرای migrations
alembic upgrade head

# تست
uvicorn app.main:app --host 127.0.0.1 --port 8000 &
sleep 5
curl http://localhost:8000/health
kill %1
```

### مرحله 8: نصب و Build Frontend

```bash
cd /var/www/writers/frontend

# نصب وابستگی‌ها
npm ci --production=false

# Build
npm run build

# تست
npm start &
sleep 10
curl http://localhost:3000
kill %1
```

### مرحله 9: نصب Worker

```bash
cd /var/www/writers/worker

# ایجاد virtual environment
python3 -m venv venv
source venv/bin/activate

# نصب وابستگی‌ها
pip install --upgrade pip
pip install -r requirements.txt
```

### مرحله 10: تنظیم Systemd Services

#### Backend Service

```bash
sudo nano /etc/systemd/system/writers-backend.service
```

```ini
[Unit]
Description=Writers FastAPI Backend
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=deploy
Group=deploy
WorkingDirectory=/var/www/writers/backend
Environment="PATH=/var/www/writers/backend/venv/bin"
EnvironmentFile=/var/www/writers/.env
ExecStart=/var/www/writers/backend/venv/bin/uvicorn app.main:app \
    --host 127.0.0.1 \
    --port 8000 \
    --workers 4 \
    --log-level info
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

#### Frontend Service

```bash
sudo nano /etc/systemd/system/writers-frontend.service
```

```ini
[Unit]
Description=Writers Next.js Frontend
After=network.target

[Service]
Type=simple
User=deploy
Group=deploy
WorkingDirectory=/var/www/writers/frontend
Environment="PATH=/usr/bin:/usr/local/bin"
Environment="NODE_ENV=production"
Environment="PORT=3000"
EnvironmentFile=/var/www/writers/.env
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

#### Worker Service

```bash
sudo nano /etc/systemd/system/writers-worker.service
```

```ini
[Unit]
Description=Writers Celery Worker
After=network.target redis.service postgresql.service

[Service]
Type=simple
User=deploy
Group=deploy
WorkingDirectory=/var/www/writers/worker
Environment="PATH=/var/www/writers/worker/venv/bin"
EnvironmentFile=/var/www/writers/.env
ExecStart=/var/www/writers/worker/venv/bin/celery -A tasks worker \
    --loglevel=info \
    --concurrency=4 \
    --max-tasks-per-child=1000
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

#### فعال‌سازی Services

```bash
# Reload daemon
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable writers-backend
sudo systemctl enable writers-frontend
sudo systemctl enable writers-worker

# Start services
sudo systemctl start writers-backend
sudo systemctl start writers-frontend
sudo systemctl start writers-worker

# بررسی وضعیت
sudo systemctl status writers-backend
sudo systemctl status writers-frontend
sudo systemctl status writers-worker
```

### مرحله 11: پیکربندی Nginx

```bash
# کپی فایل پیکربندی
sudo cp /var/www/writers/infrastructure/nginx/nginx.conf /etc/nginx/sites-available/writers

# ویرایش domain
sudo nano /etc/nginx/sites-available/writers
# تغییر yourdomain.com به domain واقعی

# فعال‌سازی
sudo ln -s /etc/nginx/sites-available/writers /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# تست
sudo nginx -t

# راه‌اندازی
sudo systemctl restart nginx
```

### مرحله 12: تنظیم SSL با Let's Encrypt

```bash
# درخواست گواهی
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# تست تمدید خودکار
sudo certbot renew --dry-run

# یا استفاده از اسکریپت
cd /var/www/writers/infrastructure/scripts
sudo bash setup-ssl.sh yourdomain.com admin@yourdomain.com
```

### مرحله 13: تنظیم Firewall

```bash
# فعال‌سازی UFW
sudo ufw default deny incoming
sudo ufw default allow outgoing

# باز کردن پورت‌های ضروری
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS

# فعال‌سازی
sudo ufw enable

# بررسی وضعیت
sudo ufw status
```

### مرحله 14: راه‌اندازی Monitoring

```bash
# نصب Docker (برای monitoring stack)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker deploy

# نصب Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# راه‌اندازی monitoring
cd /var/www/writers/infrastructure
sudo bash scripts/setup-monitoring.sh
```

## 🐳 استقرار با Docker

### مرحله 1: آماده‌سازی

```bash
# نصب Docker و Docker Compose (اگر نصب نیست)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# کلون repository
git clone https://github.com/yourusername/writers.git
cd writers
```

### مرحله 2: تنظیم Environment

```bash
cp .env.example .env
nano .env
# تنظیم مقادیر برای production
```

### مرحله 3: Build و Run

```bash
cd infrastructure

# Build images
docker-compose build

# راه‌اندازی
docker-compose up -d

# بررسی وضعیت
docker-compose ps

# مشاهده logs
docker-compose logs -f
```

### مرحله 4: اجرای Migration

```bash
docker-compose exec backend alembic upgrade head
```

### مرحله 5: تنظیم Nginx و SSL

```bash
# پیکربندی Nginx در host
sudo cp nginx/nginx.conf /etc/nginx/sites-available/writers
sudo ln -s /etc/nginx/sites-available/writers /etc/nginx/sites-enabled/

# SSL
sudo certbot --nginx -d yourdomain.com
```

## ☁️ استقرار روی Cloud Providers

### AWS (Amazon Web Services)

#### با EC2

```bash
# 1. راه‌اندازی EC2 instance
#    - Instance type: t3.medium یا بالاتر
#    - Storage: 50GB SSD
#    - Security Group: 22, 80, 443

# 2. نصب مطابق بخش VPS

# 3. تنظیم RDS برای PostgreSQL
#    - Engine: PostgreSQL 15
#    - Instance class: db.t3.medium

# 4. تنظیم ElastiCache برای Redis
#    - Engine: Redis 7
#    - Node type: cache.t3.medium

# 5. تنظیم S3 برای storage
aws s3 mb s3://writers-storage

# 6. تنظیم CloudWatch برای monitoring
```

#### با ECS (Container Service)

```bash
# 1. Push images به ECR
aws ecr create-repository --repository-name writers-backend
aws ecr create-repository --repository-name writers-frontend
aws ecr create-repository --repository-name writers-worker

# 2. Build و Push
docker-compose build
docker tag writers-backend:latest AWS_ACCOUNT.dkr.ecr.region.amazonaws.com/writers-backend:latest
docker push AWS_ACCOUNT.dkr.ecr.region.amazonaws.com/writers-backend:latest

# 3. ایجاد ECS cluster و services
```

### Google Cloud Platform (GCP)

```bash
# 1. ایجاد VM instance
gcloud compute instances create writers-server \
    --machine-type=n1-standard-2 \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud

# 2. ایجاد Cloud SQL (PostgreSQL)
gcloud sql instances create writers-db \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro

# 3. ایجاد Memorystore (Redis)
gcloud redis instances create writers-redis \
    --size=1 \
    --region=us-central1

# 4. نصب application مطابق VPS
```

### DigitalOcean

```bash
# 1. ایجاد Droplet
#    - Size: 2GB RAM, 1 CPU
#    - Image: Ubuntu 22.04

# 2. ایجاد Managed Database (PostgreSQL)
# از پنل DigitalOcean

# 3. نصب Redis
sudo apt install redis-server

# 4. نصب application مطابق VPS

# 5. تنظیم Load Balancer (اختیاری)
```

## 📊 تنظیمات Performance

### Nginx Caching

```nginx
# در nginx.conf
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=1g inactive=60m;

location /api/ {
    proxy_cache my_cache;
    proxy_cache_valid 200 10m;
    proxy_cache_valid 404 1m;
    add_header X-Cache-Status $upstream_cache_status;
}
```

### Database Connection Pooling

در `.env`:
```env
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10
```

### Redis Optimization

```conf
# در redis.conf
maxmemory-policy allkeys-lru
tcp-backlog 511
timeout 300
```

## 🔄 استراتژی Deployment

### Blue-Green Deployment

```bash
# 1. نصب نسخه جدید در port دیگر
# 2. تست نسخه جدید
# 3. تغییر Nginx upstream
# 4. Reload Nginx
# 5. حذف نسخه قدیمی
```

### Rolling Update

```bash
# با Docker Compose
docker-compose up -d --no-deps --build backend

# با Kubernetes
kubectl set image deployment/writers-backend backend=writers-backend:v2
```

### Canary Deployment

```nginx
# در Nginx
upstream backend {
    server backend-v1:8000 weight=90;
    server backend-v2:8000 weight=10;
}
```

## 🔐 امنیت Production

### Security Headers

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
```

### Fail2Ban

```bash
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

### تنظیمات SSH

```bash
sudo nano /etc/ssh/sshd_config

# تغییرات:
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes

sudo systemctl restart sshd
```

## 📝 Post-Deployment Checklist

- [ ] تمام services اجرا می‌شوند
- [ ] Health checks موفق هستند
- [ ] SSL کار می‌کند
- [ ] Monitoring فعال است
- [ ] Logs جمع‌آوری می‌شوند
- [ ] Backup خودکار تنظیم شده
- [ ] Alerts تنظیم شده
- [ ] Domain به درستی تنظیم است
- [ ] Email notifications کار می‌کند
- [ ] Performance قابل قبول است

## 🆘 Rollback Strategy

```bash
# Rollback با Git
cd /var/www/writers
git log --oneline
git checkout <previous-commit>
sudo systemctl restart writers-backend writers-frontend writers-worker

# Rollback با Docker
docker-compose down
docker-compose up -d --force-recreate
```

---

برای جزئیات بیشتر، به [راهنمای اجرا](RUNNING.md) و [عیب‌یابی](TROUBLESHOOTING.md) مراجعه کنید.
