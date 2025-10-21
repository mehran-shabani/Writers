#!/bin/bash
# =============================================================================
# Quick Start Script for Docker Compose Deployment
# =============================================================================
# این اسکریپت برای راه‌اندازی سریع اپلیکیشن با Docker Compose
# 
# استفاده:
#   chmod +x quick-start-docker.sh
#   ./quick-start-docker.sh
# =============================================================================

set -e  # خروج در صورت خطا

# رنگ‌ها برای output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# تابع برای چاپ پیام‌ها
info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# بررسی اجرا با root
if [ "$EUID" -eq 0 ]; then 
   error "لطفاً این اسکریپت را بدون sudo اجرا کنید"
   exit 1
fi

info "شروع راه‌اندازی سریع اپلیکیشن با Docker Compose..."
echo ""

# بررسی نصب Docker
info "بررسی نصب Docker..."
if ! command -v docker &> /dev/null; then
    error "Docker نصب نیست. لطفاً ابتدا Docker را نصب کنید."
    echo "برای نصب: https://docs.docker.com/engine/install/"
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    error "Docker Compose نصب نیست."
    exit 1
fi

success "Docker و Docker Compose نصب شده‌اند"
docker --version
docker compose version
echo ""

# بررسی فایل .env
info "بررسی فایل متغیرهای محیطی..."
if [ ! -f "../.env" ]; then
    warning "فایل .env یافت نشد. در حال ایجاد از .env.example..."
    if [ -f "../.env.example" ]; then
        cp ../.env.example ../.env
        warning "فایل .env ایجاد شد. لطفاً رمزها را تنظیم کنید!"
        echo ""
        echo "برای تولید رمز امن:"
        echo "  openssl rand -base64 48"
        echo ""
        read -p "آیا می‌خواهید ادامه دهید؟ (y/n) " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        error "فایل .env.example یافت نشد!"
        exit 1
    fi
else
    success "فایل .env موجود است"
fi
echo ""

# بررسی فایل .env در infrastructure
info "بررسی فایل .env در infrastructure..."
if [ ! -f ".env" ]; then
    if [ -f ".env.docker" ]; then
        info "کپی .env.docker به .env..."
        cp .env.docker .env
        warning "لطفاً فایل infrastructure/.env را ویرایش کنید"
    fi
fi
echo ""

# بررسی دایرکتوری storage
info "بررسی دایرکتوری /storage..."
if [ ! -d "/storage" ]; then
    warning "/storage موجود نیست"
    warning "اگر فضای ذخیره‌سازی جداگانه دارید، ابتدا آن را mount کنید:"
    echo "  sudo STORAGE_DEVICE=/dev/sdX1 ./setup_storage.sh"
    echo ""
    read -p "آیا می‌خواهید با یک دایرکتوری موقت ادامه دهید؟ (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        info "ایجاد /tmp/storage به عنوان موقت..."
        mkdir -p /tmp/storage/uploads /tmp/storage/results
        warning "در production حتماً از دیسک جداگانه استفاده کنید!"
    else
        exit 1
    fi
else
    success "/storage موجود است"
fi
echo ""

# بررسی SSD برای PostgreSQL
info "بررسی SSD برای PostgreSQL..."
SSD_PATH="${SSD_MOUNT_POINT:-/mnt/ssd}"
if [ ! -d "$SSD_PATH/postgresql/data" ]; then
    warning "$SSD_PATH/postgresql/data موجود نیست"
    info "ایجاد دایرکتوری داده PostgreSQL..."
    sudo mkdir -p "$SSD_PATH/postgresql/data"
    sudo chown -R 999:999 "$SSD_PATH/postgresql/data"  # PostgreSQL UID در Docker
    sudo chmod 700 "$SSD_PATH/postgresql/data"
    success "دایرکتوری ایجاد شد"
else
    success "دایرکتوری PostgreSQL data موجود است"
fi
echo ""

# Pull کردن image های پایه
info "دانلود image های Docker..."
docker compose pull postgres redis || true
echo ""

# Build کردن image های اپلیکیشن
info "Build کردن image های اپلیکیشن..."
if [ -d "../backend" ] && [ -f "../backend/Dockerfile" ]; then
    info "Build backend..."
    docker compose build backend
else
    warning "Dockerfile برای backend یافت نشد - از image استفاده می‌شود"
fi

if [ -d "../frontend" ] && [ -f "../frontend/Dockerfile" ]; then
    info "Build frontend..."
    docker compose build frontend
else
    warning "Dockerfile برای frontend یافت نشد - از image استفاده می‌شود"
fi

if [ -d "../worker" ] && [ -f "../worker/Dockerfile" ]; then
    info "Build worker..."
    docker compose build worker
else
    warning "Dockerfile برای worker یافت نشد - از image استفاده می‌شود"
fi
echo ""

# اجرای سرویس‌ها
info "اجرای سرویس‌ها..."
docker compose up -d
echo ""

# انتظار برای آماده شدن سرویس‌ها
info "انتظار برای آماده شدن سرویس‌ها (30 ثانیه)..."
sleep 30
echo ""

# بررسی وضعیت
info "بررسی وضعیت سرویس‌ها..."
docker compose ps
echo ""

# نمایش لاگ‌ها
info "لاگ‌های اخیر:"
docker compose logs --tail=20
echo ""

# تست سلامت سرویس‌ها
echo "=================================="
info "تست سلامت سرویس‌ها:"
echo "=================================="

# PostgreSQL
if docker compose exec -T postgres pg_isready &> /dev/null; then
    success "✓ PostgreSQL: آماده"
else
    error "✗ PostgreSQL: مشکل دارد"
fi

# Redis
if docker compose exec -T redis redis-cli ping &> /dev/null; then
    success "✓ Redis: آماده"
else
    error "✗ Redis: مشکل دارد"
fi

# Backend (اگر endpoint health دارد)
if command -v curl &> /dev/null; then
    if curl -f -s http://localhost:8000/health &> /dev/null; then
        success "✓ Backend: آماده"
    else
        warning "✗ Backend: در حال راه‌اندازی یا مشکل دارد"
    fi
fi

# Frontend
if command -v curl &> /dev/null; then
    if curl -f -s http://localhost:3000 &> /dev/null; then
        success "✓ Frontend: آماده"
    else
        warning "✗ Frontend: در حال راه‌اندازی یا مشکل دارد"
    fi
fi

echo ""
echo "=================================="
success "راه‌اندازی کامل شد!"
echo "=================================="
echo ""
echo "دسترسی به سرویس‌ها:"
echo "  - Frontend:  http://localhost:3000"
echo "  - Backend:   http://localhost:8000"
echo "  - PostgreSQL: localhost:5432 (فقط در Docker network)"
echo "  - Redis:      localhost:6379 (فقط در Docker network)"
echo ""
echo "دستورات مفید:"
echo "  - مشاهده لاگ‌ها:        docker compose logs -f"
echo "  - بررسی وضعیت:          docker compose ps"
echo "  - ری‌استارت سرویس:      docker compose restart [service]"
echo "  - متوقف کردن:           docker compose stop"
echo "  - حذف سرویس‌ها:         docker compose down"
echo ""
echo "برای جزئیات بیشتر: cat DEPLOYMENT.md"
echo ""
