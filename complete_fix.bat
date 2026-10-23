@echo off
cls
echo ============================================================
echo          MindMap Database Complete Fix
echo ============================================================
echo.
echo This script will:
echo 1. Create all Django tables (including auth_user)
echo 2. Create admin superuser
echo 3. Setup teacher and student user accounts
echo.
echo ============================================================
pause
echo.

echo.
echo ============================================================
echo STEP 1: Creating Django Tables
echo ============================================================
echo.
python create_tables.py
if errorlevel 1 (
    echo.
    echo ERROR: Failed to create tables
    echo Make sure MySQL is running in XAMPP
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo STEP 2: Creating Admin User
echo ============================================================
echo.
echo Please enter the following when prompted:
echo   Username: admin
echo   Email: (press Enter to skip)
echo   Password: admin123
echo   Password (again): admin123
echo.
echo If you see "password is too common" warning, type: y
echo.
pause

python manage.py createsuperuser
if errorlevel 1 (
    echo.
    echo Note: If admin user already exists, that's okay!
    echo.
)

echo.
echo ============================================================
echo STEP 3: Setting Up Teacher and Student Accounts
echo ============================================================
echo.
python setup_database.py

echo.
echo ============================================================
echo ✓✓✓ SETUP COMPLETE! ✓✓✓
echo ============================================================
echo.
echo Your MindMap system is now ready to use!
echo.
echo To start the server:
echo   1. Run: python manage.py runserver
echo   2. Or double-click: start_server.bat
echo.
echo Then visit: http://127.0.0.1:8000/
echo.
echo Login credentials:
echo   Username: admin
echo   Password: admin123
echo.
echo ============================================================
pause
