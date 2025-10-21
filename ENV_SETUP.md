# راهنمای پیکربندی متغیرهای محیطی (Environment Variables Setup Guide)

## 📋 فهرست

1. [نمای کلی](#نمای-کلی)
2. [ساختار پروژه](#ساختار-پروژه)
3. [راهنمای نصب سریع](#راهنمای-نصب-سریع)
4. [متغیرهای سراسری](#متغیرهای-سراسری)
5. [متغیرهای اختصاصی هر سرویس](#متغیرهای-اختصاصی-هر-سرویس)
6. [نکات امنیتی](#نکات-امنیتی)
7. [محیط‌های مختلف](#محیط-های-مختلف)

---

## 🌟 نمای کلی

این پروژه از یک ساختار ماژولار برای مدیریت متغیرهای محیطی استفاده می‌کند. هر سرویس (`frontend`, `backend`, `worker`) فایل `.env` مخصوص خود را دارد که از متغیرهای سراسری مشترک استفاده می‌کند.

## 📁 ساختار پروژه

```
/workspace/
├── .env.example              # متغیرهای سراسری مشترک (الگو)
├── .gitignore                # فایل‌های .env واقعی را نادیده می‌گیرد
├── frontend/
│   └── .env.local            # متغیرهای اختصاصی فرانت‌اند (الگو)
├── backend/
│   └── .env                  # متغیرهای اختصاصی بک‌اند (الگو)
├── worker/
│   └── .env                  # متغیرهای اختصاصی Worker (الگو)
└── infrastructure/
    └── (فایل‌های زیرساخت و دیپلوی)
```

## 🚀 راهنمای نصب سریع

### مرحله ۱: ایجاد فایل‌های محیطی واقعی

#### در ریشه پروژه:
```bash
# کپی فایل الگو به فایل واقعی
cp .env.example .env

# ویرایش و تنظیم مقادیر واقعی
nano .env  # یا vim، code، etc.
```

#### برای Frontend:
```bash
cd frontend
cp .env.local .env.local.real  # یا فقط ویرایش .env.local
# برای Next.js: فایل .env.local به‌صورت پیش‌فرض استفاده می‌شود
# برای Vite: نام فایل را به .env تغییر دهید
nano .env.local
cd ..
```

#### برای Backend:
```bash
cd backend
cp .env .env.real  # یا فقط مقادیر را در .env پر کنید
nano .env
cd ..
```

#### برای Worker:
```bash
cd worker
cp .env .env.real  # یا فقط مقادیر را در .env پر کنید
nano .env
cd ..
```

### مرحله ۲: تنظیم متغیرهای اصلی

#### متغیرهای ضروری که باید حتماً تنظیم شوند:

```bash
# در فایل .env ریشه پروژه
POSTGRES_PASSWORD=your_secure_password_here
REDIS_PASSWORD=your_redis_password_here
JWT_SECRET=your_very_long_random_jwt_secret_minimum_32_chars
JWT_REFRESH_SECRET=your_very_long_random_refresh_secret_minimum_32_chars
SESSION_SECRET=your_session_secret_minimum_32_chars
```

#### تولید رمزهای امن:

```bash
# تولید رمز تصادفی با OpenSSL
openssl rand -base64 32

# تولید رمز تصادفی با Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"

# تولید رمز تصادفی با Python
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### مرحله ۳: تأیید پیکربندی

```bash
# بررسی اینکه فایل‌های .env واقعی ایجاد شده‌اند
ls -la .env
ls -la frontend/.env.local
ls -la backend/.env
ls -la worker/.env

# بررسی اینکه فایل‌های .env در .gitignore قرار دارند
cat .gitignore | grep .env
```

## 🌐 متغیرهای سراسری

فایل `.env.example` در ریشه پروژه شامل متغیرهای مشترک است:

### پایگاه داده (PostgreSQL)
- `POSTGRES_HOST`: آدرس سرور پایگاه داده
- `POSTGRES_PORT`: پورت پایگاه داده (پیش‌فرض: 5432)
- `POSTGRES_DB`: نام دیتابیس
- `POSTGRES_USER`: نام کاربری
- `POSTGRES_PASSWORD`: رمز عبور

### Redis
- `REDIS_URL`: آدرس اتصال Redis
- `REDIS_PASSWORD`: رمز عبور Redis
- `REDIS_CACHE_DB`, `REDIS_SESSION_DB`, `REDIS_QUEUE_DB`: شماره دیتابیس‌های مختلف

### ذخیره‌سازی فایل
- `STORAGE_ROOT`: مسیر ریشه ذخیره‌سازی
- `STORAGE_TYPE`: نوع ذخیره‌سازی (local, s3, gcs)
- `S3_*`: تنظیمات S3/Object Storage

### امنیت
- `JWT_SECRET`: کلید مخفی JWT
- `JWT_EXPIRATION`: مدت اعتبار توکن
- `SESSION_SECRET`: کلید مخفی Session
- `CORS_ORIGINS`: منابع مجاز CORS

## 🔧 متغیرهای اختصاصی هر سرویس

### Frontend (`frontend/.env.local`)

**متغیرهای عمومی (در مرورگر قابل دسترسی):**
- `NEXT_PUBLIC_API_URL` یا `VITE_API_URL`: آدرس API
- `NEXT_PUBLIC_APP_URL` یا `VITE_APP_URL`: آدرس اپلیکیشن
- `NEXT_PUBLIC_ANALYTICS_ID`: شناسه Analytics

**نکته مهم:** 
- فقط متغیرهای با پیشوند `NEXT_PUBLIC_` (Next.js) یا `VITE_` (Vite) در مرورگر قابل دسترسی هستند
- هیچ‌گاه اطلاعات حساس را با این پیشوندها قرار ندهید

### Backend (`backend/.env`)

**تنظیمات سرور:**
- `PORT`: پورت سرور (پیش‌فرض: 8000)
- `HOST`: آدرس هاست (پیش‌فرض: 0.0.0.0)
- `API_PREFIX`: پیشوند API (مثال: /api)

**احراز هویت:**
- همه متغیرهای JWT و Session از فایل سراسری
- تنظیمات اضافی CORS و Rate Limiting

**آپلود فایل:**
- `UPLOAD_MAX_FILE_SIZE`: حداکثر حجم فایل
- `UPLOAD_ALLOWED_TYPES`: انواع فایل مجاز

### Worker (`worker/.env`)

**تنظیمات Worker:**
- `WORKER_CONCURRENCY`: تعداد Job های همزمان
- `WORKER_MAX_RETRIES`: حداکثر تلاش مجدد
- `QUEUES`: لیست صف‌های قابل پردازش

**Job های برنامه‌ریزی شده:**
- `CRON_*`: تعریف Job های Cron
- `CRON_ENABLED`: فعال/غیرفعال سازی Cron

## 🔒 نکات امنیتی

### ✅ انجام دهید:

1. **هیچ‌گاه فایل‌های `.env` واقعی را commit نکنید**
   ```bash
   # بررسی قبل از commit
   git status
   # اگر .env در لیست بود:
   git reset HEAD .env
   ```

2. **رمزهای قوی استفاده کنید**
   - حداقل 32 کاراکتر برای JWT_SECRET
   - استفاده از حروف، اعداد و کاراکترهای خاص
   - از ژنراتورهای رمز تصادفی استفاده کنید

3. **رمزها را به‌صورت دوره‌ای تغییر دهید**
   - هر 3-6 ماه یک بار
   - بلافاصله پس از مشکوک بودن به نشت

4. **برای محیط‌های مختلف از رمزهای متفاوت استفاده کنید**
   - Development ≠ Staging ≠ Production
   - هیچ‌گاه رمزهای Production را در Development استفاده نکنید

5. **از Vault برای Production استفاده کنید**
   - AWS Secrets Manager
   - HashiCorp Vault
   - Azure Key Vault
   - Google Secret Manager

### ❌ انجام ندهید:

1. ❌ فایل‌های `.env` را commit نکنید
2. ❌ رمزها را در کد هاردکد نکنید
3. ❌ اطلاعات حساس را در لاگ‌ها ذخیره نکنید
4. ❌ متغیرهای حساس را با `NEXT_PUBLIC_` یا `VITE_` شروع نکنید
5. ❌ رمزهای پیش‌فرض را در Production استفاده نکنید

## 🌍 محیط‌های مختلف

### Development (توسعه)

```bash
NODE_ENV=development
APP_ENV=development

# می‌توانید از سرویس‌های محلی استفاده کنید
POSTGRES_HOST=localhost
REDIS_URL=redis://localhost:6379

# لاگ‌های بیشتر
LOG_LEVEL=debug
```

### Staging (تست)

```bash
NODE_ENV=staging
APP_ENV=staging

# از سرورهای تست استفاده کنید
POSTGRES_HOST=staging-db.example.com
REDIS_URL=redis://staging-redis.example.com:6379

# لاگ متوسط
LOG_LEVEL=info
```

### Production (محصول)

```bash
NODE_ENV=production
APP_ENV=production

# از سرورهای تولید امن استفاده کنید
POSTGRES_HOST=prod-db.example.com
REDIS_URL=redis://prod-redis.example.com:6379

# فقط لاگ‌های مهم
LOG_LEVEL=warn

# فعال‌سازی ویژگی‌های امنیتی
SESSION_COOKIE_SECURE=true
SENTRY_DSN=your_sentry_dsn
```

## 📝 مثال استفاده در کد

### Backend (Node.js/Express)

```javascript
// config/database.js
require('dotenv').config();

module.exports = {
  host: process.env.POSTGRES_HOST,
  port: process.env.POSTGRES_PORT,
  database: process.env.POSTGRES_DB,
  username: process.env.POSTGRES_USER,
  password: process.env.POSTGRES_PASSWORD,
};
```

### Frontend (Next.js)

```javascript
// config/api.js
export const API_URL = process.env.NEXT_PUBLIC_API_URL;
export const APP_URL = process.env.NEXT_PUBLIC_APP_URL;
```

### Worker (Node.js)

```javascript
// config/queue.js
require('dotenv').config();

module.exports = {
  redis: {
    url: process.env.REDIS_URL,
    password: process.env.REDIS_PASSWORD,
    db: process.env.REDIS_QUEUE_DB,
  },
  concurrency: parseInt(process.env.WORKER_CONCURRENCY, 10),
};
```

## 🆘 عیب‌یابی

### مشکل: متغیرها بارگذاری نمی‌شوند

```bash
# بررسی مسیر فایل .env
ls -la .env

# بررسی محتوای فایل
cat .env | grep -v '^#' | grep -v '^$'

# اطمینان از بارگذاری dotenv
# در Node.js:
require('dotenv').config({ path: '.env' });
```

### مشکل: CORS Error در Frontend

```bash
# در backend/.env بررسی کنید:
CORS_ORIGINS=http://localhost:3000

# اگر Frontend در پورت دیگری است:
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### مشکل: اتصال به Database ناموفق است

```bash
# بررسی اطلاعات اتصال
echo "postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_HOST:$POSTGRES_PORT/$POSTGRES_DB"

# تست اتصال
psql "postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_HOST:$POSTGRES_PORT/$POSTGRES_DB"
```

## 📚 منابع بیشتر

- [The Twelve-Factor App - Config](https://12factor.net/config)
- [dotenv Documentation](https://github.com/motdotla/dotenv)
- [OWASP - Secure Configuration](https://owasp.org/www-project-secure-coding-practices/)

---

**تهیه شده برای پروژه ماژولار با معماری Microservices**
