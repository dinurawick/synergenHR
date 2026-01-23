#!/bin/bash

# Database Setup Script for Docker Deployment

set -e

echo "🗄️ Setting up PostgreSQL database with Docker..."

# Generate secure database password
DB_PASSWORD=$(openssl rand -base64 32)

# Create environment file with database configuration
cat > .env.production << EOF
DEBUG=False
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,$(curl -s ifconfig.me)
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com
TIME_ZONE=UTC

# Database Configuration
DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@db:5432/synergenhr
DB_PASSWORD=${DB_PASSWORD}
EOF

echo "✅ Database configuration created"
echo "🔐 Database password: ${DB_PASSWORD}"
echo "📝 Save this password securely!"

# Start only the database first
echo "🚀 Starting PostgreSQL container..."
docker-compose -f docker-compose.prod.yml up -d db

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 15

# Check database connection
if docker-compose -f docker-compose.prod.yml exec db pg_isready -U postgres; then
    echo "✅ Database is ready!"
else
    echo "❌ Database failed to start. Check logs:"
    docker-compose -f docker-compose.prod.yml logs db
    exit 1
fi

echo "🎉 Database setup completed!"
echo ""
echo "📋 Database Details:"
echo "   Host: localhost (from host machine)"
echo "   Port: 5432"
echo "   Database: synergenhr"
echo "   Username: postgres"
echo "   Password: ${DB_PASSWORD}"