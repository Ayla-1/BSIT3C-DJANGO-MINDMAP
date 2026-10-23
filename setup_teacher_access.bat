@echo off
cls
echo ============================================================
echo          Setup Teacher Access
echo ============================================================
echo.
echo This will:
echo 1. Check your current database
echo 2. Add sample teachers, students, and subjects
echo 3. Create user accounts for them
echo.
echo ============================================================
pause
echo.

echo.
echo Step 1: Checking current database...
echo ============================================================
python check_data.py
echo.

echo.
echo ============================================================
echo Step 2: Adding sample data...
echo ============================================================
python add_sample_data.py
echo.

echo.
echo ============================================================
echo ✓ Setup Complete!
echo ============================================================
echo.
echo You can now test teacher access:
echo.
echo 1. Start server: python manage.py runserver
echo 2. Visit: http://127.0.0.1:8000/
echo 3. Login as teacher:
echo      Username: john.doe
echo      Password: teacher123
echo.
echo Or try student:
echo      Username: 2024-0001
echo      Password: student123
echo.
echo ============================================================
pause
