#!/bin/bash
set -e

# Persistent 100TB Storage Mount Setup
# This script configures persistent mounting of large storage to /storage

echo "=== Storage Mount and Configuration Setup ==="

# Configuration variables
STORAGE_DEVICE="${STORAGE_DEVICE:-/dev/sdb1}"
STORAGE_MOUNT_POINT="/storage"
FS_TYPE="${FS_TYPE:-ext4}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root or with sudo"
    exit 1
fi

echo "Storage device: $STORAGE_DEVICE"
echo "Mount point: $STORAGE_MOUNT_POINT"
echo "Filesystem type: $FS_TYPE"
echo ""

# Check if device exists
if [ ! -b "$STORAGE_DEVICE" ]; then
    echo "Warning: Block device $STORAGE_DEVICE does not exist"
    echo "Available block devices:"
    lsblk
    echo ""
    echo "Please set STORAGE_DEVICE environment variable to the correct device"
    echo "Example: export STORAGE_DEVICE=/dev/sdb1"
    exit 1
fi

# Create mount point if it doesn't exist
if [ ! -d "$STORAGE_MOUNT_POINT" ]; then
    echo "Creating mount point $STORAGE_MOUNT_POINT..."
    mkdir -p "$STORAGE_MOUNT_POINT"
fi

# Check if device is already formatted
CURRENT_FS=$(blkid -o value -s TYPE "$STORAGE_DEVICE" 2>/dev/null || echo "")

if [ -z "$CURRENT_FS" ]; then
    echo "Device is not formatted. Formatting as $FS_TYPE..."
    echo "WARNING: This will erase all data on $STORAGE_DEVICE"
    read -p "Continue? (yes/no): " -r
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        echo "Aborted"
        exit 1
    fi
    
    mkfs.$FS_TYPE -F "$STORAGE_DEVICE"
    echo "✓ Device formatted successfully"
else
    echo "Device is already formatted as $CURRENT_FS"
fi

# Get UUID of the device for persistent mounting
DEVICE_UUID=$(blkid -s UUID -o value "$STORAGE_DEVICE")
echo "Device UUID: $DEVICE_UUID"

# Check if already mounted
if mountpoint -q "$STORAGE_MOUNT_POINT"; then
    echo "Warning: $STORAGE_MOUNT_POINT is already mounted"
    echo "Unmounting..."
    umount "$STORAGE_MOUNT_POINT"
fi

# Mount the device
echo "Mounting $STORAGE_DEVICE to $STORAGE_MOUNT_POINT..."
mount "$STORAGE_DEVICE" "$STORAGE_MOUNT_POINT"

# Verify mount
if mountpoint -q "$STORAGE_MOUNT_POINT"; then
    echo "✓ Device mounted successfully"
    df -h "$STORAGE_MOUNT_POINT"
else
    echo "✗ Failed to mount device"
    exit 1
fi

# Create subdirectories
echo ""
echo "Creating subdirectories..."
mkdir -p "$STORAGE_MOUNT_POINT/uploads"
mkdir -p "$STORAGE_MOUNT_POINT/results"

# Set permissions
echo "Setting permissions..."

# uploads directory - writable by www-data (web server) and specific users
chown -R www-data:www-data "$STORAGE_MOUNT_POINT/uploads"
chmod 755 "$STORAGE_MOUNT_POINT/uploads"

# results directory - readable by all, writable by owner
chown -R root:root "$STORAGE_MOUNT_POINT/results"
chmod 755 "$STORAGE_MOUNT_POINT/results"

# Set sticky bit on uploads to prevent users from deleting others' files
chmod +t "$STORAGE_MOUNT_POINT/uploads"

echo "✓ Subdirectories created and permissions set"

# Add to /etc/fstab for persistent mounting
FSTAB_ENTRY="UUID=$DEVICE_UUID $STORAGE_MOUNT_POINT $FS_TYPE defaults,nofail 0 2"

# Backup fstab
cp /etc/fstab /etc/fstab.backup.$(date +%Y%m%d_%H%M%S)

# Check if entry already exists
if grep -q "$DEVICE_UUID" /etc/fstab; then
    echo "Warning: Entry for this device already exists in /etc/fstab"
    echo "Existing entry:"
    grep "$DEVICE_UUID" /etc/fstab
else
    echo "Adding entry to /etc/fstab for persistent mounting..."
    echo "$FSTAB_ENTRY" >> /etc/fstab
    echo "✓ Entry added to /etc/fstab"
fi

# Verify fstab entry
echo ""
echo "Verifying fstab configuration..."
if mount -a; then
    echo "✓ fstab configuration is valid"
else
    echo "✗ Error in fstab configuration"
    echo "Restoring backup..."
    cp /etc/fstab.backup.$(date +%Y%m%d_%H%M%S) /etc/fstab
    exit 1
fi

# Display final status
echo ""
echo "=== Storage Setup Complete ==="
echo "Mount point: $STORAGE_MOUNT_POINT"
echo "Device: $STORAGE_DEVICE (UUID: $DEVICE_UUID)"
echo "Filesystem: $FS_TYPE"
echo ""
echo "Subdirectories created:"
echo "  - $STORAGE_MOUNT_POINT/uploads/ (owner: www-data, mode: 755, sticky bit enabled)"
echo "  - $STORAGE_MOUNT_POINT/results/ (owner: root, mode: 755)"
echo ""
echo "Storage usage:"
df -h "$STORAGE_MOUNT_POINT"
echo ""
echo "Directory structure:"
ls -lah "$STORAGE_MOUNT_POINT"
