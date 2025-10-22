#!/bin/bash

# Comprehensive health check script for all services
# Can be used for monitoring and automated checks

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
NEXTJS_URL="${NEXTJS_URL:-http://localhost:3000}"
FASTAPI_URL="${FASTAPI_URL:-http://localhost:8000}"
NGINX_URL="${NGINX_URL:-http://localhost}"
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_DB="${POSTGRES_DB:-writers_db}"
POSTGRES_USER="${POSTGRES_USER:-writers_user}"

# Exit code tracking
EXIT_CODE=0

echo "==================================="
echo "Service Health Check"
echo "==================================="
echo ""

# Check Nginx
echo -n "Nginx:          "
if curl -sf "$NGINX_URL/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Running${NC}"
else
    echo -e "${RED}✗ Down${NC}"
    EXIT_CODE=1
fi

# Check Next.js
echo -n "Next.js:        "
if curl -sf "$NEXTJS_URL" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Running${NC}"
else
    echo -e "${RED}✗ Down${NC}"
    EXIT_CODE=1
fi

# Check FastAPI
echo -n "FastAPI:        "
if curl -sf "$FASTAPI_URL/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Running${NC}"
else
    echo -e "${RED}✗ Down${NC}"
    EXIT_CODE=1
fi

# Check Redis
echo -n "Redis:          "
if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Running${NC}"
else
    echo -e "${RED}✗ Down${NC}"
    EXIT_CODE=1
fi

# Check PostgreSQL
echo -n "PostgreSQL:     "
if pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Running${NC}"
else
    echo -e "${RED}✗ Down${NC}"
    EXIT_CODE=1
fi

# Check Celery Worker
echo -n "Celery Worker:  "
if pgrep -f "celery worker" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Running${NC}"
else
    echo -e "${RED}✗ Down${NC}"
    EXIT_CODE=1
fi

# Check Celery Beat (if used)
echo -n "Celery Beat:    "
if pgrep -f "celery beat" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Running${NC}"
else
    echo -e "${YELLOW}✗ Not Running (Optional)${NC}"
fi

echo ""
echo "==================================="

# System resources
echo "System Resources"
echo "==================================="

# Memory usage
TOTAL_MEM=$(free -h | awk '/^Mem:/ {print $2}')
USED_MEM=$(free -h | awk '/^Mem:/ {print $3}')
MEM_PERCENT=$(free | awk '/^Mem:/ {printf "%.1f", $3/$2 * 100}')
echo -n "Memory:         $USED_MEM / $TOTAL_MEM "
if (( $(echo "$MEM_PERCENT > 90" | bc -l) )); then
    echo -e "${RED}(${MEM_PERCENT}% - Critical)${NC}"
    EXIT_CODE=1
elif (( $(echo "$MEM_PERCENT > 75" | bc -l) )); then
    echo -e "${YELLOW}(${MEM_PERCENT}% - Warning)${NC}"
else
    echo -e "${GREEN}(${MEM_PERCENT}% - OK)${NC}"
fi

# Disk usage
DISK_PERCENT=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
DISK_USED=$(df -h / | awk 'NR==2 {print $3}')
DISK_TOTAL=$(df -h / | awk 'NR==2 {print $2}')
echo -n "Disk:           $DISK_USED / $DISK_TOTAL "
if [ "$DISK_PERCENT" -gt 90 ]; then
    echo -e "${RED}(${DISK_PERCENT}% - Critical)${NC}"
    EXIT_CODE=1
elif [ "$DISK_PERCENT" -gt 75 ]; then
    echo -e "${YELLOW}(${DISK_PERCENT}% - Warning)${NC}"
else
    echo -e "${GREEN}(${DISK_PERCENT}% - OK)${NC}"
fi

# CPU load
LOAD_AVG=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')
CPU_CORES=$(nproc)
echo "CPU Load:       $LOAD_AVG (${CPU_CORES} cores)"

# GPU check (if nvidia-smi available)
if command -v nvidia-smi &> /dev/null; then
    echo ""
    echo "GPU Status:"
    nvidia-smi --query-gpu=index,name,temperature.gpu,utilization.gpu,memory.used,memory.total --format=csv,noheader | while IFS=',' read -r idx name temp util mem_used mem_total; do
        echo "  GPU $idx: $name"
        echo "    Temperature: $temp"
        echo "    Utilization: $util"
        echo "    Memory: $mem_used / $mem_total"
    done
fi

echo "==================================="

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}All services are healthy${NC}"
else
    echo -e "${RED}Some services are down or resources are critical${NC}"
fi

exit $EXIT_CODE
