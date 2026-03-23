#!/bin/bash
# Script to update static files on the hosted Linux server
# Run this script on your Linux server after pulling changes from Git

set -e  # Exit on error

echo "=========================================="
echo "  Updating Static Files on Server"
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "docker-compose.yaml" ]; then
    echo "Error: docker-compose.yaml not found. Please run this script from the project root directory."
    exit 1
fi

# Step 1: Pull latest changes (if needed)
echo ""
echo "Step 1: Checking Git status..."
git status

# Step 2: Rebuild and restart Docker containers
echo ""
echo "Step 2: Rebuilding and restarting Docker containers..."
docker-compose down
docker-compose up -d --build

# Step 3: Wait for containers to start
echo ""
echo "Step 3: Waiting for containers to start..."
sleep 15

# Step 4: Collect static files inside the container
echo ""
echo "Step 4: Collecting static files inside Docker container..."
docker-compose exec -T server python manage.py collectstatic --noinput --clear

# Step 5: Check container status
echo ""
echo "Step 5: Checking container status..."
docker-compose ps

echo ""
echo "=========================================="
echo "  Update Complete!"
echo "=========================================="
echo ""
echo "IMPORTANT: Clear your browser cache and hard refresh (Ctrl+Shift+R or Cmd+Shift+R)"
echo ""
echo "If the issue persists, check:"
echo "1. Browser console for JavaScript errors (F12)"
echo "2. Docker logs: docker-compose logs -f server"
echo "3. Static files are being served correctly"
echo ""
