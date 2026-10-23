"""
Setup script for MindMap Database
This script will create test users and link them to existing database records
Run this after setting up the MySQL database
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User
from apps.core.models import UserProfile
from apps.users.models import Student, Teacher

def create_admin_user():
    """Create admin user"""
    print("\n=== Creating Admin User ===")
    
    # Check if admin already exists
    if User.objects.filter(username='admin').exists():
        print("Admin user already exists!")
        admin_user = User.objects.get(username='admin')
    else:
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@mindmap.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        print("✓ Admin user created: username='admin', password='admin123'")
    
    # Create or get profile
    profile, created = UserProfile.objects.get_or_create(
        user=admin_user,
        defaults={'role': 'admin'}
    )
    if created:
        print("✓ Admin profile created")
    else:
        print("✓ Admin profile already exists")
    
    return admin_user

def create_teacher_users():
    """Create users for existing teachers in database"""
    print("\n=== Creating Teacher Users ===")
    
    teachers = Teacher.objects.all()
    if not teachers.exists():
        print("No teachers found in database. Please add teachers first.")
        return
    
    created_count = 0
    for teacher in teachers:
        # Create username from email
        username = teacher.email.split('@')[0]
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            print(f"- User for {teacher.get_full_name()} already exists")
            user = User.objects.get(username=username)
        else:
            user = User.objects.create_user(
                username=username,
                email=teacher.email,
                password='teacher123',  # Default password
                first_name=teacher.first_name,
                last_name=teacher.last_name
            )
            print(f"✓ Created user for {teacher.get_full_name()}: username='{username}', password='teacher123'")
            created_count += 1
        
        # Create profile
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'role': 'teacher'}
        )
    
    print(f"\n✓ Processed {teachers.count()} teachers, created {created_count} new users")

def create_student_users():
    """Create users for existing students in database"""
    print("\n=== Creating Student Users ===")
    
    students = Student.objects.all()
    if not students.exists():
        print("No students found in database. Please add students first.")
        return
    
    created_count = 0
    for student in students:
        # Use student_number as username
        username = student.student_number
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            print(f"- User for {student.get_full_name()} already exists")
            user = User.objects.get(username=username)
        else:
            user = User.objects.create_user(
                username=username,
                email=student.email or f"{username}@student.mindmap.com",
                password='student123',  # Default password
                first_name=student.first_name,
                last_name=student.last_name
            )
            print(f"✓ Created user for {student.get_full_name()}: username='{username}', password='student123'")
            created_count += 1
        
        # Create profile
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'role': 'student'}
        )
    
    print(f"\n✓ Processed {students.count()} students, created {created_count} new users")

def main():
    """Main setup function"""
    print("=" * 60)
    print("MindMap Database Setup")
    print("=" * 60)
    
    try:
        # Create admin
        create_admin_user()
        
        # Create teacher users
        create_teacher_users()
        
        # Create student users
        create_student_users()
        
        print("\n" + "=" * 60)
        print("✓ SETUP COMPLETE!")
        print("=" * 60)
        print("\nDefault Login Credentials:")
        print("-" * 60)
        print("Admin:")
        print("  Username: admin")
        print("  Password: admin123")
        print("\nTeachers:")
        print("  Username: [email prefix]")
        print("  Password: teacher123")
        print("\nStudents:")
        print("  Username: [student_number]")
        print("  Password: student123")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
