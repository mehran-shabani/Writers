#!/bin/bash
set -e

# Setup SSL certificates with Let's Encrypt Certbot
# This script automates SSL certificate installation and renewal configuration

DOMAIN="${1:-yourdomain.com}"
EMAIL="${2:-admin@yourdomain.com}"

echo "==================================="
echo "SSL Certificate Setup with Certbot"
echo "==================================="
echo "Domain: $DOMAIN"
echo "Email: $EMAIL"
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

# Install Certbot if not already installed
echo "Checking Certbot installation..."
if ! command -v certbot &> /dev/null; then
    echo "Installing Certbot..."
    apt-get update
    apt-get install -y certbot python3-certbot-nginx
else
    echo "Certbot is already installed"
fi

# Create webroot directory for ACME challenge
echo "Creating webroot directory..."
mkdir -p /var/www/certbot

# Update Nginx configuration with actual domain
echo "Updating Nginx configuration with domain: $DOMAIN"
sed -i "s/yourdomain.com/$DOMAIN/g" /etc/nginx/sites-available/writers

# Test Nginx configuration
echo "Testing Nginx configuration..."
nginx -t

# Reload Nginx
echo "Reloading Nginx..."
systemctl reload nginx

# Obtain SSL certificate
echo "Obtaining SSL certificate..."
certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    --force-renewal \
    -d "$DOMAIN" \
    -d "www.$DOMAIN"

# Update Nginx configuration to use the new certificate
echo "Configuring Nginx to use SSL certificate..."
systemctl reload nginx

# Setup automatic renewal
echo "Setting up automatic certificate renewal..."
cat > /etc/cron.d/certbot-renew << EOF
# Renew Let's Encrypt certificates twice daily
0 */12 * * * root certbot renew --quiet --deploy-hook "systemctl reload nginx"
EOF

echo ""
echo "==================================="
echo "SSL Setup Complete!"
echo "==================================="
echo "Certificate location: /etc/letsencrypt/live/$DOMAIN/"
echo "Renewal cron job installed"
echo ""
echo "Test your SSL configuration at:"
echo "https://www.ssllabs.com/ssltest/analyze.html?d=$DOMAIN"
echo ""
