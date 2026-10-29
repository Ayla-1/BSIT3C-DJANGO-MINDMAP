"""Seed the high school demo data set.

Usage:
    python manage.py seed_highschool

Creates (idempotently):
  * an administrator account
  * two sections (Section A and Section B, Grade 11)
  * three teacher accounts with exactly two subjects each
  * the six high school subjects
  * 22 students (11 per section) with their own student accounts
  * quarterly grades, learning assessments, academic progress notes
  * a few announcements
"""

import random
from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.core.models import UserProfile
from apps.users.models import (
    AcademicProgress,
    Announcement,
    Grade,
    LearningAssessment,
    Section,
    Student,
    Subject,
    Teacher,
)


CURRENT_YEAR = '2026-2027'
PREVIOUS_YEAR = '2025-2026'

SUBJECTS = [
    ('MATH', 'Mathematics'),
    ('SCI', 'Science'),
    ('ENG', 'English'),
    ('FIL', 'Filipino'),
    ('AP', 'Araling Panlipunan'),
    ('ESP', 'Edukasyon sa Pagpapakatao'),
]

TEACHERS = [
    {
        'first_name': 'Ayla',
        'last_name': 'Cayao',
        'username': 'ayla.cayao',
        'email': 'ayla.cayao@mindmap.edu.ph',
        'password': 'lala123',
        'department': 'Mathematics and Science',
        'specialization': 'Mathematics, General Science',
        'subjects': ['Mathematics', 'Science'],
    },
    {
        'first_name': 'Ash',
        'last_name': 'Claro',
        'username': 'ash.claro',
        'email': 'ash.claro@mindmap.edu.ph',
        'password': 'ash123',
        'department': 'Languages',
        'specialization': 'English, Filipino',
        'subjects': ['English', 'Filipino'],
    },
    {
        'first_name': 'Wende',
        'last_name': 'Fernandez',
        'username': 'wende.fernandez',
        'email': 'wende.fernandez@mindmap.edu.ph',
        'password': 'wen123',
        'department': 'Social Sciences and Values Education',
        'specialization': 'Araling Panlipunan, Values Education',
        'subjects': ['Araling Panlipunan', 'Edukasyon sa Pagpapakatao'],
    },
]

STUDENTS = [
    ('2026-0001', 'Juan', 'Dela Cruz', 'Male', 'A'),
    ('2026-0002', 'Maria', 'Santos', 'Female', 'A'),
    ('2026-0003', 'Pedro', 'Reyes', 'Male', 'A'),
    ('2026-0004', 'Ana', 'Garcia', 'Female', 'A'),
    ('2026-0005', 'Carlos', 'Mendoza', 'Male', 'A'),
    ('2026-0006', 'Liza', 'Ramos', 'Female', 'A'),
    ('2026-0007', 'Miguel', 'Torres', 'Male', 'A'),
    ('2026-0008', 'Sofia', 'Villanueva', 'Female', 'A'),
    ('2026-0009', 'Gabriel', 'Aquino', 'Male', 'A'),
    ('2026-0010', 'Andrea', 'Bautista', 'Female', 'A'),
    ('2026-0011', 'Rafael', 'Navarro', 'Male', 'A'),
    ('2026-0012', 'Jasmine', 'Lim', 'Female', 'B'),
    ('2026-0013', 'Marco', 'Villareal', 'Male', 'B'),
    ('2026-0014', 'Bianca', 'Cruz', 'Female', 'B'),
    ('2026-0015', 'Nathaniel', 'Gomez', 'Male', 'B'),
    ('2026-0016', 'Kristine', 'Padilla', 'Female', 'B'),
    ('2026-0017', 'Joshua', 'Soriano', 'Male', 'B'),
    ('2026-0018', 'Patricia', 'Enriquez', 'Female', 'B'),
    ('2026-0019', 'Daniel', 'Mercado', 'Male', 'B'),
    ('2026-0020', 'Camille', 'Robles', 'Female', 'B'),
    ('2026-0021', 'Bryan', 'Estrada', 'Male', 'B'),
    ('2026-0022', 'Nicole', 'Salazar', 'Female', 'B'),
]

SUBJECT_NOTES = {
    'Mathematics': {
        'strengths': 'Solves linear equations and word problems accurately; shows strong number sense and neat computation.',
        'areas': 'Needs more practice with geometry proofs and multi-step problems involving fractions and decimals.',
        'improvements': 'Improved accuracy in solving equations and now checks work before submitting.',
    },
    'Science': {
        'strengths': 'Explains scientific concepts clearly and participates actively in laboratory activities.',
        'areas': 'Needs to strengthen skills in interpreting graphs and writing complete conclusions from experiments.',
        'improvements': 'Shows better understanding of the scientific method and records observations more carefully.',
    },
    'English': {
        'strengths': 'Reads with good comprehension and expresses ideas confidently during class discussions.',
        'areas': 'Needs to improve paragraph organization and subject-verb agreement in written work.',
        'improvements': 'Writing is more organized and vocabulary used in essays has become more varied.',
    },
    'Filipino': {
        'strengths': 'Nakapagpapahayag ng sariling kaisipan nang malinaw at may wastong gamit ng wika.',
        'areas': 'Kailangan pa ng pagsasanay sa pagbuo ng sanaysay at pag-unawa sa mas malalim na teksto.',
        'improvements': 'Mas maayos na ang pagkakasulat ng talata at mas aktibo sa talakayan.',
    },
    'Araling Panlipunan': {
        'strengths': 'Demonstrates strong understanding of Philippine history and analyzes current events well.',
        'areas': 'Needs to improve skills in reading maps and interpreting timelines and primary sources.',
        'improvements': 'Better recall of key historical events and more thoughtful analysis in recitation.',
    },
    'Edukasyon sa Pagpapakatao': {
        'strengths': 'Shows respect, honesty and responsibility in class and works well with classmates.',
        'areas': 'Needs to practice making decisions based on values and explaining the reasons behind them.',
        'improvements': 'More consistent in completing tasks on time and in helping groupmates.',
    },
}

ANNOUNCEMENTS = [
    {
        'title': 'First Quarter Grades are now available',
        'body': 'Students can now view their first quarter grades on their dashboard. Please review your performance and talk to your subject teacher if you need support.',
        'audience': 'all',
        'is_pinned': True,
    },
    {
        'title': 'Parent-Teacher Conference',
        'body': 'The parent-teacher conference for Grade 11 will be held on November 14, 2026 from 8:00 AM to 12:00 NN in the assigned classrooms.',
        'audience': 'students',
    },
    {
        'title': 'Grade submission reminder',
        'body': 'Teachers are reminded to encode the written work, performance task and quarterly assessment scores before the end of the week.',
        'audience': 'teachers',
    },
    {
        'title': 'Reading and Numeracy Program',
        'body': 'Students who need additional practice in reading and numeracy will join the intervention program every Tuesday and Thursday afternoon.',
        'audience': 'students',
    },
]


class Command(BaseCommand):
    help = 'Create sections, teachers, subjects, students, grades and progress data for the high school system.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.ensure_admin()
        sections = self.create_sections()
        teachers = self.create_teachers()
        subjects = self.create_subjects(teachers, sections)
        students = self.create_students(sections)
        self.create_grades(students, subjects)
        self.create_assessments(students, subjects)
        self.create_progress(students, subjects)
        self.create_announcements()
        self.cleanup_orphan_users()

        self.stdout.write(self.style.SUCCESS('High school demo data is ready.'))
        self.stdout.write('  Admin:   admin / admin123')
        for teacher in TEACHERS:
            self.stdout.write(
                f"  Teacher: {teacher['username']} / {teacher['password']}  "
                f"({teacher['first_name']} {teacher['last_name']}: "
                f"{', '.join(teacher['subjects'])})"
            )
        self.stdout.write('  Students: <student_number> / student123 (e.g. 2026-0001 / student123)')

    # ------------------------------------------------------------------ data
    def ensure_admin(self):
        admin, _ = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@mindmap.edu.ph', 'first_name': 'System', 'last_name': 'Administrator'},
        )
        admin.is_staff = True
        admin.is_superuser = True
        admin.set_password('admin123')
        admin.save()
        UserProfile.objects.update_or_create(user=admin, defaults={'role': 'admin'})

    def create_sections(self):
        a = Section.objects.update_or_create(
            code='A',
            defaults={'name': 'Section A', 'grade_level': 'Grade 11', 'room': 'Room 101', 'school_year': CURRENT_YEAR},
        )[0]
        b = Section.objects.update_or_create(
            code='B',
            defaults={'name': 'Section B', 'grade_level': 'Grade 11', 'room': 'Room 102', 'school_year': CURRENT_YEAR},
        )[0]
        return {'A': a, 'B': b}

    def create_teachers(self):
        teachers = {}
        for data in TEACHERS:
            user, _ = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                },
            )
            user.email = data['email']
            user.first_name = data['first_name']
            user.last_name = data['last_name']
            user.set_password(data['password'])
            user.save()
            UserProfile.objects.update_or_create(user=user, defaults={'role': 'teacher'})

            teacher, _ = Teacher.objects.update_or_create(
                email=data['email'],
                defaults={
                    'user': user,
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'department': data['department'],
                    'specialization': data['specialization'],
                },
            )
            teachers[data['first_name']] = teacher
        return teachers

    def create_subjects(self, teachers, sections):
        by_name = {teacher.first_name: teacher for teacher in teachers.values()}
        subjects = {}
        for code, name in SUBJECTS:
            owner_name = next(t['first_name'] for t in TEACHERS if name in t['subjects'])
            subject, _ = Subject.objects.update_or_create(
                code=code,
                defaults={
                    'name': name,
                    'teacher': by_name[owner_name],
                    'description': f'Grade 11 {name}',
                },
            )
            subject.sections.set(sections.values())
            subjects[name] = subject
        # Section advisers after teachers exist.
        sections['A'].adviser = by_name['Ayla']
        sections['A'].save()
        sections['B'].adviser = by_name['Ash']
        sections['B'].save()
        return subjects

    def create_students(self, sections):
        students = {}
        rng = random.Random(20261029)
        for index, (number, first, last, gender, section_code) in enumerate(STUDENTS):
            email = f'{first.lower()}.{last.lower().replace(" ", "")}@student.mindmap.edu.ph'
            user, _ = User.objects.get_or_create(
                username=number,
                defaults={'email': email, 'first_name': first, 'last_name': last},
            )
            user.first_name = first
            user.last_name = last
            user.email = email
            user.set_password('student123')
            user.save()
            UserProfile.objects.update_or_create(user=user, defaults={'role': 'student'})

            student, _ = Student.objects.update_or_create(
                student_number=number,
                defaults={
                    'user': user,
                    'first_name': first,
                    'last_name': last,
                    'email': email,
                    'gender': gender,
                    'birthdate': date(2009, 1 + (index % 12), 1 + (index % 27)),
                    'section': sections[section_code],
                    'grade_level': sections[section_code].grade_level,
                    'enrollment_date': date(2026, 6, 15),
                    'guardian_name': f'{last} Family',
                    'guardian_contact': f'0917{7000000 + index}',
                    'address': f'{index + 1} Mabini Street, Barangay San Roque',
                },
            )
            students[number] = student
        return students

    def create_grades(self, students, subjects):
        rng = random.Random(77)
        for number, student in students.items():
            for name, subject in subjects.items():
                ability = rng.randint(72, 94)
                for year, quarter_dates in (
                    (PREVIOUS_YEAR, (1, 2, 3, 4)),
                    (CURRENT_YEAR, (1,)),
                ):
                    for quarter in quarter_dates:
                        trend = 0 if year == PREVIOUS_YEAR else 1.5
                        base = ability + trend + (quarter - 1) * 1.2
                        ww = min(100, max(60, base + rng.uniform(-4, 6)))
                        pt = min(100, max(60, base + rng.uniform(-3, 5)))
                        qa = min(100, max(60, base + rng.uniform(-6, 4)))
                        Grade.objects.update_or_create(
                            student=student,
                            subject=subject,
                            quarter=quarter,
                            school_year=year,
                            defaults={
                                'written_work': Decimal(f'{ww:.2f}'),
                                'performance_task': Decimal(f'{pt:.2f}'),
                                'quarterly_assessment': Decimal(f'{qa:.2f}'),
                                'recorded_by': subject.teacher,
                            },
                        )

    def create_assessments(self, students, subjects):
        rng = random.Random(1234)
        for number, student in students.items():
            for name, subject in subjects.items():
                max_score = 30
                score = rng.randint(20, 30)
                LearningAssessment.objects.update_or_create(
                    student=student,
                    subject=subject,
                    title=f'{name} Quiz 1',
                    defaults={
                        'teacher': subject.teacher,
                        'assessment_date': date(2026, 8, 20),
                        'assessment_type': 'Quiz',
                        'quarter': 1,
                        'score': Decimal(score),
                        'max_score': Decimal(max_score),
                        'notes': 'First quarter diagnostic quiz.',
                    },
                )
                project_score = rng.randint(28, 40)
                LearningAssessment.objects.update_or_create(
                    student=student,
                    subject=subject,
                    title=f'{name} Performance Task 1',
                    defaults={
                        'teacher': subject.teacher,
                        'assessment_date': date(2026, 9, 18),
                        'assessment_type': 'Performance Task',
                        'quarter': 1,
                        'score': Decimal(project_score),
                        'max_score': Decimal(40),
                        'notes': 'Individual performance task for the first quarter.',
                    },
                )

    def create_progress(self, students, subjects):
        rng = random.Random(555)
        for number, student in students.items():
            for name, subject in subjects.items():
                notes = SUBJECT_NOTES[name]
                latest = student.grades.filter(subject=subject).order_by('-school_year', '-quarter').first()
                previous = student.grades.filter(subject=subject).order_by('-school_year', '-quarter')[1:2].first()
                change = Decimal('0')
                if latest and previous and latest.final_grade and previous.final_grade:
                    change = latest.final_grade - previous.final_grade
                direction = 'increased' if change >= 0 else 'moved'
                improvement = (
                    f'{notes["improvements"]} The quarter grade {direction} by '
                    f'{abs(change):.2f} points compared with the previous quarter.'
                )
                status = 'Improving'
                grade = latest.final_grade if latest and latest.final_grade else Decimal('0')
                if grade >= 90:
                    status = 'Excellent'
                elif grade < 75:
                    status = 'At Risk'
                elif change <= 0:
                    status = 'Stable'
                AcademicProgress.objects.update_or_create(
                    student=student,
                    subject=subject,
                    record_date=date(2026, 10, 10 + (rng.randint(0, 12))),
                    defaults={
                        'teacher': subject.teacher,
                        'strengths': notes['strengths'],
                        'areas_for_improvement': notes['areas'],
                        'recent_improvements': improvement,
                        'status': status,
                    },
                )

    def create_announcements(self):
        admin = User.objects.filter(username='admin').first()
        for data in ANNOUNCEMENTS:
            Announcement.objects.update_or_create(
                title=data['title'],
                defaults={
                    'body': data['body'],
                    'audience': data['audience'],
                    'is_pinned': data.get('is_pinned', False),
                    'created_by': admin,
                },
            )

    def cleanup_orphan_users(self):
        """Remove legacy accounts that no longer belong to a student or teacher."""
        for user in User.objects.filter(is_superuser=False):
            role = getattr(getattr(user, 'profile', None), 'role', None)
            if role == 'student' and not hasattr(user, 'student_profile'):
                user.delete()
            elif role == 'teacher' and not hasattr(user, 'teacher_profile'):
                user.delete()
