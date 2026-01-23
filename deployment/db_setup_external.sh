#!/bin/bash

# External Database Configuration Script

echo "🌐 Configuring external database connection..."

# Prompt for database details
read -p "Enter database host: " DB_HOST
read -p "Enter database port (default 5432): " DB_PORT
DB_PORT=${DB_PORT:-5432}
read -p "Enter database name: " DB_NAME
read -p "Enter database username: " DB_USER
read -s -p "Enter database password: " DB_PASSWORD
echo

# Test connection (requires psql client)
if command -v psql &> /dev/null; then
    echo "🔍 Testing database connection..."
    if PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "SELECT version();" > /dev/null 2>&1; then
        echo "✅ Database connection successful!"
    else
        echo "❌ Database connection failed! Please check your credentials."
        exit 1
    fi
else
    echo "⚠️ psql not found. Skipping connection test."
    echo "Install with: sudo apt install postgresql-client"
fi

# Create environment configuration
cat > .env.production << EOF
DEBUG=False
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,$(curl -s ifconfig.me)
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com
TIME_ZONE=UTC

# External Database Configuration
DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}

# Alternative format
DB_ENGINE=django.db.backends.postgresql
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}
DB_HOST=${DB_HOST}
DB_PORT=${DB_PORT}
EOF

echo "✅ External database configuration created!"
echo ""
echo "📋 Database Details:"
echo "   Host: ${DB_HOST}"
echo "   Port: ${DB_PORT}"
echo "   Database: ${DB_NAME}"
echo "   Username: ${DB_USER}"