# مستندات API سیستم Writers

این سند تمام Endpointهای API موجود در سیستم Writers را شرح می‌دهد.

## 📋 اطلاعات کلی

### Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://yourdomain.com/api`

### احراز هویت

سیستم از JWT (JSON Web Token) برای احراز هویت استفاده می‌کند. Token‌ها به صورت HttpOnly Cookie ذخیره می‌شوند.

#### انواع Token

- **Access Token**: زمان اعتبار 30 دقیقه
- **Refresh Token**: زمان اعتبار 7 روز

### Headers

```http
Content-Type: application/json
Cookie: access_token=<token>; refresh_token=<token>
```

### Response Format

#### موفق
```json
{
  "status": "success",
  "data": { ... }
}
```

#### خطا
```json
{
  "detail": "پیام خطا"
}
```

### Status Codes

- `200 OK`: درخواست موفق
- `201 Created`: منبع ایجاد شد
- `204 No Content`: درخواست موفق بدون محتوا
- `400 Bad Request`: داده‌های ورودی نامعتبر
- `401 Unauthorized`: احراز هویت نشده
- `403 Forbidden`: دسترسی مجاز نیست
- `404 Not Found`: منبع یافت نشد
- `422 Unprocessable Entity`: خطای اعتبارسنجی
- `500 Internal Server Error`: خطای سرور

## 🔐 Authentication API

### POST /api/auth/register

ثبت‌نام کاربر جدید

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "نام کامل (اختیاری)"
}
```

**Validation:**
- Email باید معتبر باشد
- Password حداقل 8 کاراکتر
- Password باید شامل حروف بزرگ، کوچک و عدد باشد

**Response (201):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "نام کامل",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00"
}
```

**Errors:**
- `400`: ایمیل تکراری است
- `422`: داده‌های نامعتبر

**مثال با cURL:**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!",
    "full_name": "نام کامل"
  }'
```

---

### POST /api/auth/login

ورود به سیستم

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200):**
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "نام کامل"
  },
  "message": "Login successful"
}
```

**Set-Cookie Headers:**
```
access_token=<jwt_token>; HttpOnly; Secure; SameSite=Strict; Max-Age=1800
refresh_token=<jwt_token>; HttpOnly; Secure; SameSite=Strict; Max-Age=604800
```

**Errors:**
- `401`: ایمیل یا رمز عبور اشتباه
- `422`: داده‌های نامعتبر

**مثال:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }'
```

---

### POST /api/auth/logout

خروج از سیستم

**Headers:**
```
Cookie: access_token=<token>
```

**Response (200):**
```json
{
  "message": "Logout successful"
}
```

**مثال:**
```bash
curl -X POST http://localhost:8000/api/auth/logout \
  -b cookies.txt
```

---

### GET /api/auth/me

دریافت اطلاعات کاربر جاری

**Headers:**
```
Cookie: access_token=<token>
```

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "نام کامل",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00"
}
```

**Errors:**
- `401`: Token نامعتبر یا منقضی شده

**مثال:**
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -b cookies.txt
```

---

### POST /api/auth/refresh

تمدید Access Token

**Headers:**
```
Cookie: refresh_token=<token>
```

**Response (200):**
```json
{
  "message": "Token refreshed successfully"
}
```

**Set-Cookie:**
```
access_token=<new_jwt_token>; HttpOnly; Secure; SameSite=Strict; Max-Age=1800
```

**Errors:**
- `401`: Refresh token نامعتبر

**مثال:**
```bash
curl -X POST http://localhost:8000/api/auth/refresh \
  -b cookies.txt \
  -c cookies.txt
```

---

## 📝 Tasks API

### GET /api/tasks

دریافت لیست تسک‌ها

**Headers:**
```
Cookie: access_token=<token>
```

**Query Parameters:**
- `skip` (int): تعداد رکورد skip (default: 0)
- `limit` (int): تعداد رکورد (default: 100, max: 100)
- `status` (string): فیلتر بر اساس وضعیت (pending, processing, completed, failed)

**Response (200):**
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "عنوان تسک",
      "description": "توضیحات",
      "status": "completed",
      "file_path": "/storage/files/file.txt",
      "processing_status": "success",
      "processing_result": { ... },
      "owner_id": 1,
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

**مثال:**
```bash
# دریافت همه تسک‌ها
curl -X GET http://localhost:8000/api/tasks \
  -b cookies.txt

# با فیلتر
curl -X GET "http://localhost:8000/api/tasks?status=completed&limit=10" \
  -b cookies.txt
```

---

### POST /api/tasks

ایجاد تسک جدید

**Headers:**
```
Cookie: access_token=<token>
Content-Type: application/json
```

**Request:**
```json
{
  "title": "عنوان تسک",
  "description": "توضیحات تسک (اختیاری)",
  "status": "pending"
}
```

**Validation:**
- Title: حداقل 3 کاراکتر، اجباری
- Description: اختیاری
- Status: یکی از [pending, in_progress, completed]

**Response (201):**
```json
{
  "id": 1,
  "title": "عنوان تسک",
  "description": "توضیحات",
  "status": "pending",
  "owner_id": 1,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

**Errors:**
- `422`: داده‌های نامعتبر
- `401`: احراز هویت نشده

**مثال:**
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "title": "تسک جدید",
    "description": "این یک تسک تستی است"
  }'
```

---

### GET /api/tasks/{task_id}

دریافت جزئیات یک تسک

**Headers:**
```
Cookie: access_token=<token>
```

**URL Parameters:**
- `task_id` (int): شناسه تسک

**Response (200):**
```json
{
  "id": 1,
  "title": "عنوان تسک",
  "description": "توضیحات",
  "status": "completed",
  "file_path": "/storage/files/file.txt",
  "processing_status": "success",
  "processing_result": {
    "processed_at": "2024-01-01T00:00:00",
    "data": { ... }
  },
  "owner_id": 1,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

**Errors:**
- `404`: تسک یافت نشد
- `403`: دسترسی مجاز نیست (تسک متعلق به کاربر دیگری است)

**مثال:**
```bash
curl -X GET http://localhost:8000/api/tasks/1 \
  -b cookies.txt
```

---

### PUT /api/tasks/{task_id}

ویرایش تسک

**Headers:**
```
Cookie: access_token=<token>
Content-Type: application/json
```

**Request:**
```json
{
  "title": "عنوان جدید (اختیاری)",
  "description": "توضیحات جدید (اختیاری)",
  "status": "completed"
}
```

**Response (200):**
```json
{
  "id": 1,
  "title": "عنوان جدید",
  "description": "توضیحات جدید",
  "status": "completed",
  "updated_at": "2024-01-01T00:00:00"
}
```

**Errors:**
- `404`: تسک یافت نشد
- `403`: دسترسی مجاز نیست
- `422`: داده‌های نامعتبر

**مثال:**
```bash
curl -X PUT http://localhost:8000/api/tasks/1 \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "status": "completed"
  }'
```

---

### DELETE /api/tasks/{task_id}

حذف تسک

**Headers:**
```
Cookie: access_token=<token>
```

**Response (204):**
بدون محتوا

**Errors:**
- `404`: تسک یافت نشد
- `403`: دسترسی مجاز نیست

**مثال:**
```bash
curl -X DELETE http://localhost:8000/api/tasks/1 \
  -b cookies.txt
```

---

### POST /api/tasks/{task_id}/upload

آپلود فایل برای تسک

**Headers:**
```
Cookie: access_token=<token>
Content-Type: multipart/form-data
```

**Form Data:**
- `file` (file): فایل برای آپلود

**Validation:**
- حداکثر حجم: 10MB
- فرمت‌های مجاز: txt, pdf, doc, docx, jpg, png

**Response (200):**
```json
{
  "message": "File uploaded successfully",
  "file_path": "/storage/uploads/filename.txt",
  "task_id": 1,
  "celery_task_id": "abc-123-def-456"
}
```

**Errors:**
- `400`: فرمت فایل مجاز نیست
- `413`: حجم فایل بیش از حد مجاز
- `404`: تسک یافت نشد

**مثال:**
```bash
curl -X POST http://localhost:8000/api/tasks/1/upload \
  -b cookies.txt \
  -F "file=@/path/to/file.txt"
```

---

### GET /api/tasks/{task_id}/status

دریافت وضعیت پردازش فایل

**Headers:**
```
Cookie: access_token=<token>
```

**Response (200):**
```json
{
  "task_id": 1,
  "processing_status": "processing",
  "progress": 50,
  "message": "در حال پردازش..."
}
```

**Processing Statuses:**
- `pending`: در انتظار پردازش
- `processing`: در حال پردازش
- `success`: پردازش موفق
- `failed`: پردازش ناموفق

**مثال:**
```bash
curl -X GET http://localhost:8000/api/tasks/1/status \
  -b cookies.txt
```

---

## 🔧 System API

### GET /health

بررسی سلامت سیستم

**Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00",
  "version": "1.0.0"
}
```

**مثال:**
```bash
curl http://localhost:8000/health
```

---

### GET /metrics

متریک‌های Prometheus

**Response (200):**
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",path="/api/tasks"} 42
...
```

**مثال:**
```bash
curl http://localhost:8000/metrics
```

---

## 📊 نمونه استفاده کامل

### JavaScript/TypeScript (با Axios)

```typescript
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

// تنظیمات Axios
const api = axios.create({
  baseURL: API_BASE,
  withCredentials: true, // برای ارسال cookies
  headers: {
    'Content-Type': 'application/json',
  },
});

// ثبت‌نام
async function register(email: string, password: string) {
  const response = await api.post('/api/auth/register', {
    email,
    password,
  });
  return response.data;
}

// ورود
async function login(email: string, password: string) {
  const response = await api.post('/api/auth/login', {
    email,
    password,
  });
  return response.data;
}

// دریافت تسک‌ها
async function getTasks() {
  const response = await api.get('/api/tasks');
  return response.data;
}

// ایجاد تسک
async function createTask(title: string, description?: string) {
  const response = await api.post('/api/tasks', {
    title,
    description,
  });
  return response.data;
}

// آپلود فایل
async function uploadFile(taskId: number, file: File) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post(
    `/api/tasks/${taskId}/upload`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );
  return response.data;
}
```

### Python (با Requests)

```python
import requests

API_BASE = 'http://localhost:8000'
session = requests.Session()

# ثبت‌نام
def register(email, password):
    response = session.post(f'{API_BASE}/api/auth/register', json={
        'email': email,
        'password': password,
    })
    return response.json()

# ورود
def login(email, password):
    response = session.post(f'{API_BASE}/api/auth/login', json={
        'email': email,
        'password': password,
    })
    return response.json()

# دریافت تسک‌ها
def get_tasks():
    response = session.get(f'{API_BASE}/api/tasks')
    return response.json()

# ایجاد تسک
def create_task(title, description=None):
    response = session.post(f'{API_BASE}/api/tasks', json={
        'title': title,
        'description': description,
    })
    return response.json()

# آپلود فایل
def upload_file(task_id, file_path):
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = session.post(
            f'{API_BASE}/api/tasks/{task_id}/upload',
            files=files
        )
    return response.json()
```

## 🔗 Interactive Documentation

برای مستندات تعاملی و تست API:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📝 نکات مهم

1. **همیشه از HTTPS در Production استفاده کنید**
2. **Token‌ها را امن نگه دارید**
3. **Rate Limiting را رعایت کنید**
4. **خطاها را مدیریت کنید**
5. **از Refresh Token برای تمدید دسترسی استفاده کنید**

## 🔗 مراجع مرتبط

- [راهنمای احراز هویت](AUTHENTICATION.md)
- [راهنمای خطاها](ERROR_HANDLING.md)
- [محدودیت‌های API](RATE_LIMITING.md)

---

برای سوالات و مشکلات، به [GitHub Issues](https://github.com/yourusername/writers/issues) مراجعه کنید.
