#!/bin/bash

# Load Demo Data Script for SynergenHR

set -e

echo "🎭 Loading SynergenHR Demo Data..."

# Check if we're using Docker or manual installation
if [ -f "docker-compose.prod.yml" ] && docker-compose -f docker-compose.prod.yml ps | grep -q "server.*Up"; then
    echo "📦 Using Docker deployment..."
    DOCKER_MODE=true
    MANAGE_CMD="docker-compose -f docker-compose.prod.yml exec server python manage.py"
elif [ -f "venv/bin/activate" ]; then
    echo "🐍 Using manual Python installation..."
    DOCKER_MODE=false
    source venv/bin/activate
    MANAGE_CMD="python manage.py"
else
    echo "❌ Could not detect installation method!"
    echo "Please ensure either Docker is running or virtual environment exists."
    exit 1
fi

echo "📋 Demo data files found:"
ls -la load_data/

echo ""
echo "⚠️  WARNING: This will add demo data to your database."
echo "   - Demo employees, departments, and sample records will be created"
echo "   - This is recommended for testing and demonstrations"
echo "   - Do NOT run this on production systems with real data"
echo ""

# Prompt for confirmation
read -p "Do you want to proceed with loading demo data? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Demo data loading cancelled."
    exit 0
fi

echo ""
echo "🚀 Starting demo data loading process..."

# Load data in the correct order (dependencies matter)
echo "📊 Loading base data (companies, departments, job positions)..."
$MANAGE_CMD loaddata load_data/base_data.json

echo "👥 Loading user data..."
$MANAGE_CMD loaddata load_data/user_data.json

echo "💼 Loading employee information..."
$MANAGE_CMD loaddata load_data/employee_info_data.json

echo "🏢 Loading work information..."
$MANAGE_CMD loaddata load_data/work_info_data.json

echo "🏷️ Loading tags..."
$MANAGE_CMD loaddata load_data/tags.json

echo "📧 Loading mail templates..."
$MANAGE_CMD loaddata load_data/mail_templates.json

echo "🤖 Loading mail automations..."
$MANAGE_CMD loaddata load_data/mail_automations.json

echo "🏖️ Loading leave data..."
$MANAGE_CMD loaddata load_data/leave_data.json

echo "⏰ Loading attendance data..."
$MANAGE_CMD loaddata load_data/attendance_data.json

echo "💰 Loading payroll data..."
$MANAGE_CMD loaddata load_data/payroll_data.json

echo "🏦 Loading loan account data..."
$MANAGE_CMD loaddata load_data/payroll_loanaccount_data.json

echo "📋 Loading recruitment data..."
$MANAGE_CMD loaddata load_data/recruitment_data.json

echo "🎯 Loading PMS data..."
$MANAGE_CMD loaddata load_data/pms_data.json

echo "📦 Loading asset data..."
$MANAGE_CMD loaddata load_data/asset_data.json

echo "🚀 Loading onboarding data..."
$MANAGE_CMD loaddata load_data/onboarding_data.json

echo "👋 Loading offboarding data..."
$MANAGE_CMD loaddata load_data/offboarding_data.json

echo "📊 Loading project data..."
$MANAGE_CMD loaddata load_data/project_data.json

echo "❓ Loading FAQ categories..."
$MANAGE_CMD loaddata load_data/faq_category.json

echo "❓ Loading FAQ data..."
$MANAGE_CMD loaddata load_data/faq.json

echo ""
echo "✅ Demo data loading completed successfully!"
echo ""
echo "🎉 Your SynergenHR system now includes:"
echo "   • Sample employees and departments"
echo "   • Demo attendance records"
echo "   • Sample leave requests and types"
echo "   • Example payroll data"
echo "   • Recruitment pipeline examples"
echo "   • Asset management samples"
echo "   • Performance management data"
echo "   • FAQ and help content"
echo ""
echo "🔐 Demo Login Credentials:"
echo "   Username: admin"
echo "   Password: admin"
echo ""
echo "⚠️  Remember to change the admin password after login!"
echo ""
echo "🌐 Access your system at:"
if [ "$DOCKER_MODE" = true ]; then
    echo "   http://$(curl -s ifconfig.me):8000"
else
    echo "   http://localhost:8000"
fi