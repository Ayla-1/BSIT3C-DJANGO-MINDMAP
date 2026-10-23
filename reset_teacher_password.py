import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User

username = 'aylakristel110104'

try:
    user = User.objects.get(username=username)
    user.set_password('teacher123')
    user.save()
    
    print(f"✓ Password reset successful!")
    print(f"\nLogin credentials:")
    print(f"  Username: {username}")
    print(f"  Password: teacher123")
    print(f"\nGo to: http://localhost:8000/test-login/")
    
except User.DoesNotExist:
    print(f"✗ User '{username}' not found!")
