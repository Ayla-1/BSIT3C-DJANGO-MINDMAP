"""
Check current database data and add sample data if needed
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User
from apps.core.models import UserProfile
from apps.users.models import Student, Teacher, Subject

print("=" * 60)
print("Database Status Check")
print("=" * 60)

# Check Teachers
print("\n📋 TEACHERS:")
teachers = Teacher.objects.all()
print(f"Total: {teachers.count()}")
for teacher in teachers:
    print(f"  - {teacher.get_full_name()} ({teacher.email})")
    # Check if user exists
    username = teacher.email.split('@')[0]
    try:
        user = User.objects.get(username=username)
        profile = user.profile
        print(f"    ✓ User exists: {username} (role: {profile.role})")
    except User.DoesNotExist:
        print(f"    ✗ No user account yet")
    except UserProfile.DoesNotExist:
        print(f"    ⚠ User exists but no profile")

# Check Students
print("\n👨‍🎓 STUDENTS:")
students = Student.objects.all()
print(f"Total: {students.count()}")
for student in students[:5]:  # Show first 5
    print(f"  - {student.student_number}: {student.get_full_name()}")
    try:
        user = User.objects.get(username=student.student_number)
        profile = user.profile
        print(f"    ✓ User exists (role: {profile.role})")
    except User.DoesNotExist:
        print(f"    ✗ No user account yet")
    except UserProfile.DoesNotExist:
        print(f"    ⚠ User exists but no profile")

if students.count() > 5:
    print(f"  ... and {students.count() - 5} more")

# Check Subjects
print("\n📚 SUBJECTS:")
subjects = Subject.objects.all()
print(f"Total: {subjects.count()}")
for subject in subjects[:5]:
    teacher_name = subject.teacher.get_full_name() if subject.teacher else "Unassigned"
    print(f"  - {subject.subject_code}: {subject.subject_name} (Teacher: {teacher_name})")

# Check Users
print("\n👤 DJANGO USERS:")
users = User.objects.all()
print(f"Total: {users.count()}")
for user in users:
    try:
        profile = user.profile
        print(f"  - {user.username} ({user.get_full_name()}) - Role: {profile.role}")
    except UserProfile.DoesNotExist:
        print(f"  - {user.username} ({user.get_full_name()}) - No profile!")

print("\n" + "=" * 60)
print("RECOMMENDATIONS:")
print("=" * 60)

if teachers.count() == 0:
    print("\n⚠ No teachers found!")
    print("  Run this to add sample teacher:")
    print("  python add_sample_data.py")
    
if students.count() == 0:
    print("\n⚠ No students found!")
    print("  Run this to add sample student:")
    print("  python add_sample_data.py")

# Check for users without profiles
users_without_profile = []
for user in User.objects.all():
    try:
        user.profile
    except UserProfile.DoesNotExist:
        users_without_profile.append(user.username)

if users_without_profile:
    print(f"\n⚠ {len(users_without_profile)} users without profiles:")
    for username in users_without_profile:
        print(f"  - {username}")
    print("  Run: python setup_database.py to fix")

# Check for teachers/students without users
teachers_without_users = []
for teacher in teachers:
    username = teacher.email.split('@')[0]
    if not User.objects.filter(username=username).exists():
        teachers_without_users.append(teacher.email)

students_without_users = []
for student in students:
    if not User.objects.filter(username=student.student_number).exists():
        students_without_users.append(student.student_number)

if teachers_without_users or students_without_users:
    print(f"\n⚠ Some records don't have user accounts:")
    if teachers_without_users:
        print(f"  Teachers without users: {len(teachers_without_users)}")
    if students_without_users:
        print(f"  Students without users: {len(students_without_users)}")
    print("  Run: python setup_database.py to create them")

if teachers.count() > 0 and students.count() > 0 and len(users_without_profile) == 0:
    print("\n✅ Database looks good!")
    print("\nYou can now:")
    print("  1. Login as admin: admin / admin123")
    print("  2. Login as teacher: [email_prefix] / teacher123")
    print("  3. Login as student: [student_number] / student123")

print("=" * 60)
