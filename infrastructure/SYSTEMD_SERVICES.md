# راهنمای سرویس‌های systemd

این مستند شامل فایل‌های سرویس systemd برای اجرای مستقیم اپلیکیشن روی سرور است.

---

## 📋 فهرست

- [نمای کلی](#نمای-کلی)
- [پیش‌نیازها](#پیش-نیازها)
- [فایل‌های سرویس](#فایل-های-سرویس)
  - [Backend Service](#backend-service)
  - [Frontend Service](#frontend-service)
  - [Worker Service](#worker-service)
- [نصب و راه‌اندازی](#نصب-و-راه-اندازی)
- [مدیریت سرویس‌ها](#مدیریت-سرویس-ها)
- [نکات امنیتی](#نکات-امنیتی)

---

## نمای کلی

این فایل‌های سرویس systemd برای اجرای اپلیکیشن به‌صورت Native روی سرور Linux طراحی شده‌اند. هر سرویس:

- به‌صورت خودکار با سیستم راه‌اندازی می‌شود
- در صورت خطا، به‌صورت خودکار ری‌استارت می‌شود
- دارای محدودیت منابع (CPU, Memory) است
- دارای تنظیمات امنیتی است
- لاگ‌ها را ذخیره می‌کند

---

## پیش‌نیازها

قبل از استفاده از این سرویس‌ها:

1. **زیرساخت را راه‌اندازی کنید**:
   ```bash
   cd /workspace/infrastructure
   sudo ./setup_postgresql.sh
   sudo ./setup_redis.sh
   sudo STORAGE_DEVICE=/dev/sdX1 ./setup_storage.sh
   ```

2. **Node.js را نصب کنید**:
   ```bash
   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
   sudo apt-get install -y nodejs
   ```

3. **اپلیکیشن را build کنید**:
   ```bash
   cd /workspace/backend && npm install && npm run build
   cd /workspace/frontend && npm install && npm run build
   cd /workspace/worker && npm install && npm run build
   ```

4. **دایرکتوری لاگ ایجاد کنید**:
   ```bash
   sudo mkdir -p /var/log/app
   sudo chown www-data:www-data /var/log/app
   ```

5. **فایل‌های .env را پیکربندی کنید**:
   ```bash
   cp /workspace/.env.example /workspace/.env
   # سپس ویرایش کنید
   ```

---

## فایل‌های سرویس

### Backend Service

**مسیر**: `/etc/systemd/system/app-backend.service`

```ini
[Unit]
Description=Application Backend API Server
Documentation=https://github.com/your-repo
After=network.target postgresql.service redis-server.service
Wants=postgresql.service redis-server.service
StartLimitIntervalSec=0

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/workspace/backend

# بارگذاری متغیرهای محیطی از فایل‌ها
EnvironmentFile=/workspace/.env
EnvironmentFile=/workspace/backend/.env

# متغیرهای محیطی مستقیم
Environment="NODE_ENV=production"
Environment="POSTGRES_HOST=localhost"
Environment="REDIS_HOST=localhost"
Environment="PORT=8000"

# دستور اجرا
# اگر TypeScript build کرده‌اید:
ExecStart=/usr/bin/node /workspace/backend/dist/index.js
# اگر مستقیم از source اجرا می‌کنید:
# ExecStart=/usr/bin/node /workspace/backend/src/index.js
# اگر از PM2 استفاده می‌کنید:
# ExecStart=/usr/bin/pm2 start /workspace/backend/ecosystem.config.js --no-daemon

# ری‌استارت خودکار در صورت خطا
Restart=always
RestartSec=10
StartLimitBurst=5

# مدیریت لاگ
StandardOutput=append:/var/log/app/backend.log
StandardError=append:/var/log/app/backend-error.log
SyslogIdentifier=app-backend

# امنیت - Hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/storage /var/log/app /tmp
ProtectKernelTunables=true
ProtectControlGroups=true
RestrictRealtime=true
RestrictNamespaces=true

# محدودیت منابع
LimitNOFILE=65536
LimitNPROC=512
MemoryMax=2G
MemoryHigh=1536M
CPUQuota=200%
TasksMax=512

# Timeout ها
TimeoutStartSec=60
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
```

### Frontend Service

**مسیر**: `/etc/systemd/system/app-frontend.service`

```ini
[Unit]
Description=Application Frontend Web Server (Next.js/React)
Documentation=https://github.com/your-repo
After=network.target app-backend.service
Wants=app-backend.service
StartLimitIntervalSec=0

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/workspace/frontend

# بارگذاری متغیرهای محیطی
EnvironmentFile=/workspace/.env
EnvironmentFile=/workspace/frontend/.env.local

# متغیرهای محیطی
Environment="NODE_ENV=production"
Environment="PORT=3000"

# دستور اجرا
# برای Next.js:
ExecStart=/usr/bin/npm start
# یا اگر standalone build دارید:
# ExecStart=/usr/bin/node /workspace/frontend/.next/standalone/server.js
# برای Vite/React با serve:
# ExecStart=/usr/bin/npx serve -s /workspace/frontend/dist -l 3000

# ری‌استارت خودکار
Restart=always
RestartSec=10
StartLimitBurst=5

# مدیریت لاگ
StandardOutput=append:/var/log/app/frontend.log
StandardError=append:/var/log/app/frontend-error.log
SyslogIdentifier=app-frontend

# امنیت - Hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/log/app
ProtectKernelTunables=true
ProtectControlGroups=true
RestrictRealtime=true

# محدودیت منابع
LimitNOFILE=65536
MemoryMax=1G
MemoryHigh=768M
CPUQuota=100%
TasksMax=256

# Timeout ها
TimeoutStartSec=90
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
```

### Worker Service

**مسیر**: `/etc/systemd/system/app-worker.service`

```ini
[Unit]
Description=Application Background Worker (Job Processor)
Documentation=https://github.com/your-repo
After=network.target postgresql.service redis-server.service app-backend.service
Wants=postgresql.service redis-server.service
StartLimitIntervalSec=0

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/workspace/worker

# بارگذاری متغیرهای محیطی
EnvironmentFile=/workspace/.env
EnvironmentFile=/workspace/worker/.env

# متغیرهای محیطی
Environment="NODE_ENV=production"
Environment="POSTGRES_HOST=localhost"
Environment="REDIS_HOST=localhost"
Environment="WORKER_CONCURRENCY=5"
Environment="WORKER_MAX_RETRIES=3"

# دستور اجرا
ExecStart=/usr/bin/node /workspace/worker/dist/index.js
# یا:
# ExecStart=/usr/bin/node /workspace/worker/src/index.js

# ری‌استارت خودکار
Restart=always
RestartSec=10
StartLimitBurst=5

# مدیریت لاگ
StandardOutput=append:/var/log/app/worker.log
StandardError=append:/var/log/app/worker-error.log
SyslogIdentifier=app-worker

# امنیت - Hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/storage /var/log/app /tmp
ProtectKernelTunables=true
ProtectControlGroups=true
RestrictRealtime=true
RestrictNamespaces=true

# محدودیت منابع (Worker معمولاً منابع بیشتری نیاز دارد)
LimitNOFILE=65536
LimitNPROC=1024
MemoryMax=4G
MemoryHigh=3G
CPUQuota=400%
TasksMax=1024

# Timeout ها
TimeoutStartSec=60
TimeoutStopSec=60

[Install]
WantedBy=multi-user.target
```

---

## نصب و راه‌اندازی

### مرحله 1: کپی فایل‌های سرویس

```bash
# ایجاد فایل‌های سرویس
sudo nano /etc/systemd/system/app-backend.service
# محتوای بالا را paste کنید

sudo nano /etc/systemd/system/app-frontend.service
# محتوای بالا را paste کنید

sudo nano /etc/systemd/system/app-worker.service
# محتوای بالا را paste کنید
```

یا می‌توانید از script استفاده کنید:

```bash
# اجرای اسکریپت نصب (اگر موجود باشد)
cd /workspace/infrastructure
sudo ./install-systemd-services.sh
```

### مرحله 2: تنظیم مجوزها

```bash
# مجوزهای فایل‌های سرویس
sudo chmod 644 /etc/systemd/system/app-*.service

# مجوزهای فایل‌های اپلیکیشن
sudo chown -R www-data:www-data /workspace/backend
sudo chown -R www-data:www-data /workspace/frontend
sudo chown -R www-data:www-data /workspace/worker

# مجوزهای فایل‌های .env (محافظت از اطلاعات حساس)
sudo chmod 640 /workspace/.env
sudo chmod 640 /workspace/backend/.env
sudo chmod 640 /workspace/frontend/.env.local
sudo chmod 640 /workspace/worker/.env
sudo chown www-data:www-data /workspace/.env
sudo chown www-data:www-data /workspace/backend/.env
sudo chown www-data:www-data /workspace/frontend/.env.local
sudo chown www-data:www-data /workspace/worker/.env
```

### مرحله 3: فعال‌سازی و شروع سرویس‌ها

```bash
# بارگذاری مجدد systemd
sudo systemctl daemon-reload

# فعال‌سازی برای شروع خودکار با سیستم
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

### مرحله 4: تست و بررسی

```bash
# تست Backend API
curl http://localhost:8000/health

# تست Frontend
curl http://localhost:3000

# بررسی لاگ‌ها
sudo journalctl -u app-backend.service -f
sudo journalctl -u app-frontend.service -f
sudo journalctl -u app-worker.service -f

# یا لاگ‌های فایل
tail -f /var/log/app/backend.log
tail -f /var/log/app/frontend.log
tail -f /var/log/app/worker.log
```

---

## مدیریت سرویس‌ها

### دستورات اصلی

```bash
# شروع سرویس
sudo systemctl start app-backend.service

# متوقف کردن
sudo systemctl stop app-backend.service

# ری‌استارت
sudo systemctl restart app-backend.service

# Reload (اگر سرویس از SIGHUP پشتیبانی می‌کند)
sudo systemctl reload app-backend.service

# بررسی وضعیت
sudo systemctl status app-backend.service

# فعال‌سازی (شروع خودکار با سیستم)
sudo systemctl enable app-backend.service

# غیرفعال‌سازی
sudo systemctl disable app-backend.service

# مشاهده لاگ
sudo journalctl -u app-backend.service

# مشاهده لاگ real-time
sudo journalctl -u app-backend.service -f

# مشاهده 100 خط آخر لاگ
sudo journalctl -u app-backend.service -n 100

# لاگ‌های امروز
sudo journalctl -u app-backend.service --since today

# لاگ‌های یک ساعت گذشته
sudo journalctl -u app-backend.service --since "1 hour ago"
```

### مدیریت همه سرویس‌ها به‌صورت یکجا

```bash
# شروع همه سرویس‌ها
sudo systemctl start app-backend.service app-frontend.service app-worker.service

# ری‌استارت همه
sudo systemctl restart app-backend.service app-frontend.service app-worker.service

# وضعیت همه
systemctl status 'app-*'

# لیست تمام سرویس‌های اپلیکیشن
systemctl list-units --type=service | grep app-
```

### مشاهده منابع مصرفی

```bash
# منابع استفاده شده توسط سرویس
systemd-cgtop

# جزئیات یک سرویس خاص
systemctl show app-backend.service --property=CPUUsageNSec,MemoryCurrent

# وضعیت دقیق
systemctl status app-backend.service -l --no-pager
```

---

## نکات امنیتی

### Hardening Options در فایل‌های سرویس

فایل‌های سرویس بالا شامل تنظیمات امنیتی زیر هستند:

1. **NoNewPrivileges=true**
   - جلوگیری از افزایش مجوزها

2. **PrivateTmp=true**
   - دایرکتوری `/tmp` مجزا برای هر سرویس

3. **ProtectSystem=strict**
   - فقط مسیرهای مشخص شده قابل نوشتن هستند

4. **ProtectHome=true**
   - دسترسی به دایرکتوری‌های home محافظت شده

5. **ReadWritePaths=...**
   - فقط مسیرهای مشخص شده قابل نوشتن

6. **محدودیت منابع**:
   - `MemoryMax`: حداکثر حافظه
   - `CPUQuota`: حداکثر CPU
   - `LimitNOFILE`: حداکثر تعداد فایل‌های باز
   - `TasksMax`: حداکثر تعداد Task ها

### بررسی امنیت سرویس

```bash
# آنالیز امنیت سرویس
systemd-analyze security app-backend.service

# نمایش تنظیمات امنیتی
systemctl show app-backend.service | grep -i protect
systemctl show app-backend.service | grep -i private

# تست تنظیمات
sudo systemd-analyze verify /etc/systemd/system/app-backend.service
```

### محافظت از فایل‌های .env

```bash
# مجوزهای امن برای .env
sudo chmod 640 /workspace/.env
sudo chown www-data:www-data /workspace/.env

# جلوگیری از خواندن توسط کاربران دیگر
ls -la /workspace/.env
# باید نمایش دهد: -rw-r----- 1 www-data www-data

# Audit تغییرات
sudo auditctl -w /workspace/.env -p war -k env_file_changes
```

---

## Troubleshooting

### سرویس start نمی‌شود

```bash
# بررسی دقیق خطا
sudo systemctl status app-backend.service -l

# لاگ‌های کامل
sudo journalctl -u app-backend.service -n 200 --no-pager

# بررسی syntax فایل سرویس
sudo systemd-analyze verify /etc/systemd/system/app-backend.service

# تست اجرای دستی
cd /workspace/backend
sudo -u www-data /usr/bin/node dist/index.js
```

### سرویس بعد از مدتی متوقف می‌شود

```bash
# بررسی لاگ‌های crash
sudo journalctl -u app-backend.service --since "1 hour ago"

# بررسی محدودیت حافظه
systemctl status app-backend.service | grep Memory

# افزایش محدودیت حافظه در فایل سرویس
# MemoryMax=4G  # به جای 2G
sudo systemctl daemon-reload
sudo systemctl restart app-backend.service
```

### مشکلات مجوزها

```bash
# بررسی مجوزها
ls -la /workspace/backend
ls -la /workspace/.env
ls -la /var/log/app

# تنظیم مجدد مجوزها
sudo chown -R www-data:www-data /workspace/backend
sudo chmod -R 755 /workspace/backend
sudo chmod 640 /workspace/.env

# تست دسترسی
sudo -u www-data ls -la /workspace/backend
sudo -u www-data cat /workspace/.env
```

### اجرای دستی برای debug

```bash
# متوقف کردن سرویس
sudo systemctl stop app-backend.service

# اجرای دستی با کاربر www-data
cd /workspace/backend
sudo -u www-data bash -c 'source /workspace/.env && source /workspace/backend/.env && node dist/index.js'

# یا با متغیرهای مستقیم
sudo -u www-data \
  NODE_ENV=production \
  POSTGRES_HOST=localhost \
  node dist/index.js
```

---

## اسکریپت‌های کمکی

### اسکریپت نصب خودکار

ایجاد فایل `/workspace/infrastructure/install-systemd-services.sh`:

```bash
#!/bin/bash
set -e

echo "Installing systemd service files..."

# کپی فایل‌های سرویس
sudo cp /workspace/infrastructure/systemd/app-backend.service /etc/systemd/system/
sudo cp /workspace/infrastructure/systemd/app-frontend.service /etc/systemd/system/
sudo cp /workspace/infrastructure/systemd/app-worker.service /etc/systemd/system/

# تنظیم مجوزها
sudo chmod 644 /etc/systemd/system/app-*.service

# بارگذاری مجدد systemd
sudo systemctl daemon-reload

echo "Service files installed successfully!"
echo "To enable and start services, run:"
echo "  sudo systemctl enable app-backend.service app-frontend.service app-worker.service"
echo "  sudo systemctl start app-backend.service app-frontend.service app-worker.service"
```

### اسکریپت مدیریت سرویس‌ها

ایجاد فایل `/workspace/infrastructure/manage-services.sh`:

```bash
#!/bin/bash

SERVICES="app-backend.service app-frontend.service app-worker.service"

case "$1" in
    start)
        sudo systemctl start $SERVICES
        ;;
    stop)
        sudo systemctl stop $SERVICES
        ;;
    restart)
        sudo systemctl restart $SERVICES
        ;;
    status)
        systemctl status $SERVICES
        ;;
    logs)
        sudo journalctl -f -u app-backend.service -u app-frontend.service -u app-worker.service
        ;;
    enable)
        sudo systemctl enable $SERVICES
        ;;
    disable)
        sudo systemctl disable $SERVICES
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|enable|disable}"
        exit 1
        ;;
esac
```

استفاده:

```bash
chmod +x /workspace/infrastructure/manage-services.sh

# شروع همه سرویس‌ها
./manage-services.sh start

# مشاهده لاگ‌ها
./manage-services.sh logs

# ری‌استارت
./manage-services.sh restart
```

---

## منابع

- [systemd Service Documentation](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
- [systemd Security Features](https://www.freedesktop.org/software/systemd/man/systemd.exec.html#Sandboxing)
- [Best Practices for Writing systemd Services](https://www.digitalocean.com/community/tutorials/understanding-systemd-units-and-unit-files)

---

**نکته نهایی**: این فایل‌های سرویس برای محیط Production بهینه شده‌اند. در محیط Development ممکن است بخواهید:
- محدودیت‌های منابع را کاهش دهید
- گزینه‌های hardening را غیرفعال کنید
- سطح لاگ را افزایش دهید (`LOG_LEVEL=debug`)

**تاریخ آخرین بروزرسانی**: 2025-10-21  
**نسخه**: 1.0
