# systemd Service Guide

This document contains systemd service files for running the application directly on a server.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Service Files](#service-files)
  - [Backend Service](#backend-service)
  - [Frontend Service](#frontend-service)
  - [Worker Service](#worker-service)
- [Installation and Setup](#installation-and-setup)
- [Service Management](#service-management)
- [Security Notes](#security-notes)

---

## Overview

These systemd service files are designed for running the application natively on a Linux server. Each service:

- Starts automatically with the system
- Restarts automatically in case of an error
- Has resource limits (CPU, Memory)
- Has security settings
- Stores logs

---

## Prerequisites

Before using these services:

1. **Set up the infrastructure**:
   ```bash
   cd /workspace/infrastructure
   sudo ./setup_postgresql.sh
   sudo ./setup_redis.sh
   sudo STORAGE_DEVICE=/dev/sdX1 ./setup_storage.sh
   ```

2. **Install Node.js**:
   ```bash
   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
   sudo apt-get install -y nodejs
   ```

3. **Build the application**:
   ```bash
   cd /workspace/backend && npm install && npm run build
   cd /workspace/frontend && npm install && npm run build
   cd /workspace/worker && npm install && npm run build
   ```

4. **Create a log directory**:
   ```bash
   sudo mkdir -p /var/log/app
   sudo chown www-data:www-data /var/log/app
   ```

5. **Configure the `.env` files**:
   ```bash
   cp /workspace/.env.example /workspace/.env
   # Then edit
   ```

---

## Service Files

### Backend Service

**Path**: `/etc/systemd/system/app-backend.service`

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

# Load environment variables from files
EnvironmentFile=/workspace/.env
EnvironmentFile=/workspace/backend/.env

# Direct environment variables
Environment="NODE_ENV=production"
Environment="POSTGRES_HOST=localhost"
Environment="REDIS_HOST=localhost"
Environment="PORT=8000"

# Execution command
# If you have built TypeScript:
ExecStart=/usr/bin/node /workspace/backend/dist/index.js
# If you are running directly from the source:
# ExecStart=/usr/bin/node /workspace/backend/src/index.js
# If you are using PM2:
# ExecStart=/usr/bin/pm2 start /workspace/backend/ecosystem.config.js --no-daemon

# Automatic restart in case of an error
Restart=always
RestartSec=10
StartLimitBurst=5

# Log management
StandardOutput=append:/var/log/app/backend.log
StandardError=append:/var/log/app/backend-error.log
SyslogIdentifier=app-backend

# Security - Hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/storage /var/log/app /tmp
ProtectKernelTunables=true
ProtectControlGroups=true
RestrictRealtime=true
RestrictNamespaces=true

# Resource limits
LimitNOFILE=65536
LimitNPROC=512
MemoryMax=2G
MemoryHigh=1536M
CPUQuota=200%
TasksMax=512

# Timeouts
TimeoutStartSec=60
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
```

### Frontend Service

**Path**: `/etc/systemd/system/app-frontend.service`

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

# Load environment variables
EnvironmentFile=/workspace/.env
EnvironmentFile=/workspace/frontend/.env.local

# Environment variables
Environment="NODE_ENV=production"
Environment="PORT=3000"

# Execution command
# For Next.js:
ExecStart=/usr/bin/npm start
# Or if you have a standalone build:
# ExecStart=/usr/bin/node /workspace/frontend/.next/standalone/server.js
# For Vite/React with serve:
# ExecStart=/usr/bin/npx serve -s /workspace/frontend/dist -l 3000

# Automatic restart
Restart=always
RestartSec=10
StartLimitBurst=5

# Log management
StandardOutput=append:/var/log/app/frontend.log
StandardError=append:/var/log/app/frontend-error.log
SyslogIdentifier=app-frontend

# Security - Hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/log/app
ProtectKernelTunables=true
ProtectControlGroups=true
RestrictRealtime=true

# Resource limits
LimitNOFILE=65536
MemoryMax=1G
MemoryHigh=768M
CPUQuota=100%
TasksMax=256

# Timeouts
TimeoutStartSec=90
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
```

### Worker Service

**Path**: `/etc/systemd/system/app-worker.service`

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

# Load environment variables
EnvironmentFile=/workspace/.env
EnvironmentFile=/workspace/worker/.env

# Environment variables
Environment="NODE_ENV=production"
Environment="POSTGRES_HOST=localhost"
Environment="REDIS_HOST=localhost"
Environment="WORKER_CONCURRENCY=5"
Environment="WORKER_MAX_RETRIES=3"

# Execution command
ExecStart=/usr/bin/node /workspace/worker/dist/index.js
# Or:
# ExecStart=/usr/bin/node /workspace/worker/src/index.js

# Automatic restart
Restart=always
RestartSec=10
StartLimitBurst=5

# Log management
StandardOutput=append:/var/log/app/worker.log
StandardError=append:/var/log/app/worker-error.log
SyslogIdentifier=app-worker

# Security - Hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/storage /var/log/app /tmp
ProtectKernelTunables=true
ProtectControlGroups=true
RestrictRealtime=true
RestrictNamespaces=true

# Resource limits (Worker usually needs more resources)
LimitNOFILE=65536
LimitNPROC=1024
MemoryMax=4G
MemoryHigh=3G
CPUQuota=400%
TasksMax=1024

# Timeouts
TimeoutStartSec=60
TimeoutStopSec=60

[Install]
WantedBy=multi-user.target
```

---

## Installation and Setup

### Step 1: Copy Service Files

```bash
# Create service files
sudo nano /etc/systemd/system/app-backend.service
# Paste the content above

sudo nano /etc/systemd/system/app-frontend.service
# Paste the content above

sudo nano /etc/systemd/system/app-worker.service
# Paste the content above
```

Or you can use a script:

```bash
# Run the installation script (if it exists)
cd /workspace/infrastructure
sudo ./install-systemd-services.sh
```

### Step 2: Set Permissions

```bash
# Permissions for service files
sudo chmod 644 /etc/systemd/system/app-*.service

# Permissions for application files
sudo chown -R www-data:www-data /workspace/backend
sudo chown -R www-data:www-data /workspace/frontend
sudo chown -R www-data:www-data /workspace/worker

# Permissions for .env files (protect sensitive information)
sudo chmod 640 /workspace/.env
sudo chmod 640 /workspace/backend/.env
sudo chmod 640 /workspace/frontend/.env.local
sudo chmod 640 /workspace/worker/.env
sudo chown www-data:www-data /workspace/.env
sudo chown www-data:www-data /workspace/backend/.env
sudo chown www-data:www-data /workspace/frontend/.env.local
sudo chown www-data:www-data /workspace/worker/.env
```

### Step 3: Enable and Start Services

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable to start automatically with the system
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

### Step 4: Test and Check

```bash
# Test Backend API
curl http://localhost:8000/health

# Test Frontend
curl http://localhost:3000

# Check logs
sudo journalctl -u app-backend.service -f
sudo journalctl -u app-frontend.service -f
sudo journalctl -u app-worker.service -f

# Or file logs
tail -f /var/log/app/backend.log
tail -f /var/log/app/frontend.log
tail -f /var/log/app/worker.log
```

---

## Service Management

### Main Commands

```bash
# Start a service
sudo systemctl start app-backend.service

# Stop
sudo systemctl stop app-backend.service

# Restart
sudo systemctl restart app-backend.service

# Reload (if the service supports SIGHUP)
sudo systemctl reload app-backend.service

# Check status
sudo systemctl status app-backend.service

# Enable (start automatically with the system)
sudo systemctl enable app-backend.service

# Disable
sudo systemctl disable app-backend.service

# View log
sudo journalctl -u app-backend.service

# View real-time log
sudo journalctl -u app-backend.service -f

# View the last 100 lines of the log
sudo journalctl -u app-backend.service -n 100

# Logs from today
sudo journalctl -u app-backend.service --since today

# Logs from the last hour
sudo journalctl -u app-backend.service --since "1 hour ago"
```

### Managing All Services at Once

```bash
# Start all services
sudo systemctl start app-backend.service app-frontend.service app-worker.service

# Restart all
sudo systemctl restart app-backend.service app-frontend.service app-worker.service

# Status of all
systemctl status 'app-*'

# List all application services
systemctl list-units --type=service | grep app-
```

### Viewing Resource Consumption

```bash
# Resources used by the service
systemd-cgtop

# Details of a specific service
systemctl show app-backend.service --property=CPUUsageNSec,MemoryCurrent

# Detailed status
systemctl status app-backend.service -l --no-pager
```

---

## Security Notes

### Hardening Options in Service Files

The service files above include the following security settings:

1. **NoNewPrivileges=true**
   - Prevents privilege escalation

2. **PrivateTmp=true**
   - Separate `/tmp` directory for each service

3. **ProtectSystem=strict**
   - Only specified paths are writable

4. **ProtectHome=true**
   - Access to home directories is protected

5. **ReadWritePaths=...**
   - Only specified paths are writable

6. **Resource limits**:
   - `MemoryMax`: Maximum memory
   - `CPUQuota`: Maximum CPU
   - `LimitNOFILE`: Maximum number of open files
   - `TasksMax`: Maximum number of tasks

### Checking Service Security

```bash
# Analyze service security
systemd-analyze security app-backend.service

# Show security settings
systemctl show app-backend.service | grep -i protect
systemctl show app-backend.service | grep -i private

# Test settings
sudo systemd-analyze verify /etc/systemd/system/app-backend.service
```

### Protecting `.env` Files

```bash
# Secure permissions for .env
sudo chmod 640 /workspace/.env
sudo chown www-data:www-data /workspace/.env

# Prevent reading by other users
ls -la /workspace/.env
# Should show: -rw-r----- 1 www-data www-data

# Audit changes
sudo auditctl -w /workspace/.env -p war -k env_file_changes
```

---

## Troubleshooting

### Service does not start

```bash
# Check for detailed errors
sudo systemctl status app-backend.service -l

# Complete logs
sudo journalctl -u app-backend.service -n 200 --no-pager

# Check the syntax of the service file
sudo systemd-analyze verify /etc/systemd/system/app-backend.service

# Test manual execution
cd /workspace/backend
sudo -u www-data /usr/bin/node dist/index.js
```

### Service stops after a while

```bash
# Check crash logs
sudo journalctl -u app-backend.service --since "1 hour ago"

# Check the memory limit
systemctl status app-backend.service | grep Memory

# Increase the memory limit in the service file
# MemoryMax=4G  # Instead of 2G
sudo systemctl daemon-reload
sudo systemctl restart app-backend.service
```

### Permission problems

```bash
# Check permissions
ls -la /workspace/backend
ls -la /workspace/.env
ls -la /var/log/app

# Reset permissions
sudo chown -R www-data:www-data /workspace/backend
sudo chmod -R 755 /workspace/backend
sudo chmod 640 /workspace/.env

# Test access
sudo -u www-data ls -la /workspace/backend
sudo -u www-data cat /workspace/.env
```

### Manual execution for debug

```bash
# Stop the service
sudo systemctl stop app-backend.service

# Manual execution with the www-data user
cd /workspace/backend
sudo -u www-data bash -c 'source /workspace/.env && source /workspace/backend/.env && node dist/index.js'

# Or with direct variables
sudo -u www-data \
  NODE_ENV=production \
  POSTGRES_HOST=localhost \
  node dist/index.js
```

---

## Helper Scripts

### Automatic Installation Script

Create the file `/workspace/infrastructure/install-systemd-services.sh`:

```bash
#!/bin/bash
set -e

echo "Installing systemd service files..."

# Copy service files
sudo cp /workspace/infrastructure/systemd/app-backend.service /etc/systemd/system/
sudo cp /workspace/infrastructure/systemd/app-frontend.service /etc/systemd/system/
sudo cp /workspace/infrastructure/systemd/app-worker.service /etc/systemd/system/

# Set permissions
sudo chmod 644 /etc/systemd/system/app-*.service

# Reload systemd
sudo systemctl daemon-reload

echo "Service files installed successfully!"
echo "To enable and start services, run:"
echo "  sudo systemctl enable app-backend.service app-frontend.service app-worker.service"
echo "  sudo systemctl start app-backend.service app-frontend.service app-worker.service"
```

### Service Management Script

Create the file `/workspace/infrastructure/manage-services.sh`:

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

Usage:

```bash
chmod +x /workspace/infrastructure/manage-services.sh

# Start all services
./manage-services.sh start

# View logs
./manage-services.sh logs

# Restart
./manage-services.sh restart
```

---

## Resources

- [systemd Service Documentation](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
- [systemd Security Features](https://www.freedesktop.org/software/systemd/man/systemd.exec.html#Sandboxing)
- [Best Practices for Writing systemd Services](https://www.digitalocean.com/community/tutorials/understanding-systemd-units-and-unit-files)

---

**Final Note**: These service files are optimized for a production environment. In a development environment, you may want to:
- Reduce resource limits
- Disable hardening options
- Increase the log level (`LOG_LEVEL=debug`)

**Last Updated**: 2025-10-21
**Version**: 1.0
