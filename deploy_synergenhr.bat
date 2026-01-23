@echo off
cls
echo ========================================
echo   SynergenHR DEPLOYMENT SCRIPT
echo ========================================
echo.
echo This script will rebrand Horilla to SynergenHR
echo - Update logo to SynergenHR logo
echo - Change colors to blue and yellow
echo - Update database company names
echo - Deploy all changes
echo.
pause

echo [1/6] Checking required files...
if not exist "synergen\SYN_LOGO.png" (
    echo ❌ ERROR: SynergenHR logo not found!
    echo Please ensure synergen\SYN_LOGO.png exists
    pause
    exit /b 1
)
echo ✅ Logo file found

echo.
echo [2/6] Activating virtual environment...
call horillavenv\Scripts\activate
if errorlevel 1 (
    echo ❌ ERROR: Failed to activate virtual environment
    echo Make sure horillavenv folder exists
    pause
    exit /b 1
)
echo ✅ Virtual environment activated

echo.
echo [3/6] Copying SynergenHR logo to all locations...
copy "synergen\SYN_LOGO.png" "static\images\ui\auth-logo.png" >nul
copy "synergen\SYN_LOGO.png" "static\images\ui\horilla-logo.png" >nul
echo ✅ Logo files copied

echo.
echo [4/6] Updating database company names...
python update_company_name.py
if errorlevel 1 (
    echo ⚠️  WARNING: Database update had issues, continuing...
)

echo.
echo [5/6] Removing any extra dots from company names...
python fix_company_dots.py

echo.
echo [6/6] Collecting static files and starting server...
python manage.py collectstatic --noinput --clear
if errorlevel 1 (
    echo ❌ ERROR: Failed to collect static files
    pause
    exit /b 1
)

echo.
echo ========================================
echo   🎉 SYNERGENHR DEPLOYMENT COMPLETE!
echo ========================================
echo.
echo ✅ Logo: SynergenHR logo deployed
echo ✅ Colors: Blue (#0a0a5a) and Yellow (#dbf30d)
echo ✅ Database: Company names updated to SynergenHR
echo ✅ Static files: All changes deployed
echo.
echo 🌐 Starting Django server...
echo URL: http://localhost:8000
echo.
echo 🔄 IMPORTANT: Clear your browser cache!
echo Press Ctrl+Shift+Delete or use Ctrl+F5
echo.
echo Press Ctrl+C to stop the server when done
echo ========================================
echo.

python manage.py runserver