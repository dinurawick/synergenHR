#!/bin/bash

# SynergenHR Deployment Script for EUK Cloud Linux

set -e

echo "🚀 Starting SynergenHR deployment..."

# Set variables
DB_PASSWORD=$(openssl rand -base64 32)
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')

# Create .env.production with generated secrets
cat > .env.production << EOF
DEBUG=False
SECRET_KEY=${SECRET_KEY}
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,$(curl -s ifconfig.me)
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com
TIME_ZONE=UTC
DB_PASSWORD=${DB_PASSWORD}
EOF

echo "✅ Environment configuration created"

# Build and start services
echo "🔨 Building Docker images..."
docker-compose -f docker-compose.prod.yml build

echo "🚀 Starting services..."
docker-compose -f docker-compose.prod.yml up -d

echo "⏳ Waiting for services to be ready..."
sleep 30

# Check if services are running
if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    echo "✅ Services are running successfully!"
    echo ""
    
    # Ask about demo data
    echo "🎭 Demo Data Options:"
    echo "   SynergenHR includes comprehensive demo data with:"
    echo "   • Sample employees and departments"
    echo "   • Demo attendance and leave records"
    echo "   • Example payroll and recruitment data"
    echo "   • Asset management samples"
    echo "   • Performance management examples"
    echo ""
    read -p "Would you like to load demo data? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📊 Loading demo data..."
        chmod +x deployment/load_demo_data.sh
        ./deployment/load_demo_data.sh
    else
        echo "⏭️ Skipping demo data loading."
        echo "   You can load it later by running: ./deployment/load_demo_data.sh"
    fi
    
    echo ""
    echo "🎉 SynergenHR has been deployed successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Update your domain DNS to point to this server"
    echo "2. Install SSL certificates in ./ssl/ directory"
    echo "3. Update nginx.conf with your actual domain name"
    echo "4. Access your application at: http://$(curl -s ifconfig.me):8000"
    echo ""
    echo "🔐 Default admin credentials:"
    echo "   Username: admin"
    echo "   Password: admin"
    echo "   ⚠️  CHANGE THESE IMMEDIATELY AFTER FIRST LOGIN!"
    echo ""
    echo "📚 Additional commands:"
    echo "   Load demo data: ./deployment/load_demo_data.sh"
    echo "   Create backup: ./deployment/db_backup.sh"
    echo "   View logs: docker-compose -f docker-compose.prod.yml logs"
    echo "   Restart: docker-compose -f docker-compose.prod.yml restart"
else
    echo "❌ Deployment failed. Check logs with: docker-compose -f docker-compose.prod.yml logs"
    exit 1
fi