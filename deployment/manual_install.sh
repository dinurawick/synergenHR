#!/bin/bash

# Manual Installation Script for SynergenHR on EUK Cloud Linux

set -e

echo "🚀 Installing SynergenHR manually..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx redis-server

# Create application user
sudo useradd --system --shell /bin/bash --home /opt/synergenhr synergenhr

# Create application directory
sudo mkdir -p /opt/synergenhr
sudo chown synergenhr:synergenhr /opt/synergenhr

# Switch to application user
sudo -u synergenhr bash << 'EOF'
cd /opt/synergenhr

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create production settings
cp .env .env.production
# Edit .env.production with your production settings

# Run migrations
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createhorillauser --first_name admin --last_name admin --username admin --password admin --email admin@example.com --phone 1234567890
EOF

echo "✅ Manual installation completed!"
echo "📋 Next steps:"
echo "1. Configure PostgreSQL database"
echo "2. Set up Nginx reverse proxy"
echo "3. Create systemd service for the application"
echo "4. Configure SSL certificates"