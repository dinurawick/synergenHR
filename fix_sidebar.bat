@echo off
cls
echo ========================================
echo   FIX SYNERGENHR SIDEBAR
echo ========================================
echo.
echo This will:
echo - Copy SynergenHR logo to sidebar
echo - Update company names in database
echo - Deploy changes
echo.

echo [1/4] Activating virtual environment...
call horillavenv\Scripts\activate
if errorlevel 1 (
    echo ❌ ERROR: Virtual environment not found
    pause
    exit /b 1
)

echo.
echo [2/4] Setting up sidebar logo and name...
python setup_sidebar.py
if errorlevel 1 (
    echo ❌ ERROR: Sidebar setup failed
    pause
    exit /b 1
)

echo.
echo [3/4] Collecting static files...
python manage.py collectstatic --noinput
if errorlevel 1 (
    echo ❌ ERROR: Failed to collect static files
    pause
    exit /b 1
)

echo.
echo [4/4] Starting Django server...
echo.
echo ========================================
echo   ✅ SIDEBAR FIXED!
echo.
echo   What you should see:
echo   - Sidebar: "SynergenHR" (no dots)
echo   - Logo: SynergenHR logo in sidebar
echo   - Colors: Blue and yellow theme
echo.
echo   🔄 CLEAR YOUR BROWSER CACHE!
echo   Press Ctrl+Shift+Delete
echo.
echo   URL: http://localhost:8000
echo ========================================
echo.

python manage.py runserver