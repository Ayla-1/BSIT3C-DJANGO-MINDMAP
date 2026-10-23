# MindMap: Student Academic Progress Monitoring System
## Complete Setup Guide for Windows

This guide will walk you through setting up the MindMap system from scratch.

---

## 📋 Prerequisites

Before starting, ensure you have:
- **Windows OS**
- **Python 3.13.15** (already installed)
- **MySQL/MariaDB** (XAMPP installed)
- **pip** (Python package manager)

---

## 🚀 Step-by-Step Setup Instructions

### **STEP 1: Start MySQL Server**

1. Open **XAMPP Control Panel**
2. Click **Start** next to **MySQL**
3. Verify MySQL is running (green indicator)

---

### **STEP 2: Create/Import Database**

1. Open **phpMyAdmin** in your browser: `http://localhost/phpmyadmin`
2. Click **New** to create a database named `mindmap_db`
3. Select the `mindmap_db` database
4. Click **Import** tab
5. Choose file: `SQL/mindmap_db.sql`
6. Click **Go** to import the database structure

**Verify**: You should see 6 tables:
- students
- teachers  
- subjects
- grades
- academic_progress
- learning_assessments

---

### **STEP 3: Navigate to Project Directory**

Open **PowerShell** or **Command Prompt** and run:

```powershell
cd c:\xampp2\htdocs\BSIT3C-DJANGO-MINDMAP
```

---

### **STEP 4: Create Virtual Environment (Recommended)**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If you get an execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### **STEP 5: Install Dependencies**

```powershell
pip install -r requirements.txt
```

This will install:
- Django 5.0.14
- mysqlclient 2.2.8
- openpyxl 3.1.5

---

### **STEP 6: Configure Database Connection**

The database is already configured in `mysite/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mindmap_db',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

**If your MySQL has a password**, edit `mysite/settings.py` and update the `PASSWORD` field.

---

### **STEP 7: Create Django Migrations**

```powershell
python manage.py makemigrations core
python manage.py makemigrations users
```

---

### **STEP 8: Apply Migrations**

```powershell
python manage.py migrate
```

This creates Django's system tables (auth, sessions, etc.) in your database.

---

### **STEP 9: Setup Test Users and Link Database Records**

Run the setup script:

```powershell
python setup_database.py
```

This script will:
- Create an **admin** user
- Create user accounts for all **teachers** in the database
- Create user accounts for all **students** in the database
- Link user accounts to database records

**Default Credentials Created:**
- **Admin**: username=`admin`, password=`admin123`
- **Teachers**: username=[email prefix], password=`teacher123`
- **Students**: username=[student_number], password=`student123`

---

### **STEP 10: Add Sample Data (Optional)**

If your database is empty, add sample data via phpMyAdmin or Django admin:

#### **Option A: Via phpMyAdmin**

1. Open phpMyAdmin
2. Select `mindmap_db`
3. Add records to tables manually

#### **Option B: Via Django Admin**

```powershell
python manage.py runserver
```

Then visit `http://127.0.0.1:8000/admin/` and login with:
- Username: `admin`
- Password: `admin123`

Add teachers, students, subjects, etc.

---

### **STEP 11: Run the Development Server**

```powershell
python manage.py runserver
```

**You should see:**
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

---

### **STEP 12: Access the Application**

Open your browser and visit:

**🌐 http://127.0.0.1:8000/**

You'll see the **Login Page** with a pink theme!

---

## 👥 User Roles and Access

### **1. Admin Dashboard**
- **URL**: `http://127.0.0.1:8000/users/admin/dashboard/`
- **Login**: `admin` / `admin123`
- **Features**:
  - Manage students (add, edit, delete)
  - Manage teachers (add, edit, delete)
  - Manage subjects (add, edit, delete, assign teachers)
  - View all academic records
  - Monitor system statistics

### **2. Teacher Dashboard**
- **URL**: `http://127.0.0.1:8000/users/teacher/dashboard/`
- **Login**: Use teacher email prefix / `teacher123`
- **Features**:
  - View assigned students
  - Record and update grades
  - Create learning assessments
  - Add academic progress reports
  - Monitor student performance

### **3. Student Dashboard**
- **URL**: `http://127.0.0.1:8000/users/student/dashboard/`
- **Login**: Use student number / `student123`
- **Features**:
  - View grades by subject and semester
  - View learning assessments
  - View academic progress reports
  - Identify strengths and areas for improvement
  - View comprehensive progress report

---

## 📁 Project Structure

```
BSIT3C-DJANGO-MINDMAP/
├── apps/
│   ├── core/              # Authentication & user profiles
│   │   ├── models.py      # UserProfile model
│   │   ├── views.py       # Login/logout views
│   │   └── urls.py
│   └── users/             # Main application
│       ├── models.py      # Student, Teacher, Subject, Grade, etc.
│       ├── views.py       # All dashboard and CRUD views
│       └── urls.py
├── mysite/                # Django project settings
│   ├── settings.py        # Database and app configuration
│   └── urls.py            # Main URL routing
├── templates/
│   ├── base.html          # Pink-themed base template
│   ├── auth/
│   │   └── login.html     # Login page
│   └── users/
│       ├── admin/         # Admin templates
│       ├── teacher/       # Teacher templates
│       └── student/       # Student templates
├── static/                # CSS, JS files
├── SQL/
│   └── mindmap_db.sql     # Database structure
├── setup_database.py      # User setup script
└── requirements.txt       # Python dependencies
```

---

## 🎨 Design Features

The system uses a **clean pink theme** with:
- **White background**
- **Light pink rounded boxes** for cards
- **Pink text** for headers and accents
- **Pink primary buttons**
- **Responsive sidebar navigation**
- **Bootstrap-based layout**

---

## 🔧 Common Issues and Solutions

### **Issue 1: MySQL Connection Error**

**Error**: `Can't connect to MySQL server`

**Solution**:
1. Start MySQL in XAMPP
2. Verify database name is `mindmap_db`
3. Check MySQL is running on port 3306

---

### **Issue 2: Module Not Found**

**Error**: `ModuleNotFoundError: No module named 'mysqlclient'`

**Solution**:
```powershell
pip install mysqlclient
```

If that fails on Windows:
```powershell
pip install wheel
pip install mysqlclient
```

---

### **Issue 3: No Users Can Login**

**Solution**: Run the setup script again:
```powershell
python setup_database.py
```

---

### **Issue 4: Profile Not Found Error**

**Error**: `UserProfile matching query does not exist`

**Solution**: The user doesn't have a profile. Run:
```powershell
python setup_database.py
```

Or manually create a profile in Django admin.

---

### **Issue 5: Port Already in Use**

**Error**: `Error: That port is already in use`

**Solution**: Use a different port:
```powershell
python manage.py runserver 8080
```

Then access: `http://127.0.0.1:8080/`

---

## 📝 Adding Sample Data

### **Add a Teacher**

1. Login as admin
2. Go to **Teachers** section
3. Click **Add New Teacher**
4. Fill in:
   - First Name: John
   - Last Name: Doe
   - Email: john.doe@school.com
   - Department: Computer Science
5. Click **Create Teacher**

---

### **Add a Student**

1. Login as admin
2. Go to **Students** section
3. Click **Add New Student**
4. Fill in:
   - Student Number: 2024-0001
   - First Name: Jane
   - Last Name: Smith
   - Email: jane.smith@student.com
   - Course: BSIT
   - Year Level: 3
   - Section: C
5. Click **Create Student**

---

### **Add a Subject**

1. Login as admin
2. Go to **Subjects** section
3. Click **Add New Subject**
4. Fill in:
   - Subject Code: IT311
   - Subject Name: Web Development
   - Units: 3
   - Assign Teacher: Select teacher
5. Click **Create Subject**

---

### **Add Grades (Teacher)**

1. Login as teacher
2. Go to **Grades** section
3. Click **Add New Grade**
4. Fill in:
   - Student: Select student
   - Subject: Select subject
   - School Year: 2023-2024
   - Semester: 1st Semester
   - Prelim: 85
   - Midterm: 88
   - Finals: 90
5. Click **Add Grade**

*Final grade and remarks are calculated automatically!*

---

## 🎓 User Workflow Example

### **Scenario: Teacher Records Student Performance**

1. **Teacher logs in** with their email prefix
2. Goes to **Students** to view all students
3. Goes to **Grades** → **Add New Grade**
4. Selects student and subject
5. Enters prelim, midterm, finals scores
6. System automatically calculates final grade
7. Goes to **Assessments** → **Add Assessment**
8. Records skill area, score, strengths, areas to improve
9. Goes to **Progress** → **Add Progress Record**
10. Documents observation and recommendations

### **Scenario: Student Views Progress**

1. **Student logs in** with student number
2. Sees dashboard with:
   - Average grade
   - Total grades recorded
   - Recent assessments
3. Goes to **My Grades** to view all subjects
4. Goes to **Assessments** to see feedback
5. Goes to **Progress** to read teacher observations
6. Goes to **Progress Report** for comprehensive summary

---

## 🔐 Security Notes

- Default passwords are for **development only**
- **Change all passwords** before deploying
- Set `DEBUG = False` in production
- Use environment variables for secrets
- Enable HTTPS in production

---

## 📞 Testing the System

### **Test Login Flow**

1. Visit `http://127.0.0.1:8000/`
2. Try logging in with wrong credentials → Should show error
3. Login as admin → Should redirect to admin dashboard
4. Logout → Should return to login page
5. Login as teacher → Should redirect to teacher dashboard
6. Login as student → Should redirect to student dashboard

---

## ✅ Completion Checklist

- [ ] MySQL server is running
- [ ] Database `mindmap_db` is created and imported
- [ ] Virtual environment is activated
- [ ] Dependencies are installed
- [ ] Migrations are applied
- [ ] Setup script is run
- [ ] Admin user can login
- [ ] Teacher user can login
- [ ] Student user can login
- [ ] Admin can manage students
- [ ] Teacher can add grades
- [ ] Student can view grades

---

## 🎉 Success!

Your **MindMap Student Academic Progress Monitoring System** is now ready!

**Next Steps:**
1. Add your actual teachers and students
2. Assign subjects to teachers
3. Start recording grades and assessments
4. Monitor student progress

---

## 📚 Additional Resources

- Django Documentation: https://docs.djangoproject.com/
- MySQL Documentation: https://dev.mysql.com/doc/
- Bootstrap Documentation: https://getbootstrap.com/docs/

---

**For Support**: Check error messages in the terminal where you ran `python manage.py runserver`

**Version**: 1.0  
**Last Updated**: October 2026
