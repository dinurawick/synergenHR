#!/bin/bash

# Load Demo Data Script for Manual SynergenHR Installation

set -e

echo "🎭 Loading SynergenHR Demo Data (Manual Installation)..."

# Check if virtual environment exists
if [ ! -f "venv/bin/activate" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please ensure you have set up the virtual environment first."
    exit 1
fi

# Activate virtual environment
echo "🐍 Activating virtual environment..."
source venv/bin/activate

# Check if Django is available
if ! python -c "import django" 2>/dev/null; then
    echo "❌ Django not found in virtual environment!"
    echo "Please install requirements: pip install -r requirements.txt"
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
python manage.py loaddata load_data/base_data.json

echo "👥 Loading user data..."
python manage.py loaddata load_data/user_data.json

echo "💼 Loading employee information..."
python manage.py loaddata load_data/employee_info_data.json

echo "🏢 Loading work information..."
python manage.py loaddata load_data/work_info_data.json

echo "🏷️ Loading tags..."
python manage.py loaddata load_data/tags.json

echo "📧 Loading mail templates..."
python manage.py loaddata load_data/mail_templates.json

echo "🤖 Loading mail automations..."
python manage.py loaddata load_data/mail_automations.json

echo "🏖️ Loading leave data..."
python manage.py loaddata load_data/leave_data.json

echo "⏰ Loading attendance data..."
python manage.py loaddata load_data/attendance_data.json

echo "💰 Loading payroll data..."
python manage.py loaddata load_data/payroll_data.json

echo "🏦 Loading loan account data..."
python manage.py loaddata load_data/payroll_loanaccount_data.json

echo "📋 Loading recruitment data..."
python manage.py loaddata load_data/recruitment_data.json

echo "🎯 Loading PMS data..."
python manage.py loaddata load_data/pms_data.json

echo "📦 Loading asset data..."
python manage.py loaddata load_data/asset_data.json

echo "🚀 Loading onboarding data..."
python manage.py loaddata load_data/onboarding_data.json

echo "👋 Loading offboarding data..."
python manage.py loaddata load_data/offboarding_data.json

echo "📊 Loading project data..."
python manage.py loaddata load_data/project_data.json

echo "❓ Loading FAQ categories..."
python manage.py loaddata load_data/faq_category.json

echo "❓ Loading FAQ data..."
python manage.py loaddata load_data/faq.json

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
echo "🌐 Access your system at: http://localhost:8000"