@echo off
cls
echo ========================================
echo   SynergenHR Complete Setup
echo ========================================
echo.

echo [1/5] Activating virtual environment...
call horillavenv\Scripts\activate
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo.
echo [2/5] Updating database company names...
python update_company_name.py
if errorlevel 1 (
    echo WARNING: Database update had issues, continuing...
)

echo.
echo [3/5] Clearing old static files...
if exist staticfiles rmdir /s /q staticfiles
mkdir staticfiles

echo.
echo [4/5] Collecting static files (including logo)...
python manage.py collectstatic --noinput
if errorlevel 1 (
    echo ERROR: Failed to collect static files
    pause
    exit /b 1
)

echo.
echo [5/5] Starting Django server...
echo.
echo ========================================
echo   SynergenHR is now running!
echo   
echo   URL: http://localhost:8000
echo   
echo   CHANGES MADE:
echo   ✅ Company name: SynergenHR (in sidebar)
echo   ✅ Logo: Your synergen_logo.jpg
echo   ✅ Colors: Blue (#0a0a5a) ^& Yellow (#dbf30d)
echo   
echo   IMPORTANT: Clear your browser cache!
echo   Press Ctrl+Shift+Delete or Ctrl+F5
echo   
echo   Press Ctrl+C to stop the server
echo ========================================
echo.
python manage.py runserver
