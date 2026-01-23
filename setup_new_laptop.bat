@echo off
echo ========================================
echo SynergenHR New Laptop Setup
echo ========================================

echo.
echo This script will set up SynergenHR on your new laptop
echo using the synergenhr.db file you copied.
echo.

REM Check if database file exists
if not exist "synergenhr.db" (
    echo ERROR: synergenhr.db file not found!
    echo.
    echo Please make sure you have:
    echo 1. Copied synergenhr.db to this folder
    echo 2. Copied the entire SynergenHR project
    echo.
    pause
    exit /b 1
)

echo Step 1: Creating SQLite configuration...

REM Create .env file for SQLite
echo DEBUG=True > .env
echo SECRET_KEY=django-insecure-j8op9)1q8$1^0^s^p*_0%%d#pr@w9qj@1o=3#@d=a(^@9@zd@%%j >> .env
echo ALLOWED_HOSTS=localhost,127.0.0.1,* >> .env
echo TIME_ZONE=Asia/Kolkata >> .env
echo DATABASE_URL=sqlite:///./synergenhr.db >> .env

echo SQLite configuration created.

echo.
echo Step 2: Setting up Python environment...

REM Check if virtual environment exists
if exist "horillavenv\Scripts\activate.bat" (
    echo Virtual environment found. Activating...
    call horillavenv\Scripts\activate.bat
) else (
    echo Creating new virtual environment...
    python -m venv horillavenv
    call horillavenv\Scripts\activate.bat
    echo Installing requirements...
    pip install -r requirements.txt
)

echo.
echo Step 3: Collecting static files...
python manage.py collectstatic --noinput

echo.
echo Step 4: Testing database connection...
python manage.py check

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Your SynergenHR system is ready to use with your existing data.
echo.
echo To start the server:
echo python manage.py runserver
echo.
echo Then open: http://localhost:8000
echo.
echo Your existing login credentials should work.
echo.
pause