# Quick Start Guide

This guide is for quickly setting up the application with Docker Compose.

---

## ⚡ Quick Start with the Automated Script

```bash
cd /workspace/infrastructure
chmod +x quick-start-docker.sh
./quick-start-docker.sh
```

This script automatically:
- ✅ Checks for Docker and Docker Compose
- ✅ Creates `.env` files
- ✅ Creates the necessary directories
- ✅ Builds the images
- ✅ Runs all services
- ✅ Tests the health of the services

---

## 📝 Manual Steps

If you prefer to perform the steps manually:

### Step 1: Configure Environment Variables

```bash
# Project root
cd /workspace
cp .env.example .env
nano .env  # Edit and set passwords

# Infrastructure
cd infrastructure
cp .env.docker .env
nano .env  # Set secure passwords
```

**Be sure to change these values:**
- `POSTGRES_PASSWORD`
- `REDIS_PASSWORD`
- `JWT_SECRET`
- `JWT_REFRESH_SECRET`
- `SESSION_SECRET`

**To generate a secure password:**
```bash
openssl rand -base64 48
```

### Step 2: Prepare the Infrastructure

If this is a new server:

```bash
cd /workspace/infrastructure

# PostgreSQL on SSD
sudo ./setup_postgresql.sh

# Redis
sudo ./setup_redis.sh

# Storage (100TB storage space)
# First, identify the device: lsblk
sudo STORAGE_DEVICE=/dev/sdX1 ./setup_storage.sh
```

### Step 3: Run Docker Compose

```bash
cd /workspace/infrastructure

# Build and run
docker compose build
docker compose up -d

# Check the status
docker compose ps

# View the logs
docker compose logs -f
```

### Step 4: Test

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

## 🎯 Accessing the Services

After a successful launch:

| Service | URL | Description |
|---|---|---|
| Frontend | http://localhost:3000 | Web user interface |
| Backend API | http://localhost:8000 | API server |
| PostgreSQL | localhost:5432 | In Docker network only |
| Redis | localhost:6379 | In Docker network only |

---

## 🛠️ Useful Commands

### Service Management

```bash
# View status
docker compose ps

# View logs
docker compose logs -f

# Log a specific service
docker compose logs -f backend

# Restart a service
docker compose restart backend

# Restart all
docker compose restart

# Stop
docker compose stop

# Remove services (data is preserved)
docker compose down

# Remove with volumes (dangerous - all data is deleted!)
docker compose down -v
```

### Monitoring

```bash
# Resource consumption
docker stats

# Disk space used
docker system df

# Check health
docker compose ps

# Access the shell of a container
docker compose exec backend sh
docker compose exec postgres psql -U myapp_user -d myapp_db
```

### Scaling the Worker

```bash
# Run 3 instances of the worker
docker compose up -d --scale worker=3

# Check
docker compose ps worker
```

---

## 🐛 Troubleshooting

### Service does not start

```bash
# Check detailed logs
docker compose logs backend

# Check status
docker compose ps

# Restart with rebuild
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Database connection error

```bash
# Check PostgreSQL health
docker compose exec postgres pg_isready

# Check environment variables
docker compose exec backend env | grep POSTGRES

# Direct connection
docker compose exec postgres psql -U myapp_user -d myapp_db
```

### Disk space full

```bash
# Clean up old images and containers
docker system prune -a

# Remove unused volumes (caution!)
docker volume prune
```

### Port in use

```bash
# Find the process
sudo lsof -i :8000

# Or change the port in .env
BACKEND_PORT=8001
docker compose up -d
```

---

## 🔒 Security Tips

### ✅ Do:

1. **Use strong passwords**
   ```bash
   openssl rand -base64 48
   ```

2. **Do not commit `.env` files**
   ```bash
   # Check before commit
   git status
   ```

3. **Use a firewall for production**
   ```bash
   # Open only necessary ports
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

4. **Update regularly**
   ```bash
   docker compose pull
   docker compose up -d
   ```

### ❌ Do not:

- ❌ Do not use default passwords
- ❌ Do not expose database ports to the internet
- ❌ Do not make significant changes without a backup

---

## 📚 More Resources

- **[DEPLOYMENT.md](DEPLOYMENT.md)**: Complete deployment guide
- **[SYSTEMD_SERVICES.md](SYSTEMD_SERVICES.md)**: systemd alternative
- **[../ENV_SETUP.md](../ENV_SETUP.md)**: Environment variables guide
- **[README.md](README.md)**: General infrastructure information

---

## 🆘 Need Help?

If you have a problem:

1. Check the logs: `docker compose logs -f`
2. Read the full documentation: `cat DEPLOYMENT.md`
3. Restart the services: `docker compose restart`
4. Contact the development team

---

**Good luck! 🚀**
