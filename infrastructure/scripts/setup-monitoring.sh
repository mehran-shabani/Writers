#!/bin/bash
set -e

# Setup monitoring and logging infrastructure
# Installs and configures Prometheus, Grafana, and Loki

echo "==================================="
echo "Monitoring Setup Script"
echo "==================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

# Create log directories
echo -e "${YELLOW}Creating log directories...${NC}"
mkdir -p /var/log/writers/{fastapi,celery}
chown -R www-data:www-data /var/log/writers

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Installing Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl enable docker
    systemctl start docker
fi

# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}Installing Docker Compose...${NC}"
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Create Docker network if it doesn't exist
if ! docker network ls | grep -q app-network; then
    echo -e "${YELLOW}Creating Docker network...${NC}"
    docker network create app-network
fi

# Start monitoring stack
echo -e "${YELLOW}Starting monitoring services...${NC}"
cd "$(dirname "$0")/../"
docker-compose -f docker-compose.monitoring.yml up -d

# Wait for services to be ready
echo -e "${YELLOW}Waiting for services to start...${NC}"
sleep 10

# Check service health
echo -e "${YELLOW}Checking service health...${NC}"

if curl -sf http://localhost:9090/-/healthy > /dev/null; then
    echo -e "${GREEN}✓ Prometheus is running${NC}"
else
    echo "✗ Prometheus failed to start"
    exit 1
fi

if curl -sf http://localhost:3001/api/health > /dev/null; then
    echo -e "${GREEN}✓ Grafana is running${NC}"
else
    echo "✗ Grafana failed to start"
    exit 1
fi

if curl -sf http://localhost:3100/ready > /dev/null; then
    echo -e "${GREEN}✓ Loki is running${NC}"
else
    echo "✗ Loki failed to start"
    exit 1
fi

echo ""
echo -e "${GREEN}==================================="
echo "Monitoring Setup Complete!"
echo "===================================${NC}"
echo ""
echo "Access the following services:"
echo "  Prometheus:  http://localhost:9090"
echo "  Grafana:     http://localhost:3001 (admin/admin)"
echo "  Alertmanager: http://localhost:9093"
echo ""
echo "Log in to Grafana and explore the dashboards!"
echo ""
