# راهنمای شروع سریع (Quick Start)

این راهنما برای راه‌اندازی سریع اپلیکیشن با Docker Compose است.

---

## ⚡ شروع سریع با اسکریپت خودکار

```bash
cd /workspace/infrastructure
chmod +x quick-start-docker.sh
./quick-start-docker.sh
```

این اسکریپت به‌صورت خودکار:
- ✅ Docker و Docker Compose را بررسی می‌کند
- ✅ فایل‌های `.env` را ایجاد می‌کند
- ✅ دایرکتوری‌های مورد نیاز را می‌سازد
- ✅ Image ها را build می‌کند
- ✅ تمام سرویس‌ها را اجرا می‌کند
- ✅ سلامت سرویس‌ها را تست می‌کند

---

## 📝 مراحل دستی

اگر ترجیح می‌دهید مراحل را به‌صورت دستی انجام دهید:

### مرحله 1: پیکربندی متغیرهای محیطی

```bash
# ریشه پروژه
cd /workspace
cp .env.example .env
nano .env  # ویرایش و تنظیم رمزها

# Infrastructure
cd infrastructure
cp .env.docker .env
nano .env  # تنظیم رمزهای امن
```

**حتماً این مقادیر را تغییر دهید:**
- `POSTGRES_PASSWORD`
- `REDIS_PASSWORD`
- `JWT_SECRET`
- `JWT_REFRESH_SECRET`
- `SESSION_SECRET`

**برای تولید رمز امن:**
```bash
openssl rand -base64 48
```

### مرحله 2: آماده‌سازی زیرساخت

اگر سرور جدید است:

```bash
cd /workspace/infrastructure

# PostgreSQL روی SSD
sudo ./setup_postgresql.sh

# Redis
sudo ./setup_redis.sh

# Storage (فضای ذخیره‌سازی 100TB)
# ابتدا device را شناسایی کنید: lsblk
sudo STORAGE_DEVICE=/dev/sdX1 ./setup_storage.sh
```

### مرحله 3: اجرای Docker Compose

```bash
cd /workspace/infrastructure

# Build و اجرا
docker compose build
docker compose up -d

# بررسی وضعیت
docker compose ps

# مشاهده لاگ‌ها
docker compose logs -f
```

### مرحله 4: تست

```bash
# PostgreSQL
docker compose exec postgres psql -U myapp_user -d myapp_db -c "SELECT version();"

# Redis
docker compose exec redis redis-cli -a YOUR_PASSWORD ping

# Backend API
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000
```

---

## 🎯 دسترسی به سرویس‌ها

پس از راه‌اندازی موفق:

| سرویس | URL | توضیحات |
|-------|-----|---------|
| Frontend | http://localhost:3000 | رابط کاربری وب |
| Backend API | http://localhost:8000 | API سرور |
| PostgreSQL | localhost:5432 | فقط در Docker network |
| Redis | localhost:6379 | فقط در Docker network |

---

## 🛠️ دستورات مفید

### مدیریت سرویس‌ها

```bash
# مشاهده وضعیت
docker compose ps

# مشاهده لاگ‌ها
docker compose logs -f

# لاگ یک سرویس خاص
docker compose logs -f backend

# ری‌استارت یک سرویس
docker compose restart backend

# ری‌استارت همه
docker compose restart

# متوقف کردن
docker compose stop

# حذف سرویس‌ها (داده‌ها حفظ می‌شود)
docker compose down

# حذف با volume ها (خطرناک - تمام داده‌ها پاک می‌شود!)
docker compose down -v
```

### مانیتورینگ

```bash
# منابع مصرفی
docker stats

# فضای دیسک استفاده شده
docker system df

# بررسی health
docker compose ps

# دسترسی به shell یک container
docker compose exec backend sh
docker compose exec postgres psql -U myapp_user -d myapp_db
```

### Scale کردن Worker

```bash
# اجرای 3 instance از worker
docker compose up -d --scale worker=3

# بررسی
docker compose ps worker
```

---

## 🐛 عیب‌یابی

### سرویس start نمی‌شود

```bash
# بررسی لاگ‌های دقیق
docker compose logs backend

# بررسی وضعیت
docker compose ps

# ری‌استارت با build مجدد
docker compose down
docker compose build --no-cache
docker compose up -d
```

### خطای اتصال به Database

```bash
# بررسی health PostgreSQL
docker compose exec postgres pg_isready

# بررسی متغیرهای محیطی
docker compose exec backend env | grep POSTGRES

# اتصال مستقیم
docker compose exec postgres psql -U myapp_user -d myapp_db
```

### فضای دیسک پر شده

```bash
# پاک‌سازی image ها و container های قدیمی
docker system prune -a

# حذف volume های استفاده نشده (احتیاط!)
docker volume prune
```

### Port در حال استفاده است

```bash
# پیدا کردن process
sudo lsof -i :8000

# یا تغییر port در .env
BACKEND_PORT=8001
docker compose up -d
```

---

## 🔒 نکات امنیتی

### ✅ انجام دهید:

1. **رمزهای قوی استفاده کنید**
   ```bash
   openssl rand -base64 48
   ```

2. **فایل‌های .env را commit نکنید**
   ```bash
   # بررسی قبل از commit
   git status
   ```

3. **برای production از firewall استفاده کنید**
   ```bash
   # فقط port های لازم را باز کنید
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

4. **بروزرسانی منظم**
   ```bash
   docker compose pull
   docker compose up -d
   ```

### ❌ انجام ندهید:

- ❌ رمزهای پیش‌فرض را استفاده نکنید
- ❌ پورت‌های database را به اینترنت expose نکنید
- ❌ بدون backup تغییرات مهم ندهید

---

## 📚 منابع بیشتر

- **[DEPLOYMENT.md](DEPLOYMENT.md)**: راهنمای کامل استقرار
- **[SYSTEMD_SERVICES.md](SYSTEMD_SERVICES.md)**: جایگزین systemd
- **[../ENV_SETUP.md](../ENV_SETUP.md)**: راهنمای متغیرهای محیطی
- **[README.md](README.md)**: اطلاعات کلی infrastructure

---

## 🆘 نیاز به کمک؟

اگر مشکلی داشتید:

1. لاگ‌ها را بررسی کنید: `docker compose logs -f`
2. مستندات کامل را بخوانید: `cat DEPLOYMENT.md`
3. سرویس‌ها را ری‌استارت کنید: `docker compose restart`
4. با تیم توسعه تماس بگیرید

---

**موفق باشید! 🚀**
