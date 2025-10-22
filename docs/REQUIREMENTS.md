# پیش‌نیازها و سیستم‌های مورد نیاز

این سند تمام پیش‌نیازهای نرم‌افزاری و سخت‌افزاری مورد نیاز برای نصب و اجرای سیستم Writers را شرح می‌دهد.

## 🖥️ سخت‌افزار مورد نیاز

### حداقل سخت‌افزار (محیط Development)
- **CPU**: 4 هسته
- **RAM**: 8 GB
- **دیسک**: 20 GB فضای خالی
- **شبکه**: اتصال اینترنت پایدار

### توصیه شده برای Development
- **CPU**: 8 هسته یا بیشتر
- **RAM**: 16 GB
- **دیسک**: 50 GB SSD
- **شبکه**: اتصال پرسرعت

### محیط Production (بر اساس تعداد کاربران)

#### کوچک (تا 100 کاربر همزمان)
- **CPU**: 4-8 هسته
- **RAM**: 16 GB
- **دیسک**: 50 GB SSD + 500 GB HDD
- **شبکه**: 100 Mbps

#### متوسط (100-500 کاربر همزمان)
- **CPU**: 8-16 هسته
- **RAM**: 32 GB
- **دیسک**: 100 GB SSD + 1 TB HDD
- **شبکه**: 1 Gbps

#### بزرگ (500-1000+ کاربر همزمان)
- **CPU**: 16-32 هسته
- **RAM**: 64-128 GB
- **دیسک**: 200 GB SSD + 5 TB HDD
- **شبکه**: 10 Gbps

### پیکربندی دیسک توصیه شده
- **SSD**: برای PostgreSQL و سیستم عامل
- **HDD**: برای ذخیره فایل‌های آپلود شده
- **RAID 1 یا RAID 10**: برای محافظت از داده‌ها

### GPU (اختیاری)
برای پردازش سریع‌تر تسک‌های AI/ML:
- **NVIDIA GPU** با پشتیبانی CUDA
- حداقل 8 GB VRAM
- Driver به‌روز NVIDIA

## 💻 سیستم‌عامل

### سیستم‌عامل‌های پشتیبانی شده

#### توصیه شده
- **Ubuntu 20.04 LTS** یا **22.04 LTS**
- **Debian 11** یا **12**

#### پشتیبانی شده
- **CentOS 8** یا بالاتر
- **RHEL 8** یا بالاتر
- **Rocky Linux 8** یا بالاتر

#### محیط Development
- **Windows 10/11** (با WSL2)
- **macOS** (Monterey یا بالاتر)
- **Linux** (هر توزیع مدرن)

## 🐍 Python

### نسخه مورد نیاز
- **Python 3.10** یا بالاتر (توصیه شده: Python 3.11)

### نصب Python در Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
```

### نصب در CentOS/RHEL
```bash
sudo dnf install -y python3.11 python3.11-devel
```

### بررسی نسخه
```bash
python3 --version
# باید Python 3.10 یا بالاتر باشد
```

## 📦 Node.js و npm

### نسخه مورد نیاز
- **Node.js**: 18.x LTS یا بالاتر (توصیه شده: 20.x LTS)
- **npm**: 9.x یا بالاتر

### نصب در Ubuntu/Debian
```bash
# نصب از NodeSource
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# یا با nvm (توصیه شده)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 20
nvm use 20
```

### نصب در CentOS/RHEL
```bash
curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
sudo dnf install -y nodejs
```

### بررسی نسخه
```bash
node --version  # v20.x.x
npm --version   # 10.x.x
```

## 🐘 PostgreSQL

### نسخه مورد نیاز
- **PostgreSQL 14** یا بالاتر (توصیه شده: PostgreSQL 15)

### نصب در Ubuntu/Debian
```bash
# اضافه کردن repository رسمی PostgreSQL
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget -qO- https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo tee /etc/apt/trusted.gpg.d/pgdg.asc &>/dev/null

# نصب PostgreSQL
sudo apt update
sudo apt install -y postgresql-15 postgresql-contrib-15
```

### نصب در CentOS/RHEL
```bash
sudo dnf install -y postgresql15-server postgresql15-contrib
sudo postgresql-15-setup initdb
sudo systemctl enable postgresql-15
sudo systemctl start postgresql-15
```

### بررسی نصب
```bash
sudo systemctl status postgresql
sudo -u postgres psql --version
```

### پیکربندی‌های توصیه شده

#### فایل postgresql.conf
```ini
# Connection Settings
max_connections = 100
shared_buffers = 4GB          # 25% از RAM
effective_cache_size = 12GB   # 75% از RAM
maintenance_work_mem = 1GB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1        # برای SSD
effective_io_concurrency = 200
work_mem = 41943kB
min_wal_size = 2GB
max_wal_size = 8GB
```

## 🔴 Redis

### نسخه مورد نیاز
- **Redis 6.x** یا بالاتر (توصیه شده: Redis 7.x)

### نصب در Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y redis-server
```

### نصب در CentOS/RHEL
```bash
sudo dnf install -y redis
```

### نصب از سورس (آخرین نسخه)
```bash
wget https://download.redis.io/redis-stable.tar.gz
tar -xzvf redis-stable.tar.gz
cd redis-stable
make
sudo make install
```

### پیکربندی توصیه شده

#### فایل redis.conf
```conf
# Security
requirepass YOUR_STRONG_PASSWORD
bind 127.0.0.1

# Memory Management
maxmemory 512mb
maxmemory-policy allkeys-lru

# Persistence
save 900 1
save 300 10
save 60 10000
appendonly yes
appendfsync everysec

# Performance
tcp-backlog 511
timeout 300
tcp-keepalive 300
```

### بررسی نصب
```bash
redis-cli --version
sudo systemctl status redis-server
redis-cli ping  # باید PONG برگرداند
```

## 🌐 Nginx

### نسخه مورد نیاز
- **Nginx 1.18** یا بالاتر

### نصب در Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y nginx
```

### نصب در CentOS/RHEL
```bash
sudo dnf install -y nginx
```

### فعال‌سازی
```bash
sudo systemctl enable nginx
sudo systemctl start nginx
```

### بررسی نصب
```bash
nginx -v
sudo systemctl status nginx
curl localhost  # باید صفحه پیش‌فرض Nginx را نشان دهد
```

## 🐳 Docker و Docker Compose (برای Monitoring)

### Docker

#### نصب در Ubuntu/Debian
```bash
# حذف نسخه‌های قدیمی
sudo apt remove docker docker-engine docker.io containerd runc

# نصب Docker از repository رسمی
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# اضافه کردن کاربر به گروه docker
sudo usermod -aG docker $USER
```

#### نصب در CentOS/RHEL
```bash
sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo dnf install -y docker-ce docker-ce-cli containerd.io
sudo systemctl enable docker
sudo systemctl start docker
```

### Docker Compose

```bash
# نصب آخرین نسخه
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### بررسی نصب
```bash
docker --version
docker-compose --version
docker run hello-world
```

## 🔧 ابزارهای توسعه

### برای Backend Development
```bash
# Git
sudo apt install -y git

# Build essentials
sudo apt install -y build-essential libssl-dev libffi-dev python3-dev

# PostgreSQL development headers
sudo apt install -y libpq-dev

# برای پردازش تصویر (اختیاری)
sudo apt install -y libjpeg-dev libpng-dev
```

### برای Frontend Development
```bash
# Yarn (اختیاری - جایگزین npm)
npm install -g yarn

# پکیج‌های global مفید
npm install -g pm2           # Process Manager
npm install -g typescript    # TypeScript Compiler
```

## 📊 ابزارهای Monitoring (نصب با Docker)

این ابزارها معمولاً با Docker نصب می‌شوند و نیازی به نصب جداگانه ندارند:

- **Prometheus**: Metrics Collection
- **Grafana**: Visualization
- **Loki**: Log Aggregation
- **Promtail**: Log Collection
- **Alertmanager**: Alert Management
- **Node Exporter**: System Metrics
- **PostgreSQL Exporter**: Database Metrics
- **Redis Exporter**: Cache Metrics

## 🔐 ابزارهای امنیتی

### Certbot (برای SSL/TLS)
```bash
# Ubuntu/Debian
sudo apt install -y certbot python3-certbot-nginx

# CentOS/RHEL
sudo dnf install -y certbot python3-certbot-nginx
```

### Fail2Ban (محافظت از Brute Force)
```bash
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### UFW Firewall
```bash
sudo apt install -y ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable
```

## 📝 بررسی نهایی پیش‌نیازها

اسکریپت زیر را اجرا کنید تا تمام پیش‌نیازها بررسی شوند:

```bash
#!/bin/bash

echo "=== بررسی پیش‌نیازهای سیستم Writers ==="

# Python
echo -n "Python: "
python3 --version 2>/dev/null || echo "❌ نصب نشده"

# Node.js
echo -n "Node.js: "
node --version 2>/dev/null || echo "❌ نصب نشده"

# PostgreSQL
echo -n "PostgreSQL: "
psql --version 2>/dev/null || echo "❌ نصب نشده"

# Redis
echo -n "Redis: "
redis-cli --version 2>/dev/null || echo "❌ نصب نشده"

# Nginx
echo -n "Nginx: "
nginx -v 2>&1 || echo "❌ نصب نشده"

# Docker
echo -n "Docker: "
docker --version 2>/dev/null || echo "❌ نصب نشده"

# Docker Compose
echo -n "Docker Compose: "
docker-compose --version 2>/dev/null || echo "❌ نصب نشده"

# Git
echo -n "Git: "
git --version 2>/dev/null || echo "❌ نصب نشده"

echo ""
echo "=== بررسی سرویس‌ها ==="

# PostgreSQL Service
echo -n "PostgreSQL Service: "
systemctl is-active postgresql 2>/dev/null || echo "❌ فعال نیست"

# Redis Service
echo -n "Redis Service: "
systemctl is-active redis-server 2>/dev/null || systemctl is-active redis 2>/dev/null || echo "❌ فعال نیست"

# Nginx Service
echo -n "Nginx Service: "
systemctl is-active nginx 2>/dev/null || echo "❌ فعال نیست"

echo ""
echo "=== بررسی منابع سیستم ==="

# RAM
echo "RAM: $(free -h | awk '/^Mem:/ {print $2}')"

# CPU
echo "CPU Cores: $(nproc)"

# Disk Space
echo "Disk Space: $(df -h / | awk 'NR==2 {print $4}') available"

echo ""
echo "بررسی تکمیل شد!"
```

## 📋 چک‌لیست نهایی

قبل از شروع نصب، از موارد زیر اطمینان حاصل کنید:

- [ ] Python 3.10+ نصب شده
- [ ] Node.js 18+ نصب شده
- [ ] PostgreSQL 14+ نصب و اجرا شده
- [ ] Redis 6+ نصب و اجرا شده
- [ ] Nginx نصب شده
- [ ] Docker و Docker Compose نصب شده (برای Monitoring)
- [ ] Git نصب شده
- [ ] حداقل 16GB RAM موجود است
- [ ] حداقل 50GB فضای دیسک خالی است
- [ ] اتصال اینترنت پایدار موجود است
- [ ] دسترسی sudo/root به سیستم دارید

## 🆘 مشکلات رایج

### مشکل: Python version قدیمی است
```bash
# نصب Python از deadsnakes PPA (Ubuntu)
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11 python3.11-venv
```

### مشکل: PostgreSQL شروع نمی‌شود
```bash
# بررسی لاگ‌ها
sudo journalctl -u postgresql -n 50

# بررسی فضای دیسک
df -h

# بررسی پورت 5432
sudo netstat -tulpn | grep 5432
```

### مشکل: Redis authentication error
```bash
# حذف requirepass از redis.conf موقتاً
sudo nano /etc/redis/redis.conf
# comment کنید: # requirepass yourpassword
sudo systemctl restart redis-server
```

### مشکل: Permission denied در Docker
```bash
# اضافه کردن کاربر به گروه docker
sudo usermod -aG docker $USER
# خروج و ورود مجدد به سیستم
```

---

پس از اطمینان از نصب تمام پیش‌نیازها، می‌توانید به [راهنمای نصب](INSTALLATION.md) بروید.
