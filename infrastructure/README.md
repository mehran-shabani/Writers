# Infrastructure Setup & Deployment

این پوشه شامل اسکریپت‌های راه‌اندازی زیرساخت و فایل‌های استقرار اپلیکیشن است.

## 📁 محتویات

### فایل‌های استقرار
- **`docker-compose.yml`**: پیکربندی Docker Compose برای تمام سرویس‌ها
- **`.env.docker`**: نمونه متغیرهای محیطی برای Docker Compose
- **`docker-compose.override.yml.example`**: نمونه override برای محیط Development
- **`DEPLOYMENT.md`**: راهنمای کامل استقرار (Docker Compose + systemd)
- **`SYSTEMD_SERVICES.md`**: راهنمای جزئیات سرویس‌های systemd

### اسکریپت‌های راه‌اندازی زیرساخت

### 1. PostgreSQL Setup (`setup_postgresql.sh`)

نصب و پیکربندی PostgreSQL روی درایو SSD مجزا.

**ویژگی‌ها:**
- نصب PostgreSQL با قابلیت انتخاب نسخه
- پیکربندی دایرکتوری داده روی SSD
- تنظیمات بهینه‌سازی برای SSD
- پیکربندی امنیتی اولیه

**استفاده:**
```bash
# با تنظیمات پیش‌فرض (SSD در /mnt/ssd)
sudo ./setup_postgresql.sh

# با مسیر سفارشی
sudo SSD_MOUNT_POINT=/mnt/my-ssd PG_VERSION=15 ./setup_postgresql.sh
```

**متغیرهای محیطی:**
- `SSD_MOUNT_POINT`: مسیر mount نقطه SSD (پیش‌فرض: `/mnt/ssd`)
- `PG_DATA_DIR`: مسیر دایرکتوری داده PostgreSQL (پیش‌فرض: `$SSD_MOUNT_POINT/postgresql/data`)
- `PG_VERSION`: نسخه PostgreSQL (پیش‌فرض: `15`)
- `PG_PORT`: پورت PostgreSQL (پیش‌فرض: `5432`)

---

### 2. Storage Setup (`setup_storage.sh`)

پیکربندی mount پایدار فضای ذخیره‌سازی ۱۰۰ ترابایتی به `/storage`.

**ویژگی‌ها:**
- Mount پایدار با استفاده از UUID در `/etc/fstab`
- ایجاد زیردایرکتوری‌های `uploads/` و `results/`
- تنظیم مجوزهای دسترسی مناسب
- فرمت‌کردن اختیاری دیسک

**استفاده:**
```bash
# نمایش دستگاه‌های موجود
lsblk

# اجرای اسکریپت با مشخص کردن دستگاه
sudo STORAGE_DEVICE=/dev/sdb1 ./setup_storage.sh

# با filesystem سفارشی
sudo STORAGE_DEVICE=/dev/sdb1 FS_TYPE=xfs ./setup_storage.sh
```

**متغیرهای محیطی:**
- `STORAGE_DEVICE`: دستگاه بلاکی برای mount (مثال: `/dev/sdb1`)
- `FS_TYPE`: نوع فایل سیستم (پیش‌فرض: `ext4`)

**ساختار دایرکتوری:**
```
/storage/
├── uploads/    (owner: www-data, mode: 755, sticky bit)
└── results/    (owner: root, mode: 755)
```

---

### 3. Redis Setup (`setup_redis.sh`)

نصب و پیکربندی Redis با تنظیمات امنیتی پایه.

**ویژگی‌ها:**
- نصب Redis Server
- پیکربندی رمز عبور تصادفی امن
- Bind به localhost فقط
- غیرفعال‌سازی دستورات خطرناک (FLUSHDB, FLUSHALL)
- تنظیمات بهینه‌سازی حافظه

**استفاده:**
```bash
# با تنظیمات پیش‌فرض
sudo ./setup_redis.sh

# با تنظیمات سفارشی
sudo REDIS_PORT=6380 REDIS_PASSWORD="my-secure-password" ./setup_redis.sh
```

**متغیرهای محیطی:**
- `REDIS_PORT`: پورت Redis (پیش‌فرض: `6379`)
- `REDIS_PASSWORD`: رمز عبور (پیش‌فرض: رمز تصادفی امن)
- `REDIS_BIND_ADDRESS`: آدرس bind (پیش‌فرض: `127.0.0.1`)
- `REDIS_MAXMEMORY`: حداکثر حافظه (پیش‌فرض: `256mb`)
- `REDIS_MAXMEMORY_POLICY`: سیاست پاک‌سازی (پیش‌فرض: `allkeys-lru`)

**پس از نصب:**
رمز عبور در فایل `/etc/redis/redis-password.txt` ذخیره می‌شود.

**اتصال به Redis:**
```bash
redis-cli -a $(cat /etc/redis/redis-password.txt)
```

---

## نیازمندی‌ها

- سیستم‌عامل: Ubuntu/Debian
- دسترسی root (sudo)
- اتصال به اینترنت برای دانلود بسته‌ها

## نکات امنیتی

1. **PostgreSQL**: 
   - فقط از طریق localhost قابل دسترسی است
   - استفاده از احراز هویت `scram-sha-256`
   
2. **Redis**:
   - Bind به localhost فقط
   - رمز عبور الزامی
   - دستورات خطرناک غیرفعال شده
   
3. **Storage**:
   - مجوزهای دسترسی محدود
   - Sticky bit برای دایرکتوری uploads

## عیب‌یابی

### PostgreSQL
```bash
# بررسی وضعیت
sudo systemctl status postgresql

# مشاهده لاگ‌ها
sudo journalctl -u postgresql -n 50

# اتصال آزمایشی
sudo -u postgres psql
```

### Redis
```bash
# بررسی وضعیت
sudo systemctl status redis-server

# مشاهده لاگ‌ها
sudo tail -f /var/log/redis/redis-server.log

# تست اتصال
redis-cli -a $(sudo cat /etc/redis/redis-password.txt) PING
```

### Storage
```bash
# بررسی mount
mountpoint /storage
df -h /storage

# بررسی fstab
cat /etc/fstab | grep storage
```

## پشتیبان‌گیری

همه اسکریپت‌ها قبل از تغییرات، backup از فایل‌های پیکربندی می‌گیرند:
- PostgreSQL config: `postgresql.conf.backup`
- Redis config: `redis.conf.backup.YYYYMMDD_HHMMSS`
- fstab: `fstab.backup.YYYYMMDD_HHMMSS`

---

## 🚀 استقرار اپلیکیشن

برای استقرار کامل اپلیکیشن، دو روش در دسترس است:

### روش 1: استقرار با Docker Compose (توصیه شده)

```bash
# 1. آماده‌سازی محیط
cd /workspace/infrastructure
cp .env.docker .env
nano .env  # ویرایش و تنظیم رمزها

# 2. راه‌اندازی زیرساخت (اگر هنوز انجام نشده)
sudo ./setup_postgresql.sh
sudo ./setup_redis.sh
sudo STORAGE_DEVICE=/dev/sdX1 ./setup_storage.sh

# 3. اجرای سرویس‌ها
docker compose up -d

# 4. بررسی وضعیت
docker compose ps
docker compose logs -f
```

### روش 2: استقرار مستقیم با systemd

```bash
# 1. نصب وابستگی‌ها
sudo ./setup_postgresql.sh
sudo ./setup_redis.sh
sudo STORAGE_DEVICE=/dev/sdX1 ./setup_storage.sh

# 2. Build اپلیکیشن
cd /workspace/backend && npm install && npm run build
cd /workspace/frontend && npm install && npm run build
cd /workspace/worker && npm install && npm run build

# 3. نصب سرویس‌های systemd (مراجعه به SYSTEMD_SERVICES.md)
sudo nano /etc/systemd/system/app-backend.service
sudo nano /etc/systemd/system/app-frontend.service
sudo nano /etc/systemd/system/app-worker.service

# 4. فعال‌سازی و شروع
sudo systemctl daemon-reload
sudo systemctl enable app-backend.service app-frontend.service app-worker.service
sudo systemctl start app-backend.service app-frontend.service app-worker.service
```

**📖 مستندات کامل**: برای جزئیات بیشتر، فایل **[DEPLOYMENT.md](DEPLOYMENT.md)** را مطالعه کنید.

---

## 📚 مستندات مرتبط

- **[DEPLOYMENT.md](DEPLOYMENT.md)**: راهنمای کامل استقرار با هر دو روش
- **[SYSTEMD_SERVICES.md](SYSTEMD_SERVICES.md)**: جزئیات کامل سرویس‌های systemd
- **[../ENV_SETUP.md](../ENV_SETUP.md)**: راهنمای پیکربندی متغیرهای محیطی
- **[../.env.example](../.env.example)**: نمونه متغیرهای محیطی سراسری
