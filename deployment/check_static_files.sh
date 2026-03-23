#!/bin/bash
# Script to check if static files are properly updated

echo "=========================================="
echo "  Checking Static Files"
echo "=========================================="

# Check if the dashboard.js file exists in staticfiles
echo ""
echo "1. Checking if dashboard.js exists in staticfiles..."
if [ -f "staticfiles/payroll/dashboard.js" ]; then
    echo "✓ File exists: staticfiles/payroll/dashboard.js"
    
    # Check if the file contains the correct URL pattern
    echo ""
    echo "2. Checking for correct URL pattern in dashboard.js..."
    if grep -q "employee-view/" staticfiles/payroll/dashboard.js; then
        echo "✓ Correct URL pattern found: /employee/employee-view/"
    else
        echo "✗ Correct URL pattern NOT found!"
        echo "  Looking for old pattern..."
        if grep -q "employee-view-individual/" staticfiles/payroll/dashboard.js; then
            echo "✗ Old URL pattern still present: /employee/employee-view-individual/"
            echo "  You need to run: python manage.py collectstatic --noinput --clear"
        fi
    fi
    
    # Show last modification time
    echo ""
    echo "3. File last modified:"
    ls -lh staticfiles/payroll/dashboard.js | awk '{print "   " $6, $7, $8, $9}'
else
    echo "✗ File NOT found: staticfiles/payroll/dashboard.js"
    echo "  You need to run: python manage.py collectstatic --noinput"
fi

# Check source file
echo ""
echo "4. Checking source file..."
if [ -f "payroll/static/payroll/dashboard.js" ]; then
    echo "✓ Source file exists: payroll/static/payroll/dashboard.js"
    if grep -q "employee-view/" payroll/static/payroll/dashboard.js; then
        echo "✓ Source file has correct URL pattern"
    else
        echo "✗ Source file has incorrect URL pattern"
    fi
else
    echo "✗ Source file NOT found"
fi

echo ""
echo "=========================================="
echo "  Check Complete"
echo "=========================================="
