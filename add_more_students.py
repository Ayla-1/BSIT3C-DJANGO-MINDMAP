import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User
from apps.users.models import Student
from apps.core.models import UserProfile
from django.db import connection
from datetime import date

print("=" * 70)
print("ADDING MORE SAMPLE STUDENTS")
print("=" * 70)

students_data = [
    {
        'student_number': '2024-0001',
        'first_name': 'Juan',
        'last_name': 'Dela Cruz',
        'email': 'juan.delacruz@example.com',
        'gender': 'Male',
        'birthdate': '2005-03-15',
        'course': 'BSIT',
        'year_level': 1,
        'section': 'A',
    },
    {
        'student_number': '2024-0002',
        'first_name': 'Maria',
        'last_name': 'Santos',
        'email': 'maria.santos@example.com',
        'gender': 'Female',
        'birthdate': '2005-07-22',
        'course': 'BSIT',
        'year_level': 1,
        'section': 'A',
    },
    {
        'student_number': '2024-0003',
        'first_name': 'Pedro',
        'last_name': 'Reyes',
        'email': 'pedro.reyes@example.com',
        'gender': 'Male',
        'birthdate': '2004-11-08',
        'course': 'BSIT',
        'year_level': 2,
        'section': 'B',
    },
    {
        'student_number': '2024-0004',
        'first_name': 'Ana',
        'last_name': 'Garcia',
        'email': 'ana.garcia@example.com',
        'gender': 'Female',
        'birthdate': '2003-05-19',
        'course': 'BSCS',
        'year_level': 3,
        'section': 'A',
    },
    {
        'student_number': '2024-0005',
        'first_name': 'Carlos',
        'last_name': 'Mendoza',
        'email': 'carlos.mendoza@example.com',
        'gender': 'Male',
        'birthdate': '2003-09-30',
        'course': 'BSCS',
        'year_level': 3,
        'section': 'B',
    },
]

added_count = 0
skipped_count = 0

for data in students_data:
    # Check if student already exists
    existing = Student.objects.filter(student_number=data['student_number']).first()
    
    if existing:
        print(f"\n⚠ Skipped: {data['first_name']} {data['last_name']} (already exists)")
        skipped_count += 1
        continue
    
    try:
        # Insert student into database
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO students 
                (student_number, first_name, last_name, email, gender, birthdate, 
                 course, year_level, section, enrollment_date, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """, [
                data['student_number'],
                data['first_name'],
                data['last_name'],
                data['email'],
                data['gender'],
                data['birthdate'],
                data['course'],
                data['year_level'],
                data['section'],
                date.today()
            ])
        
        # Create user account
        user = User.objects.create_user(
            username=data['student_number'],
            email=data['email'],
            password='student123',
            first_name=data['first_name'],
            last_name=data['last_name']
        )
        
        # Create profile
        UserProfile.objects.create(user=user, role='student')
        
        print(f"\n✓ Added: {data['first_name']} {data['last_name']}")
        print(f"  Student Number: {data['student_number']}")
        print(f"  Course: {data['course']} {data['year_level']}-{data['section']}")
        print(f"  Username: {data['student_number']}")
        print(f"  Password: student123")
        
        added_count += 1
        
    except Exception as e:
        print(f"\n✗ Error adding {data['first_name']} {data['last_name']}: {e}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"\nStudents added: {added_count}")
print(f"Students skipped: {skipped_count}")
print(f"Total students now: {Student.objects.count()}")

if added_count > 0:
    print("\n" + "=" * 70)
    print("LOGIN CREDENTIALS FOR NEW STUDENTS")
    print("=" * 70)
    print("\nYou can login with any of these accounts:")
    print("\nURL: http://localhost:8000/test-login/")
    print("Role: Student")
    print("Password: student123\n")
    
    for data in students_data:
        if Student.objects.filter(student_number=data['student_number']).exists():
            print(f"  Username: {data['student_number']} → {data['first_name']} {data['last_name']} ({data['course']} {data['year_level']}-{data['section']})")

print("\n" + "=" * 70)
