"""
Script to create Django tables directly
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.core.management import call_command
from django.db import connection

print("=" * 60)
print("Creating Django Tables")
print("=" * 60)

# Check current tables
print("\nChecking existing tables...")
with connection.cursor() as cursor:
    cursor.execute("SHOW TABLES")
    existing_tables = [table[0] for table in cursor.fetchall()]
    print(f"Found {len(existing_tables)} tables")

# Run migrate with run-syncdb
print("\nRunning migrate --run-syncdb...")
try:
    call_command('migrate', '--run-syncdb', verbosity=2)
    print("\n✓ Migrations completed successfully!")
except Exception as e:
    print(f"\n✗ Error: {e}")
    sys.exit(1)

# Check tables after migration
print("\nVerifying tables were created...")
with connection.cursor() as cursor:
    cursor.execute("SHOW TABLES")
    new_tables = [table[0] for table in cursor.fetchall()]
    print(f"Now have {len(new_tables)} tables")
    
    # Check for auth_user specifically
    if 'auth_user' in new_tables:
        print("\n✓ auth_user table exists!")
    else:
        print("\n✗ auth_user table NOT found!")
        
    # List all tables
    print("\nAll tables in database:")
    for table in sorted(new_tables):
        print(f"  - {table}")

print("\n" + "=" * 60)
print("✓ Table creation complete!")
print("=" * 60)
print("\nNext step: Create admin user")
print("Run: python manage.py createsuperuser")
print("=" * 60)
