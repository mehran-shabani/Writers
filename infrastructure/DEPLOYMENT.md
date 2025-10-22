# Deployment Guide

This document provides two methods for deploying the application:
1. **Deployment with Docker Compose** (Recommended for both development and production environments)
2. **Direct Deployment with systemd** (For running natively on a server)

---

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Method 1: Deployment with Docker Compose](#method-1-deployment-with-docker-compose)
  - [Installing Docker and Docker Compose](#installing-docker-and-docker-compose)
  - [Environment Configuration](#environment-configuration)
  - [Launching Services](#launching-services)
  - [Management and Maintenance](#management-and-maintenance)
- [Method 2: Direct Deployment with systemd](#method-2-direct-deployment-with-systemd)
  - [Installing Dependencies](#installing-dependencies)
  - [Infrastructure Setup](#infrastructure-setup)
  - [systemd Configuration](#systemd-configuration)
  - [Service Management](#service-management)
- [Monitoring and Logs](#monitoring-and-logs)
- [Backup](#backup)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Hardware
- **CPU**: Minimum 4 cores (8+ cores recommended)
- **RAM**: Minimum 8GB (16GB+ recommended)
- **SSD**: For PostgreSQL (minimum 100GB)
- **Storage**: 100TB for application files (mounted at `/storage`)

### Software
- **Operating System**: Ubuntu 20.04/22.04 LTS or Debian 11/12
- **Access**: User with sudo privileges
- **Network**: Internet connection for downloading packages

---

# Method 1: Deployment with Docker Compose

Using Docker Compose is the simplest and fastest method for deployment.

## Installing Docker and Docker Compose

### Ubuntu/Debian

```bash
# Remove old versions (if they exist)
sudo apt-get remove docker docker-engine docker.io containerd runc

# Install dependencies
sudo apt-get update
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Add the Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine and Docker Compose
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add the current user to the docker group
sudo usermod -aG docker $USER

# Enable automatic startup
sudo systemctl enable docker
sudo systemctl start docker

# Test the installation
docker --version
docker compose version
```

**Note**: After running the `usermod` command, you must log out and log back in.

## Environment Configuration

### 1. Preparing the Storage Space

If you have not yet mounted the 100TB storage space:

```bash
# Run the setup_storage.sh script
cd /workspace/infrastructure
sudo STORAGE_DEVICE=/dev/sdX1 ./setup_storage.sh
```

This script:
- Mounts the disk at `/storage`
- Creates `uploads/` and `results/` directories
- Sets the appropriate permissions
- Makes the mount persistent in `/etc/fstab`

### 2. Preparing the SSD for PostgreSQL

```bash
# Run the setup_postgresql.sh script
cd /workspace/infrastructure
sudo SSD_MOUNT_POINT=/mnt/ssd ./setup_postgresql.sh
```

**Important Note**: For deployment with Docker, this script is only used to create the PostgreSQL data directory. The PostgreSQL service is run by Docker.

### 3. Configuring Environment Files

```bash
# Return to the project root
cd /workspace

# Copy the sample environment variables file
cp .env.example .env

# Edit and set the actual values
nano .env
```

**Important variables that must be set:**

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

**Generating secure passwords:**

```bash
# With OpenSSL
openssl rand -base64 48

# With Python
python3 -c "import secrets; print(secrets.token_hex(32))"

# With Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

### 4. Creating Service Environment Files

If the frontend, backend, or worker services require specific variables:

```bash
# Frontend
touch frontend/.env.local

# Backend
touch backend/.env

# Worker
touch worker/.env
```

## Launching Services

### Building and Running Services

```bash
# Go to the infrastructure directory
cd /workspace/infrastructure

# Build the images (first time)
docker compose build

# Run all services in the background
docker compose up -d

# View the status of services
docker compose ps

# View the logs of all services
docker compose logs -f

# View the log of a specific service
docker compose logs -f backend
```

### Checking the Health of Services

```bash
# Check the health check
docker compose ps

# Test the connection to PostgreSQL
docker compose exec postgres psql -U myapp_user -d myapp_db -c "SELECT version();"

# Test the connection to Redis
docker compose exec redis redis-cli -a YOUR_REDIS_PASSWORD ping

# Test the Backend API
curl http://localhost:8000/health

# Test the Frontend
curl http://localhost:3000
```

## Management and Maintenance

### Common Commands

```bash
# View logs
docker compose logs -f [service_name]

# Restart a service
docker compose restart backend

# Restart all services
docker compose restart

# Stop services
docker compose stop

# Remove services (data is preserved)
docker compose down

# Remove services + volumes (dangerous!)
docker compose down -v

# Scale the worker for more processing
docker compose up -d --scale worker=3

# Update images
docker compose pull
docker compose up -d

# View resource consumption
docker stats
```

### Monitoring

```bash
# Install Docker stats for real-time monitoring
watch -n 1 'docker stats --no-stream'

# Check disk space
docker system df

# Clean up extra space
docker system prune -a

# View network
docker network ls
docker network inspect app-network
```

### Logs

By default, Docker logs are stored in `/var/lib/docker/containers/`.

To limit the size of logs, create the file `/etc/docker/daemon.json`:

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

Then restart Docker:

```bash
sudo systemctl restart docker
```

---

# Method 2: Direct Deployment with systemd

This method is for running services directly on the server without Docker.

## Installing Dependencies

### Node.js (for Backend, Frontend, Worker)

```bash
# Install Node.js 18.x LTS
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Check the installation
node --version
npm --version
```

### PostgreSQL

```bash
# Run the setup script with full installation
cd /workspace/infrastructure
sudo ./setup_postgresql.sh

# This script:
# - Installs PostgreSQL 15
# - Configures the data directory on the SSD
# - Applies optimal settings for the SSD
# - Starts the PostgreSQL service
```

### Redis

```bash
# Run the setup script
cd /workspace/infrastructure
sudo ./setup_redis.sh

# Note the Redis password
sudo cat /etc/redis/redis-password.txt
```

## Infrastructure Setup

### Storage Setup

```bash
cd /workspace/infrastructure
sudo STORAGE_DEVICE=/dev/sdX1 ./setup_storage.sh
```

### Database Configuration

```bash
# Create the database and user
sudo -u postgres psql << EOF
CREATE DATABASE myapp_production;
CREATE USER myapp_user WITH ENCRYPTED PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE myapp_production TO myapp_user;
\q
EOF

# Test the connection
psql -U myapp_user -d myapp_production -h localhost -c "SELECT version();"
```

### Building Applications

```bash
cd /workspace

# Backend
cd backend
npm install --production
npm run build  # If there is a build process

# Frontend
cd ../frontend
npm install --production
npm run build

# Worker
cd ../worker
npm install --production
npm run build  # If there is a build process

cd ..
```

## systemd Configuration

### 1. Creating the Backend Service File

```bash
sudo nano /etc/systemd/system/app-backend.service
```

Content:

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

# Load environment variables
EnvironmentFile=/workspace/.env
EnvironmentFile=/workspace/backend/.env

# Additional variables
Environment="NODE_ENV=production"
Environment="POSTGRES_HOST=localhost"
Environment="REDIS_HOST=localhost"

# Execution command
ExecStart=/usr/bin/node /workspace/backend/dist/index.js
# Or for Node.js without a build:
# ExecStart=/usr/bin/node /workspace/backend/src/index.js

# Automatic restart
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

### 2. Creating the Frontend Service File

```bash
sudo nano /etc/systemd/system/app-frontend.service
```

Content:

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

# Load environment variables
EnvironmentFile=/workspace/.env
EnvironmentFile=/workspace/frontend/.env.local

# Additional variables
Environment="NODE_ENV=production"
Environment="PORT=3000"

# Execution command (Next.js)
ExecStart=/usr/bin/npm start
# Or for a production build:
# ExecStart=/usr/bin/node /workspace/frontend/.next/standalone/server.js

# Automatic restart
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

### 3. Creating the Worker Service File

```bash
sudo nano /etc/systemd/system/app-worker.service
```

Content:

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

# Load environment variables
EnvironmentFile=/workspace/.env
EnvironmentFile=/workspace/worker/.env

# Additional variables
Environment="NODE_ENV=production"
Environment="POSTGRES_HOST=localhost"
Environment="REDIS_HOST=localhost"
Environment="WORKER_CONCURRENCY=5"

# Execution command
ExecStart=/usr/bin/node /workspace/worker/dist/index.js

# Automatic restart
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

### 4. Creating the Log Directory

```bash
sudo mkdir -p /var/log/app
sudo chown www-data:www-data /var/log/app
sudo chmod 755 /var/log/app
```

### 5. Setting Permissions

```bash
# Ensure correct permissions
sudo chown -R www-data:www-data /workspace/backend
sudo chown -R www-data:www-data /workspace/frontend
sudo chown -R www-data:www-data /workspace/worker

# .env files should not be readable by everyone
sudo chmod 640 /workspace/.env
sudo chmod 640 /workspace/backend/.env
sudo chmod 640 /workspace/frontend/.env.local
sudo chmod 640 /workspace/worker/.env
sudo chown www-data:www-data /workspace/.env
sudo chown www-data:www-data /workspace/backend/.env
sudo chown www-data:www-data /workspace/frontend/.env.local
sudo chown www-data:www-data /workspace/worker/.env
```

## Service Management

### Enabling and Starting Services

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable for automatic start
sudo systemctl enable app-backend.service
sudo systemctl enable app-frontend.service
sudo systemctl enable app-worker.service

# Start services
sudo systemctl start app-backend.service
sudo systemctl start app-frontend.service
sudo systemctl start app-worker.service

# Check status
sudo systemctl status app-backend.service
sudo systemctl status app-frontend.service
sudo systemctl status app-worker.service
```

### Management Commands

```bash
# View logs
sudo journalctl -u app-backend.service -f
sudo journalctl -u app-frontend.service -f
sudo journalctl -u app-worker.service -f

# Or file logs
tail -f /var/log/app/backend.log
tail -f /var/log/app/frontend.log
tail -f /var/log/app/worker.log

# Restart a service
sudo systemctl restart app-backend.service
sudo systemctl restart app-frontend.service
sudo systemctl restart app-worker.service

# Stop
sudo systemctl stop app-backend.service
sudo systemctl stop app-frontend.service
sudo systemctl stop app-worker.service

# Disable automatic start
sudo systemctl disable app-backend.service
```

### Viewing Overall Status

```bash
# Status of all application services
systemctl status 'app-*'

# List all running services
systemctl list-units --type=service --state=running | grep app-
```

---

# Monitoring and Logs

## Monitoring System Resources

### Using htop

```bash
sudo apt-get install htop
htop
```

### Disk Monitoring

```bash
# Used space
df -h

# Inode usage
df -i

# Space used by /storage
du -sh /storage/*

# Largest files
find /storage -type f -exec du -h {} + | sort -rh | head -n 20
```

### PostgreSQL Monitoring

```bash
# Active connections
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"

# Database size
sudo -u postgres psql -c "SELECT pg_database.datname, pg_size_pretty(pg_database_size(pg_database.datname)) AS size FROM pg_database;"

# Slow queries
sudo -u postgres psql -d myapp_production -c "SELECT query, calls, total_time, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"
```

### Redis Monitoring

```bash
# General information
redis-cli -a $(sudo cat /etc/redis/redis-password.txt) INFO

# Memory usage
redis-cli -a $(sudo cat /etc/redis/redis-password.txt) INFO memory

# Number of keys
redis-cli -a $(sudo cat /etc/redis/redis-password.txt) DBSIZE

# Real-time monitor
redis-cli -a $(sudo cat /etc/redis/redis-password.txt) MONITOR
```

## Log Management

### Log Rotation

For Docker Compose, logs are automatically rotated (if configured in `daemon.json`).

For systemd:

```bash
sudo nano /etc/logrotate.d/app
```

Content:

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

Test:

```bash
sudo logrotate -f /etc/logrotate.d/app
```

---

# Backup

## PostgreSQL Backup

### Manual Backup

```bash
# Full database backup
sudo -u postgres pg_dump myapp_production > backup_$(date +%Y%m%d_%H%M%S).sql

# Compressed backup
sudo -u postgres pg_dump myapp_production | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Restore
sudo -u postgres psql myapp_production < backup.sql
# Or for a compressed file:
gunzip -c backup.sql.gz | sudo -u postgres psql myapp_production
```

### Automatic Backup with Cron

```bash
sudo nano /usr/local/bin/backup-postgres.sh
```

Content:

```bash
#!/bin/bash
BACKUP_DIR="/storage/backups/postgres"
RETENTION_DAYS=30
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

# Backup
sudo -u postgres pg_dump myapp_production | gzip > "$BACKUP_DIR/backup_$DATE.sql.gz"

# Remove old backups
find "$BACKUP_DIR" -name "backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: backup_$DATE.sql.gz"
```

Grant execution permission and add to Cron:

```bash
sudo chmod +x /usr/local/bin/backup-postgres.sh

# Add to cron (every day at 2 AM)
sudo crontab -e
# Add:
0 2 * * * /usr/local/bin/backup-postgres.sh >> /var/log/app/backup.log 2>&1
```

## Redis Backup

Redis automatically saves snapshots (`appendonly.aof` and `dump.rdb`).

For a manual backup:

```bash
# Trigger save
redis-cli -a $(sudo cat /etc/redis/redis-password.txt) BGSAVE

# Copy data files
sudo cp /var/lib/redis/dump.rdb /storage/backups/redis/dump_$(date +%Y%m%d).rdb
```

## Application Files Backup

```bash
# Backup application code
tar -czf app_backup_$(date +%Y%m%d).tar.gz /workspace

# Backup uploaded files
rsync -av --progress /storage/uploads/ /storage/backups/uploads/
```

---

# Troubleshooting

## Common Problems

### Service does not start (Docker)

```bash
# Check logs
docker compose logs [service_name]

# Check container status
docker compose ps

# Check health check
docker inspect [container_name] | grep -A 10 Health

# Restart with rebuild
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Service does not start (systemd)

```bash
# Check detailed status
sudo systemctl status app-backend.service -l

# Check logs
sudo journalctl -u app-backend.service -n 100 --no-pager

# Verify the service file
sudo systemd-analyze verify /etc/systemd/system/app-backend.service

# Manual test
cd /workspace/backend
sudo -u www-data node dist/index.js
```

### Database connection error

```bash
# Check that PostgreSQL is running
sudo systemctl status postgresql

# Test the connection
psql -U myapp_user -d myapp_production -h localhost

# Check connection settings
cat /workspace/.env | grep POSTGRES

# Check PostgreSQL log
sudo tail -f /var/log/postgresql/postgresql-15-main.log
```

### Redis connection error

```bash
# Check Redis status
sudo systemctl status redis-server

# Test the connection
redis-cli -a $(sudo cat /etc/redis/redis-password.txt) PING

# Check the port
sudo netstat -tlnp | grep 6379

# Check the log
sudo tail -f /var/log/redis/redis-server.log
```

### Disk space full

```bash
# Check disk usage
df -h

# Find large files
du -sh /var/lib/docker/* | sort -rh | head -n 10
du -sh /storage/* | sort -rh | head -n 10

# Clean up Docker (if using Docker)
docker system prune -a --volumes

# Clean up old logs
sudo journalctl --vacuum-time=7d
sudo find /var/log -name "*.log" -mtime +30 -delete
```

### Performance issues

```bash
# Check CPU and RAM
top
htop

# Check disk I/O
iostat -x 1

# Check network connections
sudo netstat -tunap | grep ESTABLISHED | wc -l

# Check slow PostgreSQL queries
sudo -u postgres psql -d myapp_production -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"
```

### Port in use

```bash
# Find the process using the port
sudo lsof -i :8000
sudo netstat -tlnp | grep :8000

# Kill the process
sudo kill -9 [PID]
```

## Getting Help

If the problem is not resolved:

1. Collect the complete logs
2. Check the system settings
3. Check the software versions
4. Contact the development team

---

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [systemd Documentation](https://www.freedesktop.org/software/systemd/man/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/docs/)

---

**Last Updated**: 2025-10-21
**Version**: 1.0
