@echo off
REM Setup SynergenHR on New Laptop - Automated Script
REM Run this script from the project root directory

echo ========================================
echo   SynergenHR Setup - New Laptop
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "manage.py" (
    echo ERROR: manage.py not found!
    echo Please run this script from the project root directory.
    pause
    exit /b 1
)

echo Step 1: Removing old virtual environment (if exists)...
if exist "horillavenv" (
    echo Found existing virtual environment, removing...
    rmdir /s /q horillavenv
    echo Old virtual environment removed.
) else (
    echo No existing virtual environment found.
)
echo.

echo Step 2: Creating new virtual environment...
python -m venv horillavenv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment!
    echo Make sure Python is installed and in PATH.
    pause
    exit /b 1
)
echo Virtual environment created successfully.
echo.

echo Step 3: Activating virtual environment...
call horillavenv\Scripts\activate.bat
echo.

echo Step 4: Upgrading pip...
python -m pip install --upgrade pip
echo.

echo Step 5: Installing dependencies...
echo This may take a few minutes...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)
echo Dependencies installed successfully.
echo.

echo Step 6: Checking .env file...
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Please create .env file with database configuration.
    echo Example:
    echo   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/synergenhr
    echo   DEBUG=True
    echo   SECRET_KEY=your-secret-key-here
    echo.
    pause
)
echo.

echo Step 7: Running database migrations...
python manage.py migrate
if errorlevel 1 (
    echo ERROR: Database migration failed!
    echo Please check your database configuration in .env file.
    pause
    exit /b 1
)
echo Migrations completed successfully.
echo.

echo Step 8: Collecting static files...
python manage.py collectstatic --noinput
echo Static files collected.
echo.

echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Create superuser: python manage.py createsuperuser
echo 2. Start server: python manage.py runserver
echo 3. Visit: http://127.0.0.1:8000
echo.
echo To activate virtual environment in future:
echo   horillavenv\Scripts\activate
echo.
pause
