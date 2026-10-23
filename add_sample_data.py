"""
Add sample data for testing the MindMap system
"""
import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User
from apps.core.models import UserProfile
from apps.users.models import Student, Teacher, Subject, Grade, LearningAssessment, AcademicProgress

print("=" * 60)
print("Adding Sample Data")
print("=" * 60)

# Add Teachers
print("\n📋 Adding Teachers...")
teachers_data = [
    {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@school.com',
        'department': 'Computer Science'
    },
    {
        'first_name': 'Jane',
        'last_name': 'Smith',
        'email': 'jane.smith@school.com',
        'department': 'Mathematics'
    },
    {
        'first_name': 'Robert',
        'last_name': 'Johnson',
        'email': 'robert.johnson@school.com',
        'department': 'English'
    }
]

created_teachers = []
for data in teachers_data:
    # Check if teacher already exists
    if Teacher.objects.filter(email=data['email']).exists():
        print(f"  - {data['first_name']} {data['last_name']} already exists")
        teacher = Teacher.objects.get(email=data['email'])
        created_teachers.append(teacher)
    else:
        teacher = Teacher(**data)
        teacher.save()
        print(f"  ✓ Created teacher: {teacher.get_full_name()}")
        created_teachers.append(teacher)
        
        # Create user account
        username = data['email'].split('@')[0]
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=data['email'],
                password='teacher123',
                first_name=data['first_name'],
                last_name=data['last_name']
            )
            UserProfile.objects.create(user=user, role='teacher')
            print(f"    ✓ Created user: {username} / teacher123")

# Add Students
print("\n👨‍🎓 Adding Students...")
students_data = [
    {
        'student_number': '2024-0001',
        'first_name': 'Alice',
        'last_name': 'Williams',
        'email': 'alice.williams@student.com',
        'gender': 'Female',
        'course': 'BSIT',
        'year_level': 3,
        'section': 'C',
        'birthdate': date(2003, 5, 15),
        'enrollment_date': date(2021, 8, 1)
    },
    {
        'student_number': '2024-0002',
        'first_name': 'Bob',
        'last_name': 'Brown',
        'email': 'bob.brown@student.com',
        'gender': 'Male',
        'course': 'BSIT',
        'year_level': 3,
        'section': 'C',
        'birthdate': date(2003, 8, 22),
        'enrollment_date': date(2021, 8, 1)
    },
    {
        'student_number': '2024-0003',
        'first_name': 'Carol',
        'last_name': 'Davis',
        'email': 'carol.davis@student.com',
        'gender': 'Female',
        'course': 'BSIT',
        'year_level': 3,
        'section': 'C',
        'birthdate': date(2003, 11, 30),
        'enrollment_date': date(2021, 8, 1)
    }
]

created_students = []
for data in students_data:
    if Student.objects.filter(student_number=data['student_number']).exists():
        print(f"  - {data['student_number']} already exists")
        student = Student.objects.get(student_number=data['student_number'])
        created_students.append(student)
    else:
        student = Student(**data)
        student.save()
        print(f"  ✓ Created student: {student.student_number} - {student.get_full_name()}")
        created_students.append(student)
        
        # Create user account
        username = data['student_number']
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=data['email'],
                password='student123',
                first_name=data['first_name'],
                last_name=data['last_name']
            )
            UserProfile.objects.create(user=user, role='student')
            print(f"    ✓ Created user: {username} / student123")

# Add Subjects
print("\n📚 Adding Subjects...")
subjects_data = [
    {
        'subject_code': 'IT311',
        'subject_name': 'Web Development',
        'units': 3,
        'teacher': created_teachers[0] if created_teachers else None
    },
    {
        'subject_code': 'IT312',
        'subject_name': 'Database Management',
        'units': 3,
        'teacher': created_teachers[0] if created_teachers else None
    },
    {
        'subject_code': 'MATH301',
        'subject_name': 'Statistics',
        'units': 3,
        'teacher': created_teachers[1] if len(created_teachers) > 1 else None
    },
    {
        'subject_code': 'ENG301',
        'subject_name': 'Technical Writing',
        'units': 3,
        'teacher': created_teachers[2] if len(created_teachers) > 2 else None
    }
]

created_subjects = []
for data in subjects_data:
    if Subject.objects.filter(subject_code=data['subject_code']).exists():
        print(f"  - {data['subject_code']} already exists")
        subject = Subject.objects.get(subject_code=data['subject_code'])
        created_subjects.append(subject)
    else:
        subject = Subject(**data)
        subject.save()
        teacher_name = subject.teacher.get_full_name() if subject.teacher else "Unassigned"
        print(f"  ✓ Created subject: {subject.subject_code} - {subject.subject_name} (Teacher: {teacher_name})")
        created_subjects.append(subject)

# Add Sample Grades
print("\n📝 Adding Sample Grades...")
if created_students and created_subjects and created_teachers:
    grades_data = [
        {
            'student': created_students[0],
            'subject': created_subjects[0],
            'school_year': '2023-2024',
            'semester': '1st Semester',
            'prelim': 85.0,
            'midterm': 88.0,
            'finals': 90.0,
            'recorded_by': created_teachers[0]
        },
        {
            'student': created_students[0],
            'subject': created_subjects[1],
            'school_year': '2023-2024',
            'semester': '1st Semester',
            'prelim': 82.0,
            'midterm': 85.0,
            'finals': 87.0,
            'recorded_by': created_teachers[0]
        }
    ]
    
    for data in grades_data:
        # Calculate final grade
        data['final_grade'] = (data['prelim'] + data['midterm'] + data['finals']) / 3
        data['remarks'] = 'PASSED' if data['final_grade'] >= 75 else 'FAILED'
        
        # Check if grade already exists
        if not Grade.objects.filter(
            student=data['student'],
            subject=data['subject'],
            school_year=data['school_year'],
            semester=data['semester']
        ).exists():
            grade = Grade(**data)
            grade.save()
            print(f"  ✓ Added grade: {grade.student.student_number} - {grade.subject.subject_code} - {grade.final_grade:.2f}")

# Add Sample Assessment
print("\n📋 Adding Sample Assessment...")
if created_students and created_subjects and created_teachers:
    assessment_data = {
        'student': created_students[0],
        'subject': created_subjects[0],
        'teacher': created_teachers[0],
        'assessment_date': date.today(),
        'skill_area': 'Programming Logic',
        'assessment_type': 'Quiz',
        'score': 45.0,
        'max_score': 50.0,
        'strengths': 'Strong understanding of basic concepts, excellent problem-solving skills',
        'areas_to_improve': 'Need more practice with advanced algorithms',
        'notes': 'Shows great potential'
    }
    
    if not LearningAssessment.objects.filter(
        student=assessment_data['student'],
        subject=assessment_data['subject'],
        assessment_date=assessment_data['assessment_date'],
        skill_area=assessment_data['skill_area']
    ).exists():
        assessment = LearningAssessment(**assessment_data)
        assessment.save()
        print(f"  ✓ Added assessment for {assessment.student.student_number}")

# Add Sample Progress
print("\n📈 Adding Sample Progress...")
if created_students and created_teachers:
    progress_data = {
        'student': created_students[0],
        'teacher': created_teachers[0],
        'assessment_date': date.today(),
        'progress_category': 'Academic Performance',
        'observation': 'Student shows consistent improvement in programming skills. Actively participates in class discussions.',
        'recommendation': 'Continue with current learning pace. Consider advanced programming challenges.',
        'status': 'Excellent'
    }
    
    if not AcademicProgress.objects.filter(
        student=progress_data['student'],
        assessment_date=progress_data['assessment_date'],
        progress_category=progress_data['progress_category']
    ).exists():
        progress = AcademicProgress(**progress_data)
        progress.save()
        print(f"  ✓ Added progress record for {progress.student.student_number}")

print("\n" + "=" * 60)
print("✅ Sample Data Added Successfully!")
print("=" * 60)
print("\nYou can now login as:")
print("\n📋 Teachers:")
for teacher in created_teachers:
    username = teacher.email.split('@')[0]
    print(f"  - Username: {username}")
    print(f"    Password: teacher123")
    print(f"    Name: {teacher.get_full_name()}")

print("\n👨‍🎓 Students:")
for student in created_students:
    print(f"  - Username: {student.student_number}")
    print(f"    Password: student123")
    print(f"    Name: {student.get_full_name()}")

print("\n👤 Admin:")
print("  - Username: admin")
print("  - Password: admin123")

print("\n" + "=" * 60)
print("Next: Run 'python manage.py runserver' and test!")
print("=" * 60)
