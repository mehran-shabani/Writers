#!/bin/bash
# =============================================================================
# Quick Start Script for Docker Compose Deployment
# =============================================================================
# This script automates the setup and launch of the application using
# Docker Compose.
#
# Usage:
#   chmod +x quick-start-docker.sh
#   ./quick-start-docker.sh
# =============================================================================

set -e  # Exit immediately if a command exits with a non-zero status.

# Colors for output messages.
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions for printing formatted messages.
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

# Check if the script is run as root.
if [ "$EUID" -eq 0 ]; then
   error "Please run this script without sudo."
   exit 1
fi

info "Starting the quick setup for the application with Docker Compose..."
echo ""

# Check for Docker installation.
info "Checking for Docker installation..."
if ! command -v docker &> /dev/null; then
    error "Docker is not installed. Please install Docker first."
    echo "Installation guide: https://docs.docker.com/engine/install/"
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    error "Docker Compose is not installed."
    exit 1
fi

success "Docker and Docker Compose are installed."
docker --version
docker compose version
echo ""

# Check for the .env file.
info "Checking for the environment variables file..."
if [ ! -f "../.env" ]; then
    warning ".env file not found. Creating from .env.example..."
    if [ -f "../.env.example" ]; then
        cp ../.env.example ../.env
        warning ".env file created. Please set the passwords."
        echo ""
        echo "To generate a secure password:"
        echo "  openssl rand -base64 48"
        echo ""
        read -p "Do you want to continue? (y/n) " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        error ".env.example file not found."
        exit 1
    fi
else
    success ".env file is present."
fi
echo ""

# Check for the .env file in the infrastructure directory.
info "Checking for the .env file in the infrastructure directory..."
if [ ! -f ".env" ]; then
    if [ -f ".env.docker" ]; then
        info "Copying .env.docker to .env..."
        cp .env.docker .env
        warning "Please edit the infrastructure/.env file."
    fi
fi
echo ""

# Check for the storage directory.
info "Checking for the /storage directory..."
if [ ! -d "/storage" ]; then
    warning "/storage does not exist."
    warning "If you have a separate storage device, mount it first:"
    echo "  sudo STORAGE_DEVICE=/dev/sdX1 ./setup_storage.sh"
    echo ""
    read -p "Do you want to continue with a temporary directory? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        info "Creating /tmp/storage as a temporary directory..."
        mkdir -p /tmp/storage/uploads /tmp/storage/results
        warning "In production, be sure to use a separate disk."
    else
        exit 1
    fi
else
    success "/storage is present."
fi
echo ""

# Check for the SSD for PostgreSQL.
info "Checking for the SSD for PostgreSQL..."
SSD_PATH="${SSD_MOUNT_POINT:-/mnt/ssd}"
if [ ! -d "$SSD_PATH/postgresql/data" ]; then
    warning "$SSD_PATH/postgresql/data does not exist."
    info "Creating PostgreSQL data directory..."
    sudo mkdir -p "$SSD_PATH/postgresql/data"
    sudo chown -R 999:999 "$SSD_PATH/postgresql/data"  # PostgreSQL UID in Docker
    sudo chmod 700 "$SSD_PATH/postgresql/data"
    success "Directory created."
else
    success "PostgreSQL data directory is present."
fi
echo ""

# Pull base images.
info "Downloading Docker images..."
docker compose pull postgres redis || true
echo ""

# Build application images.
info "Building application images..."
if [ -d "../backend" ] && [ -f "../backend/Dockerfile" ]; then
    info "Building backend..."
    docker compose build backend
else
    warning "Dockerfile for backend not found - an image will be used."
fi

if [ -d "../frontend" ] && [ -f "../frontend/Dockerfile" ]; then
    info "Building frontend..."
    docker compose build frontend
else
    warning "Dockerfile for frontend not found - an image will be used."
fi

if [ -d "../worker" ] && [ -f "../worker/Dockerfile" ]; then
    info "Building worker..."
    docker compose build worker
else
    warning "Dockerfile for worker not found - an image will be used."
fi
echo ""

# Run services.
info "Running services..."
docker compose up -d
echo ""

# Wait for services to be ready.
info "Waiting for services to be ready (30 seconds)..."
sleep 30
echo ""

# Check status.
info "Checking the status of services..."
docker compose ps
echo ""

# Display recent logs.
info "Recent logs:"
docker compose logs --tail=20
echo ""

# Test the health of services.
echo "=================================="
info "Testing the health of services:"
echo "=================================="

# PostgreSQL
if docker compose exec -T postgres pg_isready &> /dev/null; then
    success "✓ PostgreSQL: Ready"
else
    error "✗ PostgreSQL: Has issues"
fi

# Redis
if docker compose exec -T redis redis-cli ping &> /dev/null; then
    success "✓ Redis: Ready"
else
    error "✗ Redis: Has issues"
fi

# Backend (if it has a health endpoint)
if command -v curl &> /dev/null; then
    if curl -f -s http://localhost:8000/health &> /dev/null; then
        success "✓ Backend: Ready"
    else
        warning "✗ Backend: Starting up or has issues"
    fi
fi

# Frontend
if command -v curl &> /dev/null; then
    if curl -f -s http://localhost:3000 &> /dev/null; then
        success "✓ Frontend: Ready"
    else
        warning "✗ Frontend: Starting up or has issues"
    fi
fi

echo ""
echo "=================================="
success "Setup complete!"
echo "=================================="
echo ""
echo "Access the services:"
echo "  - Frontend:  http://localhost:3000"
echo "  - Backend:   http://localhost:8000"
echo "  - PostgreSQL: localhost:5432 (in Docker network only)"
echo "  - Redis:      localhost:6379 (in Docker network only)"
echo ""
echo "Useful commands:"
echo "  - View logs:        docker compose logs -f"
echo "  - Check status:          docker compose ps"
echo "  - Restart a service:      docker compose restart [service]"
echo "  - Stop:           docker compose stop"
echo "  - Remove services:         docker compose down"
echo ""
echo "For more details: cat DEPLOYMENT.md"
echo ""
