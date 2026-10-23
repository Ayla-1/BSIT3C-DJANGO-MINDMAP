"""
Quick test script to verify database connection and setup
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.db import connection

def test_database_connection():
    """Test if we can connect to the database"""
    print("\n" + "=" * 60)
    print("Testing Database Connection")
    print("=" * 60)
    
    try:
        # Test connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        
        print("✓ Database connection successful!")
        
        # Show database info
        print(f"\nDatabase: {connection.settings_dict['NAME']}")
        print(f"Host: {connection.settings_dict['HOST']}")
        print(f"Port: {connection.settings_dict['PORT']}")
        
        # Check tables
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
        
        print(f"\n✓ Found {len(tables)} tables in database:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Count records
        from apps.users.models import Student, Teacher, Subject
        
        print("\n" + "-" * 60)
        print("Current Record Counts:")
        print("-" * 60)
        print(f"Students: {Student.objects.count()}")
        print(f"Teachers: {Teacher.objects.count()}")
        print(f"Subjects: {Subject.objects.count()}")
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nYour database is ready to use!")
        print("Run 'python setup_database.py' to create user accounts.")
        print("=" * 60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("\nPlease check:")
        print("1. MySQL/XAMPP is running")
        print("2. Database 'mindmap_db' exists")
        print("3. Database credentials in settings.py are correct")
        print("=" * 60 + "\n")
        return False

if __name__ == '__main__':
    test_database_connection()
