@echo off
echo ========================================
echo MindMap Database Fix Script
echo ========================================
echo.
echo This will fix the "auth_user doesn't exist" error
echo.
echo Step 1: Running migrations with --run-syncdb...
python manage.py migrate --run-syncdb
echo.
echo ========================================
echo Step 2: Creating admin superuser...
echo ========================================
echo.
echo When prompted, enter:
echo   Username: admin
echo   Email: (press Enter to skip)
echo   Password: admin123
echo   Password (again): admin123
echo.
echo If warned about common password, type: y
echo.
python manage.py createsuperuser
echo.
echo ========================================
echo Step 3: Setting up user accounts...
echo ========================================
echo.
python setup_database.py
echo.
echo ========================================
echo ✓ FIX COMPLETE!
echo ========================================
echo.
echo You can now start the server with:
echo   python manage.py runserver
echo.
echo Or double-click: start_server.bat
echo.
echo Then login at: http://127.0.0.1:8000/
echo   Username: admin
echo   Password: admin123
echo.
pause
