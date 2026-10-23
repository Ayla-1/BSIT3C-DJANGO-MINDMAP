# MindMap: Student Academic Progress Monitoring System

**Developed by**: Cayao, Kristel Ayla P. / Claro, Asheralyn P. / Fernandez, Wendelyn V.

A comprehensive web-based system built with Django for monitoring and managing student academic progress, grades, assessments, and performance tracking.

## 🎯 Features

### For Administrators
- Manage student accounts (add, edit, delete)
- Manage teacher accounts (add, edit, delete)
- Manage subjects and assign teachers
- View comprehensive system statistics
- Monitor overall academic performance

### For Teachers
- View assigned students and subjects
- Record and update student grades (prelim, midterm, finals)
- Create learning assessments with detailed feedback
- Document academic progress observations
- Track student strengths and areas for improvement
- Monitor student performance across subjects

### For Students
- View personal dashboard with academic overview
- Access grades by subject and semester
- View learning assessment results
- Read academic progress reports from teachers
- Identify personal strengths and improvement areas
- Generate comprehensive progress reports

## 🎨 Design
- Clean, modern interface with pink theme
- White background with light pink rounded cards
- Responsive sidebar navigation
- Mobile-friendly design
- Bootstrap-based layout

## 🛠️ Technology Stack
- **Backend**: Python 3.13, Django 5.0
- **Database**: MySQL/MariaDB
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap
- **Theme**: Custom pink-themed design

## 📚 Quick Start

### Prerequisites
- Python 3.13+ installed
- MySQL/MariaDB (XAMPP) running
- Git (optional)

### Installation

1. **Navigate to project directory**
   ```bash
   cd c:\xampp2\htdocs\BSIT3C-DJANGO-MINDMAP
   ```

2. **Create virtual environment (recommended)**
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup database**
   - Start MySQL in XAMPP
   - Import `SQL/mindmap_db.sql` via phpMyAdmin
   - Database name should be `mindmap_db`

5. **Test database connection**
   ```bash
   python test_connection.py
   ```

6. **Run migrations**
   ```bash
   python manage.py migrate
   ```

7. **Create user accounts**
   ```bash
   python setup_database.py
   ```

8. **Start the server**
   ```bash
   python manage.py runserver
   ```
   
   Or simply double-click `start_server.bat`

9. **Access the application**
   - Open browser and visit: `http://127.0.0.1:8000/`
   - Login with default credentials (see below)

## 🔐 Default Login Credentials

After running `setup_database.py`:

- **Admin**: 
  - Username: `admin`
  - Password: `admin123`

- **Teachers**: 
  - Username: `[email prefix]` (e.g., john.doe for john.doe@school.com)
  - Password: `teacher123`

- **Students**: 
  - Username: `[student_number]`
  - Password: `student123`

## 📁 Project Structure

```
BSIT3C-DJANGO-MINDMAP/
├── apps/
│   ├── core/              # Authentication & profiles
│   ├── users/             # Main app (models, views)
│   └── info/              # Additional info app
├── mysite/                # Project settings
├── templates/             # HTML templates
│   ├── base.html         # Pink-themed base
│   ├── auth/             # Login pages
│   └── users/            # Role-based templates
├── static/               # CSS, JS files
├── SQL/                  # Database files
├── setup_database.py     # User setup script
├── test_connection.py    # DB test script
└── requirements.txt      # Dependencies
```

## 🗄️ Database Structure

### Tables
- **students**: Student information
- **teachers**: Teacher information
- **subjects**: Subject details
- **grades**: Grade records (prelim, midterm, finals)
- **learning_assessments**: Skill assessments and feedback
- **academic_progress**: Progress observations and recommendations

## 📖 Detailed Setup Guide

For complete step-by-step instructions, see [SETUP_GUIDE.md](SETUP_GUIDE.md)

## 🧪 Testing

After setup, verify:
1. Login with admin credentials
2. Create a test teacher
3. Create a test student
4. Create a subject and assign to teacher
5. Login as teacher and add grades
6. Login as student and view grades

## 🔧 Troubleshooting

### Can't connect to MySQL
- Ensure MySQL is running in XAMPP
- Verify database name is `mindmap_db`
- Check credentials in `mysite/settings.py`

### No module named 'mysqlclient'
```bash
pip install mysqlclient
```

### Profile not found error
```bash
python setup_database.py
```

### Port already in use
```bash
python manage.py runserver 8080
```

## 📝 Usage Examples

### Adding a Grade (Teacher)
1. Login as teacher
2. Navigate to Grades → Add New Grade
3. Select student and subject
4. Enter prelim, midterm, finals scores
5. System auto-calculates final grade
6. Submit

### Viewing Progress (Student)
1. Login as student
2. Dashboard shows overview
3. My Grades: View all grades
4. Assessments: View feedback
5. Progress: Read teacher observations
6. Progress Report: Comprehensive summary

## 🚀 Deployment Notes

Before deploying to production:
- Change all default passwords
- Set `DEBUG = False` in settings.py
- Use environment variables for secrets
- Enable HTTPS
- Use proper WSGI server (Gunicorn/uWSGI)
- Configure static files properly

## 📄 License

Educational project - for academic use.

## 📞 Support

For issues or questions:
- Check error messages in terminal
- Review SETUP_GUIDE.md
- Verify database connection
- Ensure all migrations are applied

---

**Version**: 1.0  
**Last Updated**: October 2026  
**Python**: 3.13.15  
**Django**: 5.0.14
