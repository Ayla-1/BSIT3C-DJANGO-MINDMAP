import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User
from apps.users.models import Student
from apps.core.models import UserProfile

print("=" * 70)
print("DEBUGGING STUDENT LOGIN")
print("=" * 70)

# Check students in database
print("\n1. Checking Students in Database:")
print("-" * 70)
students = Student.objects.all()
print(f"Total students: {students.count()}")

if students.count() == 0:
    print("\n⚠ No students found in database!")
    print("You need to add students first.")
else:
    for student in students[:10]:  # Show first 10
        print(f"\n  Student: {student.get_full_name()}")
        print(f"  Student Number: {student.student_number}")
        print(f"  Email: {student.email}")
        print(f"  Course: {student.course} {student.year_level}-{student.section}")
        
        # Check if user account exists
        expected_username = student.student_number
        try:
            user = User.objects.get(username=expected_username)
            print(f"  ✓ User account exists (username: {expected_username})")
            
            # Check if profile exists
            try:
                profile = user.profile
                print(f"  ✓ Profile exists (role: {profile.role})")
            except UserProfile.DoesNotExist:
                print(f"  ✗ Profile does NOT exist!")
                
        except User.DoesNotExist:
            print(f"  ✗ User account does NOT exist")
            print(f"     Expected username: {expected_username}")

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

students_with_users = 0
students_without_users = 0
students_without_profiles = 0

for student in students:
    try:
        user = User.objects.get(username=student.student_number)
        students_with_users += 1
        try:
            user.profile
        except UserProfile.DoesNotExist:
            students_without_profiles += 1
    except User.DoesNotExist:
        students_without_users += 1

print(f"\nTotal students in database: {students.count()}")
print(f"Students WITH user accounts: {students_with_users}")
print(f"Students WITHOUT user accounts: {students_without_users}")
print(f"Students WITHOUT profiles: {students_without_profiles}")

if students_without_users > 0:
    print("\n" + "=" * 70)
    print("CREATING MISSING USER ACCOUNTS")
    print("=" * 70)
    
    for student in students:
        try:
            User.objects.get(username=student.student_number)
        except User.DoesNotExist:
            # Create user
            user = User.objects.create_user(
                username=student.student_number,
                email=student.email or f"{student.student_number}@mindmap.edu",
                password='student123',
                first_name=student.first_name,
                last_name=student.last_name
            )
            
            # Create profile
            UserProfile.objects.create(user=user, role='student')
            
            print(f"\n✓ Created user for: {student.get_full_name()}")
            print(f"  Username: {student.student_number}")
            print(f"  Password: student123")

if students_without_profiles > 0:
    print("\n" + "=" * 70)
    print("CREATING MISSING PROFILES")
    print("=" * 70)
    
    for student in students:
        try:
            user = User.objects.get(username=student.student_number)
            try:
                user.profile
            except UserProfile.DoesNotExist:
                UserProfile.objects.create(user=user, role='student')
                print(f"✓ Created profile for: {student.get_full_name()}")
        except User.DoesNotExist:
            pass

# Show login instructions
if students.count() > 0:
    print("\n" + "=" * 70)
    print("STUDENT LOGIN CREDENTIALS")
    print("=" * 70)
    print("\nYou can login with any of these student accounts:")
    
    for student in students[:5]:  # Show first 5
        try:
            user = User.objects.get(username=student.student_number)
            print(f"\n  Student: {student.get_full_name()}")
            print(f"  Username: {student.student_number}")
            print(f"  Password: student123")
        except User.DoesNotExist:
            pass
    
    print("\n" + "=" * 70)
    print(f"\nLogin URL: http://localhost:8000/test-login/")
    print("Select 'Student' from the role dropdown")
    print("=" * 70)
