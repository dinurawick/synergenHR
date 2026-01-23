#!/bin/bash

# Manual PostgreSQL Setup Script for EUK Cloud Linux

set -e

echo "🗄️ Installing and configuring PostgreSQL..."

# Update system
sudo apt update

# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Start and enable PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Generate secure passwords
DB_PASSWORD=$(openssl rand -base64 32)
POSTGRES_PASSWORD=$(openssl rand -base64 32)

echo "🔐 Generated passwords:"
echo "   PostgreSQL superuser password: ${POSTGRES_PASSWORD}"
echo "   SynergenHR database password: ${DB_PASSWORD}"
echo "📝 Save these passwords securely!"

# Configure PostgreSQL
sudo -u postgres psql << EOF
-- Set password for postgres user
ALTER USER postgres PASSWORD '${POSTGRES_PASSWORD}';

-- Create database and user for SynergenHR
CREATE DATABASE synergenhr;
CREATE USER synergenhr WITH PASSWORD '${DB_PASSWORD}';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE synergenhr TO synergenhr;
ALTER USER synergenhr CREATEDB;

-- Exit
\q
EOF

# Configure PostgreSQL for network connections
sudo cp /etc/postgresql/*/main/postgresql.conf /etc/postgresql/*/main/postgresql.conf.backup
sudo cp /etc/postgresql/*/main/pg_hba.conf /etc/postgresql/*/main/pg_hba.conf.backup

# Update postgresql.conf
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = 'localhost'/" /etc/postgresql/*/main/postgresql.conf

# Update pg_hba.conf for local connections
sudo bash -c 'cat >> /etc/postgresql/*/main/pg_hba.conf << EOF

# SynergenHR application
local   synergenhr      synergenhr                              md5
host    synergenhr      synergenhr      127.0.0.1/32            md5
host    synergenhr      synergenhr      ::1/128                 md5
EOF'

# Restart PostgreSQL
sudo systemctl restart postgresql

# Test connection
if sudo -u postgres psql -d synergenhr -c "SELECT version();" > /dev/null 2>&1; then
    echo "✅ Database connection test successful!"
else
    echo "❌ Database connection test failed!"
    exit 1
fi

# Create .env file for the application
cat > .env.production << EOF
DEBUG=False
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,$(curl -s ifconfig.me)
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com
TIME_ZONE=UTC

# Database Configuration
DATABASE_URL=postgresql://synergenhr:${DB_PASSWORD}@localhost:5432/synergenhr

# Alternative format
DB_ENGINE=django.db.backends.postgresql
DB_NAME=synergenhr
DB_USER=synergenhr
DB_PASSWORD=${DB_PASSWORD}
DB_HOST=localhost
DB_PORT=5432
EOF

echo "✅ PostgreSQL setup completed!"
echo ""
echo "📋 Database Details:"
echo "   Host: localhost"
echo "   Port: 5432"
echo "   Database: synergenhr"
echo "   Username: synergenhr"
echo "   Password: ${DB_PASSWORD}"
echo ""
echo "🔧 PostgreSQL Service Commands:"
echo "   Start: sudo systemctl start postgresql"
echo "   Stop: sudo systemctl stop postgresql"
echo "   Restart: sudo systemctl restart postgresql"
echo "   Status: sudo systemctl status postgresql"