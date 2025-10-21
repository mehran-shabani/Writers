# راهنمای استقرار (Deployment Guide)

این مستند شامل دو روش استقرار اپلیکیشن است:
1. **استقرار با Docker Compose** (توصیه شده برای محیط‌های Development و Production)
2. **استقرار مستقیم با systemd** (برای اجرای Native روی سرور)

---

## 📋 فهرست مطالب

- [پیش‌نیازها](#پیش-نیازها)
- [روش ۱: استقرار با Docker Compose](#روش-۱-استقرار-با-docker-compose)
  - [نصب Docker و Docker Compose](#نصب-docker-و-docker-compose)
  - [پیکربندی محیطی](#پیکربندی-محیطی)
  - [راه‌اندازی سرویس‌ها](#راه-اندازی-سرویس-ها)
  - [مدیریت و نگهداری](#مدیریت-و-نگهداری)
- [روش ۲: استقرار مستقیم با systemd](#روش-۲-استقرار-مستقیم-با-systemd)
  - [نصب وابستگی‌ها](#نصب-وابستگی-ها)
  - [راه‌اندازی زیرساخت](#راه-اندازی-زیرساخت)
  - [پیکربندی systemd](#پیکربندی-systemd)
  - [مدیریت سرویس‌ها](#مدیریت-سرویس-ها)
- [مانیتورینگ و لاگ‌ها](#مانیتورینگ-و-لاگ-ها)
- [پشتیبان‌گیری](#پشتیبان-گیری)
- [عیب‌یابی](#عیب-یابی)

---

## پیش‌نیازها

### سخت‌افزار
- **CPU**: حداقل 4 هسته (توصیه: 8+ هسته)
- **RAM**: حداقل 8GB (توصیه: 16GB+)
- **SSD**: برای PostgreSQL (حداقل 100GB)
- **Storage**: 100TB برای فایل‌های اپلیکیشن (mount در `/storage`)

### نرم‌افزار
- **سیستم‌عامل**: Ubuntu 20.04/22.04 LTS یا Debian 11/12
- **دسترسی**: کاربر با دسترسی sudo
- **شبکه**: اتصال به اینترنت برای دانلود بسته‌ها

---

# روش ۱: استقرار با Docker Compose

استفاده از Docker Compose ساده‌ترین و سریع‌ترین روش برای استقرار است.

## نصب Docker و Docker Compose

### Ubuntu/Debian

```bash
# حذف نسخه‌های قدیمی (اگر وجود دارد)
sudo apt-get remove docker docker-engine docker.io containerd runc

# نصب وابستگی‌ها
sudo apt-get update
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# افزودن GPG key رسمی Docker
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# افزودن repository Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# نصب Docker Engine و Docker Compose
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# اضافه کردن کاربر فعلی به گروه docker
sudo usermod -aG docker $USER

# فعال‌سازی خودکار در startup
sudo systemctl enable docker
sudo systemctl start docker

# تست نصب
docker --version
docker compose version
```

**نکته**: پس از اجرای دستور `usermod`، باید از سیستم خارج و دوباره وارد شوید.

## پیکربندی محیطی

### 1. آماده‌سازی فضای ذخیره‌سازی

اگر هنوز فضای ذخیره‌سازی ۱۰۰TB را mount نکرده‌اید:

```bash
# اجرای اسکریپت setup_storage.sh
cd /workspace/infrastructure
sudo STORAGE_DEVICE=/dev/sdX1 ./setup_storage.sh
```

این اسکریپت:
- دیسک را در `/storage` mount می‌کند
- دایرکتوری‌های `uploads/` و `results/` ایجاد می‌کند
- مجوزهای مناسب را تنظیم می‌کند
- mount را در `/etc/fstab` پایدار می‌کند

### 2. آماده‌سازی SSD برای PostgreSQL

```bash
# اجرای اسکریپت setup_postgresql.sh
cd /workspace/infrastructure
sudo SSD_MOUNT_POINT=/mnt/ssd ./setup_postgresql.sh
```

**نکته مهم**: برای استقرار با Docker، این اسکریپت فقط برای ایجاد دایرکتوری داده PostgreSQL استفاده می‌شود. سرویس PostgreSQL توسط Docker اجرا می‌شود.

### 3. پیکربندی فایل‌های محیطی

```bash
# بازگشت به ریشه پروژه
cd /workspace

# کپی فایل نمونه متغیرهای محیطی
cp .env.example .env

# ویرایش و تنظیم مقادیر واقعی
nano .env
```

**متغیرهای مهم که باید تنظیم شوند:**

```bash
# Database
POSTGRES_DB=myapp_production
POSTGRES_USER=myapp_user
POSTGRES_PASSWORD=<generate-secure-password>

# Redis
REDIS_PASSWORD=<generate-secure-password>

# Security
JWT_SECRET=<generate-64-char-random-string>
JWT_REFRESH_SECRET=<generate-64-char-random-string>
SESSION_SECRET=<generate-64-char-random-string>

# Environment
NODE_ENV=production
APP_ENV=production

# URLs
APP_URL=https://yourdomain.com
API_URL=https://api.yourdomain.com

# Storage
STORAGE_ROOT=/storage
SSD_MOUNT_POINT=/mnt/ssd

# Ports
FRONTEND_PORT=3000
BACKEND_PORT=8000
```

**تولید رمزهای امن:**

```bash
# با OpenSSL
openssl rand -base64 48

# با Python
python3 -c "import secrets; print(secrets.token_hex(32))"

# با Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

### 4. ایجاد فایل‌های محیطی سرویس‌ها

اگر سرویس‌های frontend, backend, worker نیاز به متغیرهای اختصاصی دارند:

```bash
# Frontend
touch frontend/.env.local

# Backend
touch backend/.env

# Worker
touch worker/.env
```

## راه‌اندازی سرویس‌ها

### Build و اجرای سرویس‌ها

```bash
# رفتن به دایرکتوری infrastructure
cd /workspace/infrastructure

# Build کردن image ها (اولین بار)
docker compose build

# اجرای تمام سرویس‌ها در background
docker compose up -d

# مشاهده وضعیت سرویس‌ها
docker compose ps

# مشاهده لاگ‌های تمام سرویس‌ها
docker compose logs -f

# مشاهده لاگ یک سرویس خاص
docker compose logs -f backend
```

### چک کردن سلامت سرویس‌ها

```bash
# بررسی health check
docker compose ps

# تست اتصال به PostgreSQL
docker compose exec postgres psql -U myapp_user -d myapp_db -c "SELECT version();"

# تست اتصال به Redis
docker compose exec redis redis-cli -a YOUR_REDIS_PASSWORD ping

# تست Backend API
curl http://localhost:8000/health

# تست Frontend
curl http://localhost:3000
```

## مدیریت و نگهداری

### دستورات پرکاربرد

```bash
# مشاهده لاگ‌ها
docker compose logs -f [service_name]

# ری‌استارت یک سرویس
docker compose restart backend

# ری‌استارت تمام سرویس‌ها
docker compose restart

# متوقف کردن سرویس‌ها
docker compose stop

# حذف سرویس‌ها (داده‌ها حفظ می‌شود)
docker compose down

# حذف سرویس‌ها + volume ها (خطرناک!)
docker compose down -v

# Scale کردن worker برای پردازش بیشتر
docker compose up -d --scale worker=3

# بروزرسانی image ها
docker compose pull
docker compose up -d

# مشاهده منابع مصرفی
docker stats
```

### مانیتورینگ

```bash
# نصابت Docker stats برای مانیتورینگ real-time
watch -n 1 'docker stats --no-stream'

# بررسی فضای دیسک
docker system df

# پاک‌سازی فضای اضافی
docker system prune -a

# مشاهده network
docker network ls
docker network inspect app-network
```

### لاگ‌ها

لاگ‌های Docker به‌صورت پیش‌فرض در `/var/lib/docker/containers/` ذخیره می‌شوند.

برای محدود کردن حجم لاگ‌ها، فایل `/etc/docker/daemon.json` ایجاد کنید:

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

سپس Docker را ری‌استارت کنید:

```bash
sudo systemctl restart docker
```

---

# روش ۲: استقرار مستقیم با systemd

این روش برای اجرای مستقیم سرویس‌ها روی سرور بدون Docker است.

## نصب وابستگی‌ها

### Node.js (برای Backend, Frontend, Worker)

```bash
# نصب Node.js 18.x LTS
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# بررسی نصب
node --version
npm --version
```

### PostgreSQL

```bash
# اجرای اسکریپت setup با نصب کامل
cd /workspace/infrastructure
sudo ./setup_postgresql.sh

# این اسکریپت:
# - PostgreSQL 15 را نصب می‌کند
# - دایرکتوری داده را روی SSD پیکربندی می‌کند
# - تنظیمات بهینه برای SSD اعمال می‌کند
# - سرویس PostgreSQL را شروع می‌کند
```

### Redis

```bash
# اجرای اسکریپت setup
cd /workspace/infrastructure
sudo ./setup_redis.sh

# رمز عبور Redis را یادداشت کنید
sudo cat /etc/redis/redis-password.txt
```

## راه‌اندازی زیرساخت

### Storage Setup

```bash
cd /workspace/infrastructure
sudo STORAGE_DEVICE=/dev/sdX1 ./setup_storage.sh
```

### پیکربندی Database

```bash
# ایجاد database و user
sudo -u postgres psql << EOF
CREATE DATABASE myapp_production;
CREATE USER myapp_user WITH ENCRYPTED PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE myapp_production TO myapp_user;
\q
EOF

# تست اتصال
psql -U myapp_user -d myapp_production -h localhost -c "SELECT version();"
```

### Build اپلیکیشن‌ها

```bash
cd /workspace

# Backend
cd backend
npm install --production
npm run build  # اگر build process دارد

# Frontend
cd ../frontend
npm install --production
npm run build

# Worker
cd ../worker
npm install --production
npm run build  # اگر build process دارد

cd ..
```

## پیکربندی systemd

### 1. ایجاد فایل سرویس Backend

```bash
sudo nano /etc/systemd/system/app-backend.service
```

محتوا:

```ini
[Unit]
Description=Application Backend API Server
After=network.target postgresql.service redis-server.service
Wants=postgresql.service redis-server.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/workspace/backend

# بارگذاری متغیرهای محیطی
EnvironmentFile=/workspace/.env
EnvironmentFile=/workspace/backend/.env

# متغیرهای اضافی
Environment="NODE_ENV=production"
Environment="POSTGRES_HOST=localhost"
Environment="REDIS_HOST=localhost"

# دستور اجرا
ExecStart=/usr/bin/node /workspace/backend/dist/index.js
# یا برای Node.js بدون build:
# ExecStart=/usr/bin/node /workspace/backend/src/index.js

# ری‌استارت خودکار
Restart=always
RestartSec=10

# Logging
StandardOutput=append:/var/log/app/backend.log
StandardError=append:/var/log/app/backend-error.log

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/storage /var/log/app /tmp

# Resource limits
LimitNOFILE=65536
MemoryMax=2G
CPUQuota=200%

[Install]
WantedBy=multi-user.target
```

### 2. ایجاد فایل سرویس Frontend

```bash
sudo nano /etc/systemd/system/app-frontend.service
```

محتوا:

```ini
[Unit]
Description=Application Frontend Web Server
After=network.target app-backend.service
Wants=app-backend.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/workspace/frontend

# بارگذاری متغیرهای محیطی
EnvironmentFile=/workspace/.env
EnvironmentFile=/workspace/frontend/.env.local

# متغیرهای اضافی
Environment="NODE_ENV=production"
Environment="PORT=3000"

# دستور اجرا (Next.js)
ExecStart=/usr/bin/npm start
# یا برای production build:
# ExecStart=/usr/bin/node /workspace/frontend/.next/standalone/server.js

# ری‌استارت خودکار
Restart=always
RestartSec=10

# Logging
StandardOutput=append:/var/log/app/frontend.log
StandardError=append:/var/log/app/frontend-error.log

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/log/app

# Resource limits
LimitNOFILE=65536
MemoryMax=1G

[Install]
WantedBy=multi-user.target
```

### 3. ایجاد فایل سرویس Worker

```bash
sudo nano /etc/systemd/system/app-worker.service
```

محتوا:

```ini
[Unit]
Description=Application Background Worker
After=network.target postgresql.service redis-server.service app-backend.service
Wants=postgresql.service redis-server.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/workspace/worker

# بارگذاری متغیرهای محیطی
EnvironmentFile=/workspace/.env
EnvironmentFile=/workspace/worker/.env

# متغیرهای اضافی
Environment="NODE_ENV=production"
Environment="POSTGRES_HOST=localhost"
Environment="REDIS_HOST=localhost"
Environment="WORKER_CONCURRENCY=5"

# دستور اجرا
ExecStart=/usr/bin/node /workspace/worker/dist/index.js

# ری‌استارت خودکار
Restart=always
RestartSec=10

# Logging
StandardOutput=append:/var/log/app/worker.log
StandardError=append:/var/log/app/worker-error.log

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/storage /var/log/app /tmp

# Resource limits
LimitNOFILE=65536
MemoryMax=4G
CPUQuota=400%

[Install]
WantedBy=multi-user.target
```

### 4. ایجاد دایرکتوری لاگ

```bash
sudo mkdir -p /var/log/app
sudo chown www-data:www-data /var/log/app
sudo chmod 755 /var/log/app
```

### 5. تنظیم مجوزها

```bash
# اطمینان از مجوزهای صحیح
sudo chown -R www-data:www-data /workspace/backend
sudo chown -R www-data:www-data /workspace/frontend
sudo chown -R www-data:www-data /workspace/worker

# فایل‌های .env نباید برای همه قابل خواندن باشند
sudo chmod 640 /workspace/.env
sudo chmod 640 /workspace/backend/.env
sudo chmod 640 /workspace/frontend/.env.local
sudo chmod 640 /workspace/worker/.env
sudo chown www-data:www-data /workspace/.env
sudo chown www-data:www-data /workspace/backend/.env
sudo chown www-data:www-data /workspace/frontend/.env.local
sudo chown www-data:www-data /workspace/worker/.env
```

## مدیریت سرویس‌ها

### فعال‌سازی و شروع سرویس‌ها

```bash
# بارگذاری مجدد systemd
sudo systemctl daemon-reload

# فعال‌سازی برای شروع خودکار
sudo systemctl enable app-backend.service
sudo systemctl enable app-frontend.service
sudo systemctl enable app-worker.service

# شروع سرویس‌ها
sudo systemctl start app-backend.service
sudo systemctl start app-frontend.service
sudo systemctl start app-worker.service

# بررسی وضعیت
sudo systemctl status app-backend.service
sudo systemctl status app-frontend.service
sudo systemctl status app-worker.service
```

### دستورات مدیریتی

```bash
# مشاهده لاگ‌ها
sudo journalctl -u app-backend.service -f
sudo journalctl -u app-frontend.service -f
sudo journalctl -u app-worker.service -f

# یا لاگ‌های فایل
tail -f /var/log/app/backend.log
tail -f /var/log/app/frontend.log
tail -f /var/log/app/worker.log

# ری‌استارت سرویس
sudo systemctl restart app-backend.service
sudo systemctl restart app-frontend.service
sudo systemctl restart app-worker.service

# متوقف کردن
sudo systemctl stop app-backend.service
sudo systemctl stop app-frontend.service
sudo systemctl stop app-worker.service

# غیرفعال کردن شروع خودکار
sudo systemctl disable app-backend.service
```

### مشاهده وضعیت کلی

```bash
# وضعیت تمام سرویس‌های اپلیکیشن
systemctl status 'app-*'

# لیست تمام سرویس‌های در حال اجرا
systemctl list-units --type=service --state=running | grep app-
```

---

# مانیتورینگ و لاگ‌ها

## مانیتورینگ منابع سیستم

### استفاده از htop

```bash
sudo apt-get install htop
htop
```

### مانیتورینگ دیسک

```bash
# فضای استفاده شده
df -h

# استفاده از inode
df -i

# فضای استفاده شده توسط /storage
du -sh /storage/*

# بزرگ‌ترین فایل‌ها
find /storage -type f -exec du -h {} + | sort -rh | head -n 20
```

### مانیتورینگ PostgreSQL

```bash
# اتصالات فعال
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"

# حجم دیتابیس
sudo -u postgres psql -c "SELECT pg_database.datname, pg_size_pretty(pg_database_size(pg_database.datname)) AS size FROM pg_database;"

# کوئری‌های آهسته
sudo -u postgres psql -d myapp_production -c "SELECT query, calls, total_time, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"
```

### مانیتورینگ Redis

```bash
# اطلاعات کلی
redis-cli -a $(sudo cat /etc/redis/redis-password.txt) INFO

# استفاده از حافظه
redis-cli -a $(sudo cat /etc/redis/redis-password.txt) INFO memory

# تعداد کلیدها
redis-cli -a $(sudo cat /etc/redis/redis-password.txt) DBSIZE

# مانیتور real-time
redis-cli -a $(sudo cat /etc/redis/redis-password.txt) MONITOR
```

## مدیریت لاگ‌ها

### Log Rotation

برای Docker Compose، لاگ‌ها به‌صورت خودکار rotate می‌شوند (اگر در `daemon.json` تنظیم کرده باشید).

برای systemd:

```bash
sudo nano /etc/logrotate.d/app
```

محتوا:

```
/var/log/app/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload app-backend.service app-frontend.service app-worker.service > /dev/null 2>&1 || true
    endscript
}
```

تست:

```bash
sudo logrotate -f /etc/logrotate.d/app
```

---

# پشتیبان‌گیری

## PostgreSQL Backup

### Backup دستی

```bash
# Backup کامل دیتابیس
sudo -u postgres pg_dump myapp_production > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup فشرده
sudo -u postgres pg_dump myapp_production | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Restore
sudo -u postgres psql myapp_production < backup.sql
# یا برای فایل فشرده:
gunzip -c backup.sql.gz | sudo -u postgres psql myapp_production
```

### Backup خودکار با Cron

```bash
sudo nano /usr/local/bin/backup-postgres.sh
```

محتوا:

```bash
#!/bin/bash
BACKUP_DIR="/storage/backups/postgres"
RETENTION_DAYS=30
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

# Backup
sudo -u postgres pg_dump myapp_production | gzip > "$BACKUP_DIR/backup_$DATE.sql.gz"

# حذف backup های قدیمی
find "$BACKUP_DIR" -name "backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: backup_$DATE.sql.gz"
```

مجوز اجرا و افزودن به Cron:

```bash
sudo chmod +x /usr/local/bin/backup-postgres.sh

# افزودن به cron (هر روز ساعت 2 صبح)
sudo crontab -e
# اضافه کنید:
0 2 * * * /usr/local/bin/backup-postgres.sh >> /var/log/app/backup.log 2>&1
```

## Redis Backup

Redis به‌صورت خودکار snapshot ذخیره می‌کند (`appendonly.aof` و `dump.rdb`).

برای backup دستی:

```bash
# Trigger کردن save
redis-cli -a $(sudo cat /etc/redis/redis-password.txt) BGSAVE

# کپی فایل‌های داده
sudo cp /var/lib/redis/dump.rdb /storage/backups/redis/dump_$(date +%Y%m%d).rdb
```

## Application Files Backup

```bash
# Backup کد اپلیکیشن
tar -czf app_backup_$(date +%Y%m%d).tar.gz /workspace

# Backup فایل‌های آپلود شده
rsync -av --progress /storage/uploads/ /storage/backups/uploads/
```

---

# عیب‌یابی

## مشکلات رایج

### سرویس start نمی‌شود (Docker)

```bash
# بررسی لاگ‌ها
docker compose logs [service_name]

# بررسی وضعیت container
docker compose ps

# بررسی health check
docker inspect [container_name] | grep -A 10 Health

# ری‌استارت با build مجدد
docker compose down
docker compose build --no-cache
docker compose up -d
```

### سرویس start نمی‌شود (systemd)

```bash
# بررسی دقیق وضعیت
sudo systemctl status app-backend.service -l

# بررسی لاگ‌ها
sudo journalctl -u app-backend.service -n 100 --no-pager

# بررسی فایل سرویس
sudo systemd-analyze verify /etc/systemd/system/app-backend.service

# تست دستی
cd /workspace/backend
sudo -u www-data node dist/index.js
```

### خطای اتصال به Database

```bash
# بررسی اینکه PostgreSQL در حال اجرا است
sudo systemctl status postgresql

# تست اتصال
psql -U myapp_user -d myapp_production -h localhost

# بررسی تنظیمات اتصال
cat /workspace/.env | grep POSTGRES

# بررسی لاگ PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-15-main.log
```

### خطای اتصال به Redis

```bash
# بررسی وضعیت Redis
sudo systemctl status redis-server

# تست اتصال
redis-cli -a $(sudo cat /etc/redis/redis-password.txt) PING

# بررسی پورت
sudo netstat -tlnp | grep 6379

# بررسی لاگ
sudo tail -f /var/log/redis/redis-server.log
```

### فضای دیسک پر شده

```bash
# بررسی استفاده از دیسک
df -h

# پیدا کردن فایل‌های بزرگ
du -sh /var/lib/docker/* | sort -rh | head -n 10
du -sh /storage/* | sort -rh | head -n 10

# پاک‌سازی Docker (اگر از Docker استفاده می‌کنید)
docker system prune -a --volumes

# پاک‌سازی لاگ‌های قدیمی
sudo journalctl --vacuum-time=7d
sudo find /var/log -name "*.log" -mtime +30 -delete
```

### مشکلات Performance

```bash
# بررسی CPU و RAM
top
htop

# بررسی I/O دیسک
iostat -x 1

# بررسی اتصالات شبکه
sudo netstat -tunap | grep ESTABLISHED | wc -l

# بررسی query های آهسته PostgreSQL
sudo -u postgres psql -d myapp_production -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"
```

### Port در حال استفاده است

```bash
# پیدا کردن process که پورت را استفاده می‌کند
sudo lsof -i :8000
sudo netstat -tlnp | grep :8000

# Kill کردن process
sudo kill -9 [PID]
```

## دریافت کمک

اگر مشکل حل نشد:

1. لاگ‌های کامل را جمع‌آوری کنید
2. تنظیمات سیستم را بررسی کنید
3. نسخه‌های نرم‌افزار را چک کنید
4. با تیم توسعه تماس بگیرید

---

## منابع اضافی

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [systemd Documentation](https://www.freedesktop.org/software/systemd/man/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/docs/)

---

**تاریخ آخرین بروزرسانی**: 2025-10-21  
**نسخه**: 1.0
