#!/bin/bash
set -e

# PostgreSQL Installation and Configuration on SSD
# This script installs PostgreSQL and configures it to use a separate SSD drive

echo "=== PostgreSQL Installation and Configuration on SSD ==="

# Configuration variables
SSD_MOUNT_POINT="${SSD_MOUNT_POINT:-/mnt/ssd}"
PG_DATA_DIR="${PG_DATA_DIR:-${SSD_MOUNT_POINT}/postgresql/data}"
PG_VERSION="${PG_VERSION:-15}"
PG_PORT="${PG_PORT:-5432}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root or with sudo"
    exit 1
fi

# Check if SSD mount point exists
if [ ! -d "$SSD_MOUNT_POINT" ]; then
    echo "Error: SSD mount point $SSD_MOUNT_POINT does not exist"
    echo "Please mount your SSD drive first or set SSD_MOUNT_POINT environment variable"
    exit 1
fi

echo "Installing PostgreSQL $PG_VERSION..."

# Update package lists
apt-get update

# Install PostgreSQL
apt-get install -y postgresql-$PG_VERSION postgresql-contrib-$PG_VERSION

# Stop PostgreSQL service
systemctl stop postgresql

echo "Configuring PostgreSQL to use SSD storage at $PG_DATA_DIR..."

# Create PostgreSQL data directory on SSD
mkdir -p "$PG_DATA_DIR"
chown -R postgres:postgres "$PG_DATA_DIR"
chmod 700 "$PG_DATA_DIR"

# Backup original data directory if it has data
ORIGINAL_DATA_DIR="/var/lib/postgresql/$PG_VERSION/main"
if [ -d "$ORIGINAL_DATA_DIR" ] && [ "$(ls -A $ORIGINAL_DATA_DIR)" ]; then
    echo "Backing up original data directory..."
    cp -a "$ORIGINAL_DATA_DIR"/* "$PG_DATA_DIR/"
else
    # Initialize new PostgreSQL cluster on SSD
    echo "Initializing new PostgreSQL cluster..."
    su - postgres -c "/usr/lib/postgresql/$PG_VERSION/bin/initdb -D $PG_DATA_DIR"
fi

# Update PostgreSQL configuration file
PG_CONFIG="/etc/postgresql/$PG_VERSION/main/postgresql.conf"

if [ -f "$PG_CONFIG" ]; then
    # Update data directory in config
    sed -i "s|^data_directory.*|data_directory = '$PG_DATA_DIR'|" "$PG_CONFIG"
    
    # Performance tuning for SSD
    cat >> "$PG_CONFIG" << EOF

# SSD-optimized settings
random_page_cost = 1.1
effective_io_concurrency = 200

# Memory settings (adjust based on available RAM)
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
work_mem = 16MB

# WAL settings
wal_buffers = 16MB
min_wal_size = 1GB
max_wal_size = 4GB

# Checkpoint settings
checkpoint_completion_target = 0.9
EOF

    echo "PostgreSQL configuration updated"
fi

# Update pg_hba.conf for local connections
PG_HBA="/etc/postgresql/$PG_VERSION/main/pg_hba.conf"
if [ -f "$PG_HBA" ]; then
    # Backup original
    cp "$PG_HBA" "$PG_HBA.backup"
    
    # Add secure local connections
    cat >> "$PG_HBA" << EOF

# Custom configuration
# Local connections
local   all             all                                     peer
host    all             all             127.0.0.1/32            scram-sha-256
host    all             all             ::1/128                 scram-sha-256
EOF
fi

# Set proper ownership
chown -R postgres:postgres "$PG_DATA_DIR"

# Start PostgreSQL
echo "Starting PostgreSQL..."
systemctl start postgresql
systemctl enable postgresql

# Verify installation
sleep 3
if systemctl is-active --quiet postgresql; then
    echo "✓ PostgreSQL is running successfully"
    su - postgres -c "psql -c 'SELECT version();'"
    echo ""
    echo "PostgreSQL data directory: $PG_DATA_DIR"
    echo "PostgreSQL version: $PG_VERSION"
    echo "PostgreSQL port: $PG_PORT"
else
    echo "✗ PostgreSQL failed to start"
    journalctl -xe | grep postgres | tail -20
    exit 1
fi

echo ""
echo "=== PostgreSQL Setup Complete ==="
echo "To create a database and user, run:"
echo "  sudo -u postgres createdb your_database"
echo "  sudo -u postgres psql -c \"CREATE USER your_user WITH PASSWORD 'your_password';\""
echo "  sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE your_database TO your_user;\""
