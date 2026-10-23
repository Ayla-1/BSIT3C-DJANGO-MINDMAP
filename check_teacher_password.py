import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User

print("=" * 70)
print("CHECKING TEACHER PASSWORD")
print("=" * 70)

username = 'aylakristel110104'

try:
    user = User.objects.get(username=username)
    print(f"\n✓ User '{username}' exists")
    print(f"  Email: {user.email}")
    print(f"  Is active: {user.is_active}")
    print(f"  Has usable password: {user.has_usable_password()}")
    
    # Test authentication with common passwords
    from django.contrib.auth import authenticate
    
    print("\n" + "=" * 70)
    print("TESTING COMMON PASSWORDS")
    print("=" * 70)
    
    test_passwords = ['teacher123', 'password', '123456', 'admin123']
    
    for pwd in test_passwords:
        auth_user = authenticate(username=username, password=pwd)
        if auth_user:
            print(f"\n✓ SUCCESS! Password is: {pwd}")
            break
        else:
            print(f"  ✗ '{pwd}' - incorrect")
    else:
        print("\n⚠ None of the common passwords worked")
        print("\nResetting password to 'teacher123'...")
        user.set_password('teacher123')
        user.save()
        print("✓ Password reset complete!")
        print(f"\nYou can now login with:")
        print(f"  Username: {username}")
        print(f"  Password: teacher123")
        
except User.DoesNotExist:
    print(f"\n✗ User '{username}' does not exist!")
    print("\nCreating user now...")
    
    from apps.users.models import Teacher
    from apps.core.models import UserProfile
    
    teacher = Teacher.objects.get(email='aylakristel110104@gmail.com')
    
    user = User.objects.create_user(
        username=username,
        email=teacher.email,
        password='teacher123',
        first_name=teacher.first_name,
        last_name=teacher.last_name
    )
    
    UserProfile.objects.create(user=user, role='teacher')
    
    print(f"✓ User created successfully!")
    print(f"\nYou can now login with:")
    print(f"  Username: {username}")
    print(f"  Password: teacher123")
