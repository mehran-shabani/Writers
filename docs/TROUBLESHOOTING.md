# راهنمای عیب‌یابی

این سند راهنمای حل مشکلات رایج در سیستم Writers را ارائه می‌دهد.

## 🔍 فهرست مشکلات

- [مشکلات Backend](#مشکلات-backend)
- [مشکلات Frontend](#مشکلات-frontend)
- [مشکلات Worker](#مشکلات-worker)
- [مشکلات Database](#مشکلات-database)
- [مشکلات Redis](#مشکلات-redis)
- [مشکلات Nginx](#مشکلات-nginx)
- [مشکلات Docker](#مشکلات-docker)
- [مشکلات Performance](#مشکلات-performance)

---

## 🐍 مشکلات Backend

### مشکل: Backend اجرا نمی‌شود

**علائم:**
```
ERROR: Could not find a version that satisfies the requirement...
```

**راه‌حل:**
```bash
# به‌روزرسانی pip
pip install --upgrade pip

# نصب مجدد dependencies
pip install -r requirements.txt --force-reinstall

# بررسی نسخه Python
python --version  # باید 3.10+ باشد
```

---

### مشکل: خطای اتصال به Database

**علائم:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**راه‌حل:**

1. بررسی اجرای PostgreSQL:
```bash
sudo systemctl status postgresql
sudo systemctl start postgresql
```

2. بررسی connection string در `.env`:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

3. تست اتصال:
```bash
psql -U writers_user -d writers_db -c "SELECT 1;"
```

4. بررسی firewall:
```bash
sudo ufw status
sudo ufw allow 5432/tcp
```

---

### مشکل: خطای Migration

**علائم:**
```
alembic.util.exc.CommandError: Can't locate revision identified by 'xxx'
```

**راه‌حل:**

1. بررسی وضعیت فعلی:
```bash
alembic current
alembic history
```

2. Stamp کردن به آخرین revision:
```bash
alembic stamp head
```

3. اگر مشکل حل نشد، reset کامل:
```bash
# ⚠️ خطرناک - تمام داده‌ها حذف می‌شوند
alembic downgrade base
alembic upgrade head
```

---

### مشکل: خطای JWT Token

**علائم:**
```
JWTError: Signature verification failed
```

**راه‌حل:**

1. بررسی SECRET_KEY در `.env`:
```bash
# تولید SECRET_KEY جدید
openssl rand -hex 32
```

2. اطمینان از یکسان بودن SECRET_KEY در تمام سرویس‌ها

3. پاک کردن cookies مرورگر و login مجدد

---

### مشکل: Celery Task اجرا نمی‌شود

**علائم:**
```
Task never executed
```

**راه‌حل:**

1. بررسی اجرای Worker:
```bash
ps aux | grep celery
```

2. بررسی اتصال Redis:
```bash
redis-cli ping
```

3. بررسی logs Worker:
```bash
sudo journalctl -u writers-worker -f
```

4. اجرای Worker با debug mode:
```bash
celery -A tasks worker --loglevel=debug
```

---

## ⚛️ مشکلات Frontend

### مشکل: npm install شکست می‌خورد

**علائم:**
```
npm ERR! code ERESOLVE
```

**راه‌حل:**

1. پاک کردن cache:
```bash
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

2. استفاده از --legacy-peer-deps:
```bash
npm install --legacy-peer-deps
```

3. بررسی نسخه Node.js:
```bash
node --version  # باید 18+ باشد
nvm use 20
```

---

### مشکل: خطای Build

**علائم:**
```
Error: Build failed
```

**راه‌حل:**

1. بررسی خطاهای TypeScript:
```bash
npx tsc --noEmit
```

2. پاک کردن cache Next.js:
```bash
rm -rf .next
npm run build
```

3. بررسی Environment Variables:
```bash
cat .env.local
# اطمینان از وجود NEXT_PUBLIC_API_URL
```

---

### مشکل: API calls موفق نیستند

**علائم:**
```
Network Error / CORS Error
```

**راه‌حل:**

1. بررسی اجرای Backend:
```bash
curl http://localhost:8000/health
```

2. بررسی CORS در Backend:
```python
# در backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

3. بررسی proxy در Next.js:
```typescript
// بررسی app/api/[endpoint]/route.ts
```

---

### مشکل: Authentication کار نمی‌کند

**علائم:**
```
401 Unauthorized
```

**راه‌حل:**

1. بررسی cookies:
```javascript
// در Browser Console
document.cookie
```

2. بررسی withCredentials:
```typescript
// در lib/api.ts
axios.create({
  withCredentials: true,
});
```

3. پاک کردن cookies و login مجدد:
```javascript
// در Browser Console
document.cookie.split(";").forEach(c => {
  document.cookie = c.trim().split("=")[0] + '=;expires=Thu, 01 Jan 1970 00:00:00 UTC;';
});
```

---

## 🔄 مشکلات Worker

### مشکل: Worker متوقف می‌شود

**علائم:**
```
Worker shutdown
```

**راه‌حل:**

1. بررسی Memory:
```bash
free -h
# اگر کم است، افزایش swap
```

2. بررسی logs:
```bash
sudo journalctl -u writers-worker -n 100
```

3. راه‌اندازی مجدد با تنظیمات مناسب:
```bash
celery -A tasks worker --loglevel=info --max-tasks-per-child=1000
```

---

### مشکل: Tasks در Queue می‌مانند

**علائم:**
```
Tasks pending but not executing
```

**راه‌حل:**

1. بررسی تعداد Workers:
```bash
celery -A tasks inspect active
```

2. افزایش concurrency:
```bash
celery -A tasks worker --concurrency=8
```

3. بررسی Redis Queue:
```bash
redis-cli
> LLEN celery
> KEYS celery*
```

4. پاک کردن Queue (اگر لازم باشد):
```bash
celery -A tasks purge
```

---

## 🗄️ مشکلات Database

### مشکل: Database پر است

**علائم:**
```
FATAL: could not write to file: No space left on device
```

**راه‌حل:**

1. بررسی فضای دیسک:
```bash
df -h
```

2. بررسی حجم Database:
```sql
SELECT pg_size_pretty(pg_database_size('writers_db'));
```

3. پاکسازی logs قدیمی:
```sql
-- حذف رکوردهای قدیمی (مثال)
DELETE FROM tasks WHERE created_at < NOW() - INTERVAL '6 months';
```

4. اجرای VACUUM:
```sql
VACUUM FULL;
ANALYZE;
```

---

### مشکل: Slow Queries

**علائم:**
```
Queries taking too long
```

**راه‌حل:**

1. فعال‌سازی slow query log:
```sql
ALTER SYSTEM SET log_min_duration_statement = 1000;
SELECT pg_reload_conf();
```

2. بررسی query plan:
```sql
EXPLAIN ANALYZE SELECT * FROM tasks WHERE owner_id = 1;
```

3. اضافه کردن Index:
```sql
CREATE INDEX idx_tasks_owner_id ON tasks(owner_id);
```

4. بررسی و بهینه‌سازی:
```sql
-- بررسی indexes استفاده نشده
SELECT * FROM pg_stat_user_indexes WHERE idx_scan = 0;

-- آمار جداول
SELECT * FROM pg_stat_user_tables;
```

---

### مشکل: Too Many Connections

**علائم:**
```
FATAL: sorry, too many clients already
```

**راه‌حل:**

1. بررسی connection count:
```sql
SELECT count(*) FROM pg_stat_activity;
```

2. افزایش max_connections:
```bash
sudo nano /etc/postgresql/15/main/postgresql.conf
# max_connections = 200
sudo systemctl restart postgresql
```

3. بررسی connection leaks در کد:
```python
# اطمینان از استفاده صحیح از context manager
with get_db() as session:
    # queries
    pass
```

---

## 🔴 مشکلات Redis

### مشکل: Redis متوقف می‌شود

**علائم:**
```
Could not connect to Redis
```

**راه‌حل:**

1. بررسی وضعیت:
```bash
sudo systemctl status redis-server
sudo systemctl start redis-server
```

2. بررسی logs:
```bash
sudo tail -f /var/log/redis/redis-server.log
```

3. بررسی memory:
```bash
redis-cli INFO memory
```

---

### مشکل: Redis Memory Full

**علائم:**
```
OOM command not allowed when used memory > 'maxmemory'
```

**راه‌حل:**

1. افزایش maxmemory:
```bash
sudo nano /etc/redis/redis.conf
# maxmemory 1gb
sudo systemctl restart redis-server
```

2. تنظیم eviction policy:
```conf
maxmemory-policy allkeys-lru
```

3. پاک کردن keys غیرضروری:
```bash
redis-cli
> FLUSHDB  # ⚠️ همه keys حذف می‌شوند
```

---

## 🌐 مشکلات Nginx

### مشکل: 502 Bad Gateway

**علائم:**
```
502 Bad Gateway
```

**راه‌حل:**

1. بررسی اجرای Backend:
```bash
curl http://localhost:8000/health
```

2. بررسی Nginx config:
```bash
sudo nginx -t
```

3. بررسی logs:
```bash
sudo tail -f /var/log/nginx/error.log
```

4. راه‌اندازی مجدد:
```bash
sudo systemctl restart nginx
```

---

### مشکل: SSL Certificate Error

**علائم:**
```
SSL certificate problem
```

**راه‌حل:**

1. تمدید certificate:
```bash
sudo certbot renew
```

2. تست پیکربندی:
```bash
sudo certbot renew --dry-run
```

3. بررسی تاریخ انقضا:
```bash
echo | openssl s_client -servername yourdomain.com -connect yourdomain.com:443 2>/dev/null | openssl x509 -noout -dates
```

---

### مشکل: Rate Limiting

**علائم:**
```
429 Too Many Requests
```

**راه‌حل:**

1. افزایش rate limit:
```nginx
# در nginx.conf
limit_req_zone $binary_remote_addr zone=api:10m rate=20r/s;
```

2. Whitelist کردن IP خاص:
```nginx
geo $limit {
    default 1;
    192.168.1.0/24 0;  # Whitelist
}
```

---

## 🐳 مشکلات Docker

### مشکل: Container شروع نمی‌شود

**علائم:**
```
Error starting container
```

**راه‌حل:**

1. بررسی logs:
```bash
docker-compose logs backend
```

2. بررسی health check:
```bash
docker-compose ps
```

3. راه‌اندازی مجدد:
```bash
docker-compose down
docker-compose up -d
```

4. پاک کردن volumes:
```bash
docker-compose down -v
docker-compose up -d
```

---

### مشکل: Out of Disk Space

**علائم:**
```
no space left on device
```

**راه‌حل:**

1. بررسی فضا:
```bash
df -h
docker system df
```

2. پاکسازی:
```bash
# حذف containers متوقف شده
docker container prune

# حذف images استفاده نشده
docker image prune -a

# حذف volumes
docker volume prune

# پاکسازی کامل
docker system prune -a --volumes
```

---

### مشکل: Network Issues

**علائم:**
```
Could not connect to service
```

**راه‌حل:**

1. بررسی networks:
```bash
docker network ls
docker network inspect app-network
```

2. ایجاد مجدد network:
```bash
docker network rm app-network
docker network create app-network
```

3. restart containers:
```bash
docker-compose restart
```

---

## ⚡ مشکلات Performance

### مشکل: High CPU Usage

**راه‌حل:**

1. بررسی process‌ها:
```bash
top
htop
```

2. بررسی Workers:
```bash
# کاهش تعداد workers
# در systemd service file یا docker-compose
```

3. افزایش سخت‌افزار یا horizontal scaling

---

### مشکل: High Memory Usage

**راه‌حل:**

1. بررسی memory:
```bash
free -h
ps aux --sort=-%mem | head
```

2. تنظیم memory limits:
```yaml
# در docker-compose.yml
services:
  backend:
    mem_limit: 2g
```

3. بهینه‌سازی queries و cache

---

### مشکل: Slow Response Time

**راه‌حل:**

1. فعال‌سازی caching:
```python
# استفاده از Redis cache
@cache.cached(timeout=300)
def get_data():
    pass
```

2. بهینه‌سازی Database queries:
```sql
-- اضافه کردن indexes
-- استفاده از select_related
```

3. استفاده از CDN برای static files

4. Load Balancing

---

## 🆘 دستورات مفید عیب‌یابی

### بررسی سلامت کلی

```bash
#!/bin/bash

echo "=== System Health Check ==="

# Backend
echo "Backend:"
curl -f http://localhost:8000/health && echo "✓" || echo "✗"

# Frontend
echo "Frontend:"
curl -f http://localhost:3000 && echo "✓" || echo "✗"

# PostgreSQL
echo "PostgreSQL:"
pg_isready && echo "✓" || echo "✗"

# Redis
echo "Redis:"
redis-cli ping && echo "✓" || echo "✗"

# Disk Space
echo "Disk Space:"
df -h | grep -E "/$"

# Memory
echo "Memory:"
free -h | grep Mem

# Load Average
echo "Load Average:"
uptime
```

### بررسی Logs

```bash
# همه logs
sudo journalctl -xe

# Logs یک سرویس خاص
sudo journalctl -u writers-backend -f

# Logs با فیلتر زمانی
sudo journalctl --since "1 hour ago"

# Logs Docker
docker-compose logs -f --tail=100
```

### بررسی Ports

```bash
# بررسی port‌های باز
sudo netstat -tulpn | grep LISTEN

# بررسی port خاص
sudo lsof -i :8000
```

---

## 📞 دریافت کمک

اگر مشکل شما حل نشد:

1. **GitHub Issues**: [ایجاد Issue](https://github.com/yourusername/writers/issues)
2. **Discussions**: [پرسیدن سوال](https://github.com/yourusername/writers/discussions)
3. **Documentation**: مطالعه مستندات کامل
4. **Logs**: ارسال logs کامل هنگام گزارش مشکل

### الگوی گزارش مشکل

```markdown
## توضیحات مشکل
[توضیح دقیق مشکل]

## مراحل بازتولید
1. 
2. 
3. 

## رفتار مورد انتظار
[چه چیزی باید اتفاق بیفتد]

## رفتار واقعی
[چه اتفاقی می‌افتد]

## محیط
- OS: [e.g. Ubuntu 22.04]
- Python version:
- Node.js version:
- Docker version:

## Logs
```
[paste logs here]
```

## اطلاعات اضافی
[screenshots, etc.]
```

---

برای به‌روزرسانی‌های مستندات، [Repository](https://github.com/yourusername/writers) را دنبال کنید.
