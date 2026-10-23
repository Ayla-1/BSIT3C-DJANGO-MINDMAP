import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

# Reset password
user = User.objects.get(username='1')
user.set_password('student123')
user.save()

print("=" * 70)
print("STUDENT PASSWORD RESET")
print("=" * 70)
print(f"\nUsername: 1")
print(f"Password: student123")
print(f"Email: {user.email}")
print(f"Name: {user.get_full_name()}")

# Test authentication
print("\n" + "=" * 70)
print("TESTING AUTHENTICATION")
print("=" * 70)

auth_user = authenticate(username='1', password='student123')

if auth_user:
    print("\n✓ SUCCESS! Authentication works!")
    print(f"  Authenticated as: {auth_user.get_full_name()}")
    print(f"  User ID: {auth_user.id}")
    print(f"  Is active: {auth_user.is_active}")
    
    # Check profile
    try:
        profile = auth_user.profile
        print(f"  Profile role: {profile.role}")
    except:
        print("  ⚠ No profile found")
else:
    print("\n✗ FAILED! Authentication did not work!")

print("\n" + "=" * 70)
print("LOGIN INSTRUCTIONS")
print("=" * 70)
print("\n1. Go to: http://localhost:8000/test-login/")
print("2. Select 'Student' from the dropdown")
print("3. Enter username: 1")
print("4. Enter password: student123")
print("5. Click Login")
print("\n" + "=" * 70)
