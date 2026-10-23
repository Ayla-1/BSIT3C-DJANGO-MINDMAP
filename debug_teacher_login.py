"""
Debug teacher login issues
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from apps.core.models import UserProfile
from apps.users.models import Teacher

print("=" * 70)
print("DEBUGGING TEACHER LOGIN")
print("=" * 70)

# Check if teachers exist in database
print("\n1. Checking Teachers in Database:")
print("-" * 70)
teachers = Teacher.objects.all()
print(f"Total teachers: {teachers.count()}")

if teachers.count() == 0:
    print("\n❌ NO TEACHERS FOUND IN DATABASE!")
    print("\nYou need to add teachers first. Run:")
    print("  python add_sample_data.py")
else:
    for teacher in teachers:
        print(f"\n  Teacher: {teacher.get_full_name()}")
        print(f"  Email: {teacher.email}")
        
        # Get expected username
        username = teacher.email.split('@')[0]
        print(f"  Expected username: {username}")
        
        # Check if user exists
        try:
            user = User.objects.get(username=username)
            print(f"  ✓ User account exists")
            
            # Check profile
            try:
                profile = user.profile
                print(f"  ✓ Profile exists (role: {profile.role})")
                
                # Test authentication
                auth_user = authenticate(username=username, password='teacher123')
                if auth_user:
                    print(f"  ✓ Authentication works! Can login with: {username} / teacher123")
                else:
                    print(f"  ✗ Authentication FAILED!")
                    print(f"    - User exists but password is wrong")
                    print(f"    - Try resetting password")
                    
            except UserProfile.DoesNotExist:
                print(f"  ✗ User exists but NO PROFILE!")
                print(f"    - Run: python setup_database.py")
                
        except User.DoesNotExist:
            print(f"  ✗ NO USER ACCOUNT for this teacher!")
            print(f"    - Run: python setup_database.py")

# List all users
print("\n" + "=" * 70)
print("2. All Django Users:")
print("-" * 70)
users = User.objects.all()
if users.count() == 0:
    print("❌ NO USERS FOUND!")
else:
    for user in users:
        print(f"\n  Username: {user.username}")
        print(f"  Email: {user.email}")
        print(f"  Name: {user.get_full_name()}")
        
        try:
            profile = user.profile
            print(f"  Role: {profile.role}")
        except UserProfile.DoesNotExist:
            print(f"  Role: NO PROFILE!")
        
        # Test authentication
        test_passwords = ['teacher123', 'student123', 'admin123']
        for pwd in test_passwords:
            if authenticate(username=user.username, password=pwd):
                print(f"  ✓ Can login with: {user.username} / {pwd}")
                break
        else:
            print(f"  ✗ None of the default passwords work")

# Test specific teacher login
print("\n" + "=" * 70)
print("3. Testing Specific Teacher Login: john.doe")
print("-" * 70)

username = 'john.doe'
password = 'teacher123'

print(f"Attempting: {username} / {password}")

# Check if user exists
if User.objects.filter(username=username).exists():
    user = User.objects.get(username=username)
    print(f"✓ User '{username}' exists")
    print(f"  Email: {user.email}")
    print(f"  Active: {user.is_active}")
    
    # Check profile
    try:
        profile = user.profile
        print(f"✓ Profile exists (role: {profile.role})")
    except UserProfile.DoesNotExist:
        print(f"✗ NO PROFILE!")
    
    # Test authentication
    auth_user = authenticate(username=username, password=password)
    if auth_user:
        print(f"✓ AUTHENTICATION SUCCESS!")
        print(f"\n  YOU CAN LOGIN WITH:")
        print(f"  Username: {username}")
        print(f"  Password: {password}")
    else:
        print(f"✗ AUTHENTICATION FAILED!")
        print(f"\n  Possible reasons:")
        print(f"  1. Wrong password")
        print(f"  2. User is inactive")
        print(f"  3. Password not set correctly")
        print(f"\n  FIX: Reset password")
        user.set_password('teacher123')
        user.save()
        print(f"  ✓ Password reset to 'teacher123'")
        print(f"  Try logging in now!")
else:
    print(f"✗ User '{username}' DOES NOT EXIST!")
    print(f"\n  Need to create it. Checking if teacher exists...")
    
    if Teacher.objects.filter(email__startswith=username).exists():
        teacher = Teacher.objects.filter(email__startswith=username).first()
        print(f"  ✓ Teacher found: {teacher.get_full_name()}")
        print(f"  Creating user account...")
        
        user = User.objects.create_user(
            username=username,
            email=teacher.email,
            password='teacher123',
            first_name=teacher.first_name,
            last_name=teacher.last_name
        )
        UserProfile.objects.create(user=user, role='teacher')
        
        print(f"  ✓ User created!")
        print(f"\n  YOU CAN NOW LOGIN WITH:")
        print(f"  Username: {username}")
        print(f"  Password: teacher123")
    else:
        print(f"  ✗ No teacher with email starting with '{username}'")
        print(f"  Run: python add_sample_data.py")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

# Final check
working_accounts = []
print("\n✓ WORKING ACCOUNTS:")

for user in User.objects.all():
    for pwd in ['admin123', 'teacher123', 'student123']:
        if authenticate(username=user.username, password=pwd):
            try:
                role = user.profile.role
            except:
                role = "no profile"
            working_accounts.append((user.username, pwd, role))
            print(f"  {user.username} / {pwd} ({role})")
            break

if not working_accounts:
    print("  ❌ NO WORKING ACCOUNTS FOUND!")
    print("\n  RUN THIS:")
    print("  1. python add_sample_data.py")
    print("  2. python setup_database.py")

print("\n" + "=" * 70)
