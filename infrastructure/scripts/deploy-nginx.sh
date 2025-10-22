#!/bin/bash
set -e

# Safe Nginx deployment and reload script
# Validates configuration and performs health checks

echo "==================================="
echo "Nginx Deployment Script"
echo "==================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
NGINX_CONF_SOURCE="${1:-../nginx/nginx.conf}"
NGINX_CONF_DEST="/etc/nginx/sites-available/writers"
NGINX_CONF_ENABLED="/etc/nginx/sites-enabled/writers"
BACKUP_DIR="/var/backups/nginx"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root${NC}" 
   exit 1
fi

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Backup current configuration
if [ -f "$NGINX_CONF_DEST" ]; then
    echo -e "${YELLOW}Backing up current configuration...${NC}"
    cp "$NGINX_CONF_DEST" "$BACKUP_DIR/writers_$TIMESTAMP.conf"
    echo -e "${GREEN}Backup saved to: $BACKUP_DIR/writers_$TIMESTAMP.conf${NC}"
fi

# Copy new configuration
echo -e "${YELLOW}Copying new configuration...${NC}"
cp "$NGINX_CONF_SOURCE" "$NGINX_CONF_DEST"

# Enable site if not already enabled
if [ ! -L "$NGINX_CONF_ENABLED" ]; then
    echo -e "${YELLOW}Enabling site...${NC}"
    ln -s "$NGINX_CONF_DEST" "$NGINX_CONF_ENABLED"
fi

# Remove default site if exists
if [ -L "/etc/nginx/sites-enabled/default" ]; then
    echo -e "${YELLOW}Removing default site...${NC}"
    rm /etc/nginx/sites-enabled/default
fi

# Test configuration
echo -e "${YELLOW}Testing Nginx configuration...${NC}"
if nginx -t; then
    echo -e "${GREEN}Configuration test passed${NC}"
else
    echo -e "${RED}Configuration test failed!${NC}"
    echo -e "${YELLOW}Restoring backup...${NC}"
    cp "$BACKUP_DIR/writers_$TIMESTAMP.conf" "$NGINX_CONF_DEST"
    exit 1
fi

# Check if services are running
echo -e "${YELLOW}Checking service health...${NC}"

# Check Next.js
if curl -s -f http://localhost:3000 > /dev/null; then
    echo -e "${GREEN}✓ Next.js is running${NC}"
else
    echo -e "${RED}✗ Next.js is not responding on port 3000${NC}"
    echo -e "${YELLOW}Please start Next.js before proceeding${NC}"
    exit 1
fi

# Check FastAPI
if curl -s -f http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✓ FastAPI is running${NC}"
else
    echo -e "${RED}✗ FastAPI is not responding on port 8000${NC}"
    echo -e "${YELLOW}Please start FastAPI before proceeding${NC}"
    exit 1
fi

# Reload Nginx
echo -e "${YELLOW}Reloading Nginx...${NC}"
systemctl reload nginx

# Verify Nginx is running
if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✓ Nginx is running${NC}"
else
    echo -e "${RED}✗ Nginx failed to start${NC}"
    echo -e "${YELLOW}Restoring backup...${NC}"
    cp "$BACKUP_DIR/writers_$TIMESTAMP.conf" "$NGINX_CONF_DEST"
    systemctl reload nginx
    exit 1
fi

# Final health check
echo -e "${YELLOW}Performing final health check...${NC}"
sleep 2

if curl -s -f http://localhost/health > /dev/null; then
    echo -e "${GREEN}✓ Nginx health check passed${NC}"
else
    echo -e "${RED}✗ Nginx health check failed${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}==================================="
echo "Deployment Successful!"
echo "===================================${NC}"
echo "Configuration: $NGINX_CONF_DEST"
echo "Backup: $BACKUP_DIR/writers_$TIMESTAMP.conf"
echo ""
echo "View logs:"
echo "  Access: tail -f /var/log/nginx/writers_access.log"
echo "  Error:  tail -f /var/log/nginx/writers_error.log"
echo ""
