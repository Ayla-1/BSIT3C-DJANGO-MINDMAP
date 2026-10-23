# Fix: Table 'mindmap_db.auth_user' doesn't exist

## Problem
You're seeing this error because Django's authentication system tables haven't been created in your database yet, even though the migrations show as applied.

## Solution

Follow these steps **in order**:

---

### **Step 1: Verify MySQL is Running**

1. Open XAMPP Control Panel
2. Make sure MySQL shows a **green indicator** (running)
3. If not, click **Start** next to MySQL

---

### **Step 2: Check Database Exists**

1. Open phpMyAdmin: `http://localhost/phpmyadmin`
2. Look for database named `mindmap_db` in the left sidebar
3. Click on it to select it
4. Verify you see these tables:
   - students
   - teachers
   - subjects
   - grades
   - academic_progress
   - learning_assessments

If the database doesn't exist, import `SQL/mindmap_db.sql`

---

### **Step 3: Open Command Prompt/PowerShell**

1. Press `Windows + R`
2. Type `cmd` and press Enter
3. Navigate to project:
   ```
   cd c:\xampp2\htdocs\BSIT3C-DJANGO-MINDMAP
   ```

---

### **Step 4: Run Migrations Again**

Even if migrations show as applied, run this command:

```bash
python manage.py migrate --run-syncdb
```

This will create any missing tables, including Django's auth tables.

**You should see output like:**
```
Operations to perform:
  Synchronize unmigrated apps: ...
  Apply all migrations: admin, auth, contenttypes, core, sessions
Running migrations:
  Creating table auth_permission
  Creating table auth_group
  Creating table auth_user
  ...
```

---

### **Step 5: Create Admin User**

Now create the admin account:

```bash
python manage.py createsuperuser
```

**When prompted, enter:**
- Username: `admin`
- Email: `admin@mindmap.com` (or leave blank)
- Password: `admin123`
- Password (again): `admin123`

**Note:** You may see a warning that the password is too common. Type `y` to use it anyway (for development).

---

### **Step 6: Run Setup Script**

Now link existing database records to user accounts:

```bash
python setup_database.py
```

**OR** double-click the file: `run_setup.bat`

This will:
- Create user accounts for existing teachers
- Create user accounts for existing students
- Link them to the database records

---

### **Step 7: Start Server**

```bash
python manage.py runserver
```

**OR** double-click: `start_server.bat`

---

### **Step 8: Test Login**

1. Visit: `http://127.0.0.1:8000/`
2. Login with:
   - Username: `admin`
   - Password: `admin123`

---

## Alternative Fix: Fresh Database Setup

If the above doesn't work, try this fresh setup:

### **1. Drop and Recreate Database**

In phpMyAdmin:
1. Select `mindmap_db` database
2. Click "Operations" tab
3. Scroll down to "Remove database"
4. Click "Drop the database"
5. Create new database: `mindmap_db`
6. Import `SQL/mindmap_db.sql`

### **2. Run All Commands Fresh**

```bash
# Navigate to project
cd c:\xampp2\htdocs\BSIT3C-DJANGO-MINDMAP

# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser
# Username: admin
# Password: admin123

# Setup database users
python setup_database.py

# Start server
python manage.py runserver
```

---

## Why This Happens

Django creates its own tables (auth_user, auth_group, etc.) when you run migrations. These are separate from your custom tables (students, teachers, etc.). 

The migration files show as applied (`[X]`) but the actual tables might not exist if:
- Migrations were run against a different database
- Database was dropped and recreated
- Django's migration table was imported but actual tables weren't

Running `migrate --run-syncdb` forces Django to create all tables.

---

## Verify Tables Exist

In phpMyAdmin, select `mindmap_db` and check for these Django tables:

**Django System Tables:**
- auth_user
- auth_group
- auth_permission
- auth_group_permissions
- auth_user_groups
- auth_user_user_permissions
- django_admin_log
- django_content_type
- django_migrations
- django_session
- core_userprofile

**Your Custom Tables:**
- students
- teachers
- subjects
- grades
- learning_assessments
- academic_progress

---

## Test Database Connection

Run this to verify connection:

```bash
python test_connection.py
```

You should see:
```
✓ Database connection successful!
Database: mindmap_db
Host: localhost
Port: 3306
```

---

## Still Having Issues?

### Check 1: Python and Django versions
```bash
python --version
python -m django --version
```

Should show:
- Python 3.13.x
- Django 4.2.x or 5.0.x

### Check 2: Database credentials

Open `mysite/settings.py` and verify:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mindmap_db',
        'USER': 'root',
        'PASSWORD': '',  # Change if you set a password
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### Check 3: MySQL port

Make sure MySQL is running on port 3306 (default).

---

## Quick Command Reference

```bash
# Check if tables exist (via Django)
python manage.py dbshell
> SHOW TABLES;
> exit

# Force create tables
python manage.py migrate --run-syncdb

# Create admin user
python manage.py createsuperuser

# Setup database users
python setup_database.py

# Test connection
python test_connection.py

# Start server
python manage.py runserver
```

---

## Success Checklist

- [ ] MySQL is running in XAMPP
- [ ] Database `mindmap_db` exists
- [ ] Django tables exist (auth_user, etc.)
- [ ] Custom tables exist (students, teachers, etc.)
- [ ] Admin user created
- [ ] Can login at http://127.0.0.1:8000/
- [ ] See admin dashboard

---

## Need More Help?

1. Check the terminal output for specific error messages
2. Review SETUP_GUIDE.md for detailed setup
3. Check XAMPP logs: `xampp/mysql/data/mysql_error.log`

---

**This should fix your issue!** The key is running `migrate --run-syncdb` to ensure all Django tables are created.
