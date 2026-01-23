#!/bin/bash

# Database Migration Script for SynergenHR

set -e

echo "🔄 Running database migrations..."

# Check if we're using Docker or manual installation
if [ -f "docker-compose.prod.yml" ] && docker-compose -f docker-compose.prod.yml ps | grep -q "db.*Up"; then
    echo "📦 Using Docker deployment..."
    
    # Run migrations in Docker container
    docker-compose -f docker-compose.prod.yml exec server python manage.py makemigrations
    docker-compose -f docker-compose.prod.yml exec server python manage.py migrate
    
    # Collect static files
    docker-compose -f docker-compose.prod.yml exec server python manage.py collectstatic --noinput
    
    # Create superuser
    docker-compose -f docker-compose.prod.yml exec server python manage.py createhorillauser \
        --first_name admin \
        --last_name admin \
        --username admin \
        --password admin \
        --email admin@example.com \
        --phone 1234567890
    
    echo "✅ Docker migrations completed!"
    
elif [ -f "venv/bin/activate" ]; then
    echo "🐍 Using manual Python installation..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Run migrations
    python manage.py makemigrations
    python manage.py migrate
    
    # Collect static files
    python manage.py collectstatic --noinput
    
    # Create superuser
    python manage.py createhorillauser \
        --first_name admin \
        --last_name admin \
        --username admin \
        --password admin \
        --email admin@example.com \
        --phone 1234567890
    
    echo "✅ Manual installation migrations completed!"
    
else
    echo "❌ Could not detect installation method!"
    echo "Please run migrations manually:"
    echo "  python manage.py makemigrations"
    echo "  python manage.py migrate"
    echo "  python manage.py collectstatic --noinput"
    exit 1
fi

echo ""
echo "🎉 Database setup completed!"
echo ""
echo "🔐 Default admin credentials:"
echo "   Username: admin"
echo "   Password: admin"
echo "   Email: admin@example.com"
echo ""
echo "⚠️  IMPORTANT: Change the admin password immediately after first login!"
echo ""
echo "📋 Available Django management commands:"
echo "   Create superuser: python manage.py createsuperuser"
echo "   Load sample data: python manage.py loaddata load_data/*.json"
echo "   Check deployment: python manage.py check --deploy"