"""Views for the high school academic monitoring system.

Every teacher view resolves the signed-in user's own Teacher record and scopes
all subject/student queries through ``apps.users.access``. Object-level checks
raise 404 when a record belongs to another teacher, so permissions cannot be
bypassed by editing URLs or form fields.
"""

from datetime import date
from decimal import Decimal, InvalidOperation
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.core.models import UserProfile

from .access import (
    get_teacher,
    student_for_user,
    teacher_assessment_or_404,
    teacher_progress_or_404,
    teacher_sections,
    teacher_student_or_404,
    teacher_students,
    teacher_subject_or_404,
    teacher_subjects,
    visible_announcements,
)
from .analytics import (
    CURRENT_SCHOOL_YEAR,
    assessment_rows,
    overall_average,
    percent_of,
    progress_groups,
    student_snapshot,
    subject_summary,
)
from .models import (
    QUARTER_CHOICES,
    AcademicProgress,
    Announcement,
    Grade,
    LearningAssessment,
    Section,
    Student,
    Subject,
    Teacher,
)


def role_required(role):
    """Require an authenticated user with the given profile role."""

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            try:
                profile = request.user.profile
            except UserProfile.DoesNotExist:
                messages.error(request, 'User profile not found.')
                return redirect('login')
            if profile.role != role:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def _current_teacher(request):
    teacher = get_teacher(request.user)
    if teacher is None:
        messages.error(request, 'No teacher profile is linked to this account.')
        return None
    return teacher


def _decimal_or_none(raw, label, errors):
    raw = (raw or '').strip()
    if raw == '':
        return None
    try:
        value = Decimal(raw)
    except InvalidOperation:
        errors.append(f'{label} must be a number.')
        return None
    if value < 0 or value > 100:
        errors.append(f'{label} must be between 0 and 100.')
        return None
    return value.quantize(Decimal('0.01'))


def _student_or_none(request):
    student = student_for_user(request.user)
    if student is None:
        messages.error(request, 'No student record is linked to this account.')
    return student


def _client_ip(request):
    return request.META.get('REMOTE_ADDR', '')


# ==================== ADMIN VIEWS ====================

@login_required
@role_required('admin')
def admin_dashboard(request):
    sections = Section.objects.select_related('adviser').all()
    section_rows = [
        {
            'section': section,
            'count': section.students.count(),
            'average': section.students.aggregate(value=Avg('grades__final_grade'))['value'],
        }
        for section in sections
    ]
    context = {
        'total_students': Student.objects.count(),
        'total_teachers': Teacher.objects.count(),
        'total_subjects': Subject.objects.count(),
        'total_grades': Grade.objects.count(),
        'total_assessments': LearningAssessment.objects.count(),
        'total_progress': AcademicProgress.objects.count(),
        'section_rows': section_rows,
        'teacher_rows': Teacher.objects.prefetch_related('subjects').all(),
        'announcements': Announcement.objects.all()[:5],
        'recent_students': Student.objects.select_related('section').order_by('-created_at')[:5],
        'current_year': CURRENT_SCHOOL_YEAR,
    }
    return render(request, 'users/admin/dashboard.html', context)


@login_required
@role_required('admin')
def admin_students(request):
    search_query = request.GET.get('search', '').strip()
    section_filter = request.GET.get('section', '')
    students = Student.objects.select_related('section').all()
    if search_query:
        students = students.filter(
            Q(student_number__icontains=search_query)
            | Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
        )
    if section_filter:
        students = students.filter(section_id=section_filter)

    rows = []
    for student in students.order_by('section__name', 'last_name', 'first_name'):
        rows.append({
            'student': student,
            'average': student.average_grade(CURRENT_SCHOOL_YEAR),
            'label': student.performance_label(),
            'percent': percent_of(student.average_grade(CURRENT_SCHOOL_YEAR)),
        })

    context = {
        'rows': rows,
        'sections': Section.objects.all(),
        'search_query': search_query,
        'section_filter': section_filter,
    }
    return render(request, 'users/admin/students.html', context)


@login_required
@role_required('admin')
def admin_student_create(request):
    if request.method == 'POST':
        number = request.POST.get('student_number', '').strip()
        if not number:
            messages.error(request, 'Student ID is required.')
        elif Student.objects.filter(student_number=number).exists():
            messages.error(request, f'A student with ID {number} already exists.')
        elif User.objects.filter(username=number).exists():
            messages.error(request, f'Username {number} is already taken.')
        else:
            section = get_object_or_404(Section, pk=request.POST.get('section'))
            password = request.POST.get('password') or 'student123'
            user = User.objects.create_user(
                username=number,
                email=request.POST.get('email') or '',
                password=password,
                first_name=request.POST.get('first_name', ''),
                last_name=request.POST.get('last_name', ''),
            )
            UserProfile.objects.create(user=user, role='student')
            Student.objects.create(
                user=user,
                student_number=number,
                first_name=request.POST.get('first_name', ''),
                last_name=request.POST.get('last_name', ''),
                email=request.POST.get('email') or None,
                gender=request.POST.get('gender') or None,
                birthdate=request.POST.get('birthdate') or None,
                section=section,
                enrollment_date=request.POST.get('enrollment_date') or date.today(),
                guardian_name=request.POST.get('guardian_name') or None,
                guardian_contact=request.POST.get('guardian_contact') or None,
                address=request.POST.get('address') or None,
            )
            messages.success(
                request,
                f'Student {number} created. Login: {number} / {password}',
            )
            return redirect('admin_students')

    return render(request, 'users/admin/student_form.html', {
        'sections': Section.objects.all(),
        'today': date.today(),
    })


@login_required
@role_required('admin')
def admin_student_edit(request, student_id):
    student = get_object_or_404(Student.objects.select_related('section'), pk=student_id)
    if request.method == 'POST':
        section = get_object_or_404(Section, pk=request.POST.get('section'))
        student.first_name = request.POST.get('first_name', '')
        student.last_name = request.POST.get('last_name', '')
        student.email = request.POST.get('email') or None
        student.gender = request.POST.get('gender') or None
        student.birthdate = request.POST.get('birthdate') or None
        student.section = section
        student.grade_level = section.grade_level
        student.enrollment_date = request.POST.get('enrollment_date') or None
        student.phone = request.POST.get('phone') or None
        student.address = request.POST.get('address') or None
        student.guardian_name = request.POST.get('guardian_name') or None
        student.guardian_contact = request.POST.get('guardian_contact') or None
        if 'profile_picture' in request.FILES:
            student.profile_picture = request.FILES['profile_picture']
        student.save()

        if student.user:
            student.user.first_name = student.first_name
            student.user.last_name = student.last_name
            student.user.email = student.email or ''
            new_password = request.POST.get('password', '').strip()
            if new_password:
                student.user.set_password(new_password)
            student.user.save()

        messages.success(request, f'Student {student.get_full_name()} updated.')
        return redirect('admin_students')

    return render(request, 'users/admin/student_form.html', {
        'student': student,
        'sections': Section.objects.all(),
        'today': date.today(),
    })


@login_required
@role_required('admin')
def admin_student_delete(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    if request.method == 'POST':
        name = student.get_full_name()
        user = student.user
        student.delete()
        if user:
            user.delete()
        messages.success(request, f'Student {name} deleted.')
    return redirect('admin_students')


@login_required
@role_required('admin')
def admin_teachers(request):
    teachers = Teacher.objects.prefetch_related('subjects').all()
    return render(request, 'users/admin/teachers.html', {'teachers': teachers})


@login_required
@role_required('admin')
def admin_teacher_create(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        email = request.POST.get('email', '').strip()
        if not username or not password:
            messages.error(request, 'Username and password are required.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, f'Username {username} is already taken.')
        elif Teacher.objects.filter(email=email).exists():
            messages.error(request, 'That email is already used by another teacher.')
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=request.POST.get('first_name', ''),
                last_name=request.POST.get('last_name', ''),
            )
            UserProfile.objects.create(user=user, role='teacher')
            Teacher.objects.create(
                user=user,
                first_name=request.POST.get('first_name', ''),
                last_name=request.POST.get('last_name', ''),
                email=email,
                department=request.POST.get('department') or None,
                specialization=request.POST.get('specialization') or None,
            )
            messages.success(request, f'Teacher {username} created.')
            return redirect('admin_teachers')

    return render(request, 'users/admin/teacher_form.html', {
        'suggested_username': '',
    })


@login_required
@role_required('admin')
def admin_teacher_edit(request, teacher_id):
    teacher = get_object_or_404(Teacher, pk=teacher_id)
    if request.method == 'POST':
        teacher.first_name = request.POST.get('first_name', '')
        teacher.last_name = request.POST.get('last_name', '')
        teacher.email = request.POST.get('email', '')
        teacher.department = request.POST.get('department') or None
        teacher.specialization = request.POST.get('specialization') or None
        teacher.qualification = request.POST.get('qualification') or None
        teacher.phone = request.POST.get('phone') or None
        if 'profile_picture' in request.FILES:
            teacher.profile_picture = request.FILES['profile_picture']
        teacher.save()

        if teacher.user:
            teacher.user.first_name = teacher.first_name
            teacher.user.last_name = teacher.last_name
            teacher.user.email = teacher.email
            new_password = request.POST.get('password', '').strip()
            if new_password:
                teacher.user.set_password(new_password)
            teacher.user.save()

        messages.success(request, f'Teacher {teacher.get_full_name()} updated.')
        return redirect('admin_teachers')

    return render(request, 'users/admin/teacher_form.html', {'teacher': teacher})


@login_required
@role_required('admin')
def admin_teacher_delete(request, teacher_id):
    teacher = get_object_or_404(Teacher, pk=teacher_id)
    if request.method == 'POST':
        name = teacher.get_full_name()
        user = teacher.user
        if teacher.subjects.exists():
            messages.error(
                request,
                f'{name} still handles {teacher.subjects.count()} subject(s). '
                'Reassign the subjects first.',
            )
            return redirect('admin_teachers')
        teacher.delete()
        if user:
            user.delete()
        messages.success(request, f'Teacher {name} deleted.')
    return redirect('admin_teachers')


@login_required
@role_required('admin')
def admin_subjects(request):
    subjects = Subject.objects.select_related('teacher').prefetch_related('sections').order_by('name')
    return render(request, 'users/admin/subjects.html', {'subjects': subjects})


@login_required
@role_required('admin')
def admin_subject_create(request):
    if request.method == 'POST':
        code = request.POST.get('code', '').strip().upper()
        if Subject.objects.filter(code=code).exists():
            messages.error(request, f'Subject code {code} already exists.')
        else:
            teacher = Teacher.objects.filter(pk=request.POST.get('teacher')).first()
            subject = Subject.objects.create(
                code=code,
                name=request.POST.get('name', '').strip(),
                description=request.POST.get('description') or None,
                teacher=teacher,
            )
            subject.sections.set(request.POST.getlist('sections'))
            messages.success(request, f'Subject {subject.name} created.')
            return redirect('admin_subjects')

    return render(request, 'users/admin/subject_form.html', {
        'teachers': Teacher.objects.all(),
        'sections': Section.objects.all(),
    })


@login_required
@role_required('admin')
def admin_subject_edit(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)
    if request.method == 'POST':
        subject.code = request.POST.get('code', '').strip().upper()
        subject.name = request.POST.get('name', '').strip()
        subject.description = request.POST.get('description') or None
        subject.teacher = Teacher.objects.filter(pk=request.POST.get('teacher')).first()
        subject.save()
        subject.sections.set(request.POST.getlist('sections'))
        messages.success(request, f'Subject {subject.name} updated.')
        return redirect('admin_subjects')

    return render(request, 'users/admin/subject_form.html', {
        'subject': subject,
        'teachers': Teacher.objects.all(),
        'sections': Section.objects.all(),
        'assigned_section_ids': list(subject.sections.values_list('pk', flat=True)),
    })


@login_required
@role_required('admin')
def admin_subject_delete(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)
    if request.method == 'POST':
        name = subject.name
        subject.delete()
        messages.success(request, f'Subject {name} deleted.')
    return redirect('admin_subjects')


@login_required
@role_required('admin')
def admin_sections(request):
    sections = Section.objects.select_related('adviser').prefetch_related('subjects').all()
    rows = [
        {
            'section': section,
            'count': section.students.count(),
            'subjects': section.subjects.count(),
        }
        for section in sections
    ]
    return render(request, 'users/admin/sections.html', {'rows': rows})


@login_required
@role_required('admin')
def admin_section_create(request):
    if request.method == 'POST':
        section = Section(
            name=request.POST.get('name', '').strip(),
            code=request.POST.get('code', '').strip().upper(),
            grade_level=request.POST.get('grade_level', 'Grade 11'),
            room=request.POST.get('room') or None,
            school_year=request.POST.get('school_year') or CURRENT_SCHOOL_YEAR,
            adviser=Teacher.objects.filter(pk=request.POST.get('adviser')).first(),
        )
        if Section.objects.filter(Q(name=section.name) | Q(code=section.code)).exists():
            messages.error(request, 'A section with that name or code already exists.')
        else:
            section.save()
            messages.success(request, f'{section.name} created.')
            return redirect('admin_sections')

    return render(request, 'users/admin/section_form.html', {
        'teachers': Teacher.objects.all(),
        'grade_levels': ['Grade 7', 'Grade 8', 'Grade 9', 'Grade 10', 'Grade 11', 'Grade 12'],
    })


@login_required
@role_required('admin')
def admin_section_edit(request, section_id):
    section = get_object_or_404(Section, pk=section_id)
    if request.method == 'POST':
        section.name = request.POST.get('name', '').strip()
        section.code = request.POST.get('code', '').strip().upper()
        section.grade_level = request.POST.get('grade_level', section.grade_level)
        section.room = request.POST.get('room') or None
        section.school_year = request.POST.get('school_year') or section.school_year
        section.adviser = Teacher.objects.filter(pk=request.POST.get('adviser')).first()
        section.save()
        section.students.update(grade_level=section.grade_level)
        messages.success(request, f'{section.name} updated.')
        return redirect('admin_sections')

    return render(request, 'users/admin/section_form.html', {
        'section': section,
        'teachers': Teacher.objects.all(),
        'grade_levels': ['Grade 7', 'Grade 8', 'Grade 9', 'Grade 10', 'Grade 11', 'Grade 12'],
    })


@login_required
@role_required('admin')
def admin_section_delete(request, section_id):
    section = get_object_or_404(Section, pk=section_id)
    if request.method == 'POST':
        if section.students.exists():
            messages.error(request, 'Move the students to another section before deleting this one.')
        else:
            name = section.name
            section.delete()
            messages.success(request, f'{name} deleted.')
    return redirect('admin_sections')


@login_required
@role_required('admin')
def admin_announcements(request):
    return render(request, 'users/admin/announcements.html', {
        'announcements': Announcement.objects.select_related('created_by').all(),
    })


@login_required
@role_required('admin')
def admin_announcement_create(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        body = request.POST.get('body', '').strip()
        if not title or not body:
            messages.error(request, 'Title and message are required.')
        else:
            Announcement.objects.create(
                title=title,
                body=body,
                audience=request.POST.get('audience', 'all'),
                is_pinned=bool(request.POST.get('is_pinned')),
                created_by=request.user,
            )
            messages.success(request, 'Announcement posted.')
    return redirect('admin_announcements')


@login_required
@role_required('admin')
def admin_announcement_delete(request, announcement_id):
    announcement = get_object_or_404(Announcement, pk=announcement_id)
    if request.method == 'POST':
        announcement.delete()
        messages.success(request, 'Announcement deleted.')
    return redirect('admin_announcements')


@login_required
@role_required('admin')
def admin_teacher_assignments(request):
    """Overview of which teacher handles which subject and sections."""
    rows = []
    for teacher in Teacher.objects.prefetch_related('subjects__sections').all():
        rows.append({
            'teacher': teacher,
            'subjects': teacher.subjects.all(),
            'students': teacher.assigned_students().count(),
        })
    return render(request, 'users/admin/assignments.html', {'rows': rows})


# ==================== TEACHER VIEWS ====================

@login_required
@role_required('teacher')
def teacher_dashboard(request):
    teacher = _current_teacher(request)
    if teacher is None:
        return redirect('dashboard')

    subjects = teacher_subjects(teacher)
    subject_rows = []
    for subject in subjects:
        grades = Grade.objects.filter(
            subject=subject, school_year=CURRENT_SCHOOL_YEAR,
        )
        subject_rows.append({
            'subject': subject,
            'sections': subject.sections.all(),
            'graded': grades.exclude(final_grade__isnull=True).count(),
            'average': grades.aggregate(value=Avg('final_grade'))['value'],
            'progress_count': subject.progress_records.count(),
        })

    students = teacher_students(teacher)
    context = {
        'teacher': teacher,
        'subjects': subjects,
        'subject_rows': subject_rows,
        'student_count': students.count(),
        'grade_count': Grade.objects.filter(subject__teacher=teacher).count(),
        'assessment_count': LearningAssessment.objects.filter(subject__teacher=teacher).count(),
        'progress_count': AcademicProgress.objects.filter(subject__teacher=teacher).count(),
        'recent_grades': Grade.objects.filter(subject__teacher=teacher)
        .select_related('student', 'subject')
        .order_by('-updated_at')[:6],
        'recent_progress': AcademicProgress.objects.filter(subject__teacher=teacher)
        .select_related('student', 'subject')
        .order_by('-updated_at')[:5],
        'sections': teacher_sections(teacher),
        'current_year': CURRENT_SCHOOL_YEAR,
        'announcements': visible_announcements(request.user)[:3],
    }
    return render(request, 'users/teacher/dashboard.html', context)


@login_required
@role_required('teacher')
def teacher_students_view(request):
    teacher = _current_teacher(request)
    if teacher is None:
        return redirect('dashboard')

    search_query = request.GET.get('search', '').strip()
    section_filter = request.GET.get('section', '')
    students = teacher_students(teacher)
    if search_query:
        students = students.filter(
            Q(student_number__icontains=search_query)
            | Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
        )
    if section_filter:
        students = students.filter(section_id=section_filter)

    subjects = teacher_subjects(teacher)
    rows = []
    for student in students:
        subject_rows = subject_summary(student, subjects=subjects)
        rows.append({
            'student': student,
            'average': overall_average(subject_rows),
            'rows': subject_rows,
        })

    context = {
        'teacher': teacher,
        'rows': rows,
        'subjects': subjects,
        'sections': teacher_sections(teacher),
        'search_query': search_query,
        'section_filter': section_filter,
    }
    return render(request, 'users/teacher/students.html', context)


@login_required
@role_required('teacher')
def teacher_student_detail(request, student_id):
    teacher = _current_teacher(request)
    if teacher is None:
        return redirect('dashboard')

    student = teacher_student_or_404(teacher, student_id)
    subjects = teacher_subjects(teacher)
    rows = subject_summary(student, subjects=subjects)
    context = {
        'teacher': teacher,
        'student': student,
        'rows': rows,
        'average': overall_average(rows),
        'progress_records': AcademicProgress.objects.filter(
            student=student, subject__teacher=teacher,
        ).select_related('subject'),
        'assessments': assessment_rows(student, subjects),
        'subjects': subjects,
    }
    return render(request, 'users/teacher/student_detail.html', context)


@login_required
@role_required('teacher')
def teacher_gradebook(request):
    teacher = _current_teacher(request)
    if teacher is None:
        return redirect('dashboard')

    subjects = teacher_subjects(teacher)
    sections = teacher_sections(teacher)

    subject = None
    subject_id = request.POST.get('subject') or request.GET.get('subject')
    if subject_id:
        subject = teacher_subject_or_404(teacher, subject_id)
    elif subjects.exists():
        subject = subjects.first()

    if subject is None:
        messages.error(request, 'You have no assigned subject yet.')
        return redirect('teacher_dashboard')

    section = None
    section_id = request.POST.get('section') or request.GET.get('section')
    if section_id:
        section = get_object_or_404(subject.sections.all(), pk=section_id)
    else:
        section = subject.sections.first()

    quarter = int(request.POST.get('quarter') or request.GET.get('quarter') or 1)
    if quarter not in [value for value, _ in QUARTER_CHOICES]:
        quarter = 1
    school_year = request.POST.get('school_year') or request.GET.get('school_year') or CURRENT_SCHOOL_YEAR

    students = teacher_students(teacher).filter(section=section) if section else teacher_students(teacher).none()

    if request.method == 'POST':
        errors = []
        pending = []
        for student in students:
            keys = [f'ww_{student.pk}', f'pt_{student.pk}', f'qa_{student.pk}']
            if not any(key in request.POST for key in keys):
                continue
            written_work = _decimal_or_none(request.POST.get(f'ww_{student.pk}'), f'{student.get_full_name()} written work', errors)
            performance_task = _decimal_or_none(request.POST.get(f'pt_{student.pk}'), f'{student.get_full_name()} performance task', errors)
            quarterly_assessment = _decimal_or_none(request.POST.get(f'qa_{student.pk}'), f'{student.get_full_name()} quarterly assessment', errors)
            pending.append((student, written_work, performance_task, quarterly_assessment))

        if errors:
            for error in errors[:5]:
                messages.error(request, error)
        else:
            for student, written_work, performance_task, quarterly_assessment in pending:
                Grade.objects.update_or_create(
                    student=student,
                    subject=subject,
                    quarter=quarter,
                    school_year=school_year,
                    defaults={
                        'written_work': written_work,
                        'performance_task': performance_task,
                        'quarterly_assessment': quarterly_assessment,
                        'recorded_by': teacher,
                    },
                )
            messages.success(request, f'Grades saved for {subject.name} - {section.name} (Quarter {quarter}).')
        return redirect(
            f"{request.path}?subject={subject.pk}&section={section.pk if section else ''}"
            f'&quarter={quarter}&school_year={school_year}'
        )

    existing = {
        grade.student_id: grade
        for grade in Grade.objects.filter(
            subject=subject,
            quarter=quarter,
            school_year=school_year,
            student__in=students,
        )
    }
    rows = [{'student': student, 'grade': existing.get(student.pk)} for student in students]

    context = {
        'teacher': teacher,
        'subjects': subjects,
        'subject': subject,
        'sections': subject.sections.all(),
        'section': section,
        'quarter': quarter,
        'quarters': QUARTER_CHOICES,
        'school_year': school_year,
        'rows': rows,
        'current_year': CURRENT_SCHOOL_YEAR,
    }
    return render(request, 'users/teacher/gradebook.html', context)


@login_required
@role_required('teacher')
def teacher_grades(request):
    teacher = _current_teacher(request)
    if teacher is None:
        return redirect('dashboard')

    subjects = teacher_subjects(teacher)
    subject_filter = request.GET.get('subject', '')
    quarter_filter = request.GET.get('quarter', '')
    search_query = request.GET.get('search', '').strip()

    grades = Grade.objects.filter(subject__teacher=teacher).select_related('student', 'subject')
    if subject_filter:
        grades = grades.filter(subject_id=subject_filter)
    if quarter_filter:
        grades = grades.filter(quarter=quarter_filter)
    if search_query:
        grades = grades.filter(
            Q(student__student_number__icontains=search_query)
            | Q(student__first_name__icontains=search_query)
            | Q(student__last_name__icontains=search_query)
        )

    context = {
        'teacher': teacher,
        'grades': grades.order_by('subject__name', 'student__last_name', 'quarter'),
        'subjects': subjects,
        'subject_filter': subject_filter,
        'quarter_filter': quarter_filter,
        'search_query': search_query,
        'quarters': QUARTER_CHOICES,
    }
    return render(request, 'users/teacher/grades.html', context)


@login_required
@role_required('teacher')
def teacher_assessments(request):
    teacher = _current_teacher(request)
    if teacher is None:
        return redirect('dashboard')

    subjects = teacher_subjects(teacher)
    subject_filter = request.GET.get('subject', '')
    search_query = request.GET.get('search', '').strip()

    assessments = LearningAssessment.objects.filter(subject__teacher=teacher).select_related('student', 'subject')
    if subject_filter:
        assessments = assessments.filter(subject_id=subject_filter)
    if search_query:
        assessments = assessments.filter(
            Q(student__student_number__icontains=search_query)
            | Q(student__first_name__icontains=search_query)
            | Q(student__last_name__icontains=search_query)
        )

    rows = []
    for assessment in assessments.order_by('-assessment_date', '-pk'):
        percentage = assessment.get_percentage()
        rows.append({
            'assessment': assessment,
            'percent': percent_of(percentage),
            'percentage': percentage,
        })

    return render(request, 'users/teacher/assessments.html', {
        'teacher': teacher,
        'rows': rows,
        'subjects': subjects,
        'subject_filter': subject_filter,
        'search_query': search_query,
    })


@login_required
@role_required('teacher')
def teacher_assessment_create(request):
    teacher = _current_teacher(request)
    if teacher is None:
        return redirect('dashboard')

    if request.method == 'POST':
        subject = teacher_subject_or_404(teacher, request.POST.get('subject'))
        student = teacher_student_or_404(teacher, request.POST.get('student'))
        LearningAssessment.objects.create(
            student=student,
            subject=subject,
            teacher=teacher,
            assessment_date=request.POST.get('assessment_date') or date.today(),
            title=request.POST.get('title', '').strip(),
            assessment_type=request.POST.get('assessment_type', 'Quiz'),
            quarter=request.POST.get('quarter') or 1,
            score=request.POST.get('score') or None,
            max_score=request.POST.get('max_score') or None,
            notes=request.POST.get('notes') or None,
        )
        messages.success(request, 'Assessment recorded.')
        return redirect('teacher_assessments')

    return render(request, 'users/teacher/assessment_form.html', {
        'teacher': teacher,
        'subjects': teacher_subjects(teacher),
        'students': teacher_students(teacher),
        'quarters': QUARTER_CHOICES,
        'type_choices': LearningAssessment.ASSESSMENT_TYPES,
        'today': date.today(),
    })


@login_required
@role_required('teacher')
def teacher_assessment_edit(request, assessment_id):
    teacher = _current_teacher(request)
    if teacher is None:
        return redirect('dashboard')

    assessment = teacher_assessment_or_404(teacher, assessment_id)
    if request.method == 'POST':
        subject = teacher_subject_or_404(teacher, request.POST.get('subject'))
        student = teacher_student_or_404(teacher, request.POST.get('student'))
        assessment.student = student
        assessment.subject = subject
        assessment.assessment_date = request.POST.get('assessment_date') or assessment.assessment_date
        assessment.title = request.POST.get('title', '').strip()
        assessment.assessment_type = request.POST.get('assessment_type', assessment.assessment_type)
        assessment.quarter = request.POST.get('quarter') or assessment.quarter
        assessment.score = request.POST.get('score') or None
        assessment.max_score = request.POST.get('max_score') or None
        assessment.notes = request.POST.get('notes') or None
        assessment.teacher = teacher
        assessment.save()
        messages.success(request, 'Assessment updated.')
        return redirect('teacher_assessments')

    return render(request, 'users/teacher/assessment_form.html', {
        'teacher': teacher,
        'assessment': assessment,
        'subjects': teacher_subjects(teacher),
        'students': teacher_students(teacher),
        'quarters': QUARTER_CHOICES,
        'type_choices': LearningAssessment.ASSESSMENT_TYPES,
        'today': date.today(),
    })


@login_required
@role_required('teacher')
def teacher_progress(request):
    teacher = _current_teacher(request)
    if teacher is None:
        return redirect('dashboard')

    subjects = teacher_subjects(teacher)
    subject_filter = request.GET.get('subject', '')
    search_query = request.GET.get('search', '').strip()

    records = AcademicProgress.objects.filter(subject__teacher=teacher).select_related('student', 'subject')
    if subject_filter:
        records = records.filter(subject_id=subject_filter)
    if search_query:
        records = records.filter(
            Q(student__student_number__icontains=search_query)
            | Q(student__first_name__icontains=search_query)
            | Q(student__last_name__icontains=search_query)
        )

    return render(request, 'users/teacher/progress.html', {
        'teacher': teacher,
        'records': records.order_by('-record_date', '-pk'),
        'subjects': subjects,
        'subject_filter': subject_filter,
        'search_query': search_query,
    })


@login_required
@role_required('teacher')
def teacher_progress_create(request):
    teacher = _current_teacher(request)
    if teacher is None:
        return redirect('dashboard')

    student_id = request.GET.get('student')
    subject_id = request.GET.get('subject')

    if request.method == 'POST':
        subject = teacher_subject_or_404(teacher, request.POST.get('subject'))
        student = teacher_student_or_404(teacher, request.POST.get('student'))
        if not student.section_id or not subject.sections.filter(pk=student.section_id).exists():
            messages.error(request, 'That student is not enrolled in this subject.')
            return redirect('teacher_progress')

        strengths = request.POST.get('strengths', '').strip()
        areas = request.POST.get('areas_for_improvement', '').strip()
        improvements = request.POST.get('recent_improvements', '').strip()
        if not strengths or not areas or not improvements:
            messages.error(request, 'Strengths, areas for improvement and recent improvements are all required.')
        else:
            record = AcademicProgress.objects.create(
                student=student,
                subject=subject,
                teacher=teacher,
                record_date=request.POST.get('record_date') or date.today(),
                strengths=strengths,
                areas_for_improvement=areas,
                recent_improvements=improvements,
                status=request.POST.get('status', 'Improving'),
            )
            messages.success(
                request,
                f'Progress record for {student.get_full_name()} saved and now visible on the student dashboard.',
            )
            return redirect('teacher_student_detail', student_id=record.student.pk)

    return render(request, 'users/teacher/progress_form.html', {
        'teacher': teacher,
        'subjects': teacher_subjects(teacher),
        'students': teacher_students(teacher),
        'selected_student': Student.objects.filter(pk=student_id).first(),
        'selected_subject': Subject.objects.filter(pk=subject_id, teacher=teacher).first(),
        'statuses': AcademicProgress.STATUS_CHOICES,
        'today': date.today(),
    })


@login_required
@role_required('teacher')
def teacher_progress_edit(request, progress_id):
    teacher = _current_teacher(request)
    if teacher is None:
        return redirect('dashboard')

    record = teacher_progress_or_404(teacher, progress_id)

    if request.method == 'POST':
        subject = teacher_subject_or_404(teacher, request.POST.get('subject'))
        student = teacher_student_or_404(teacher, request.POST.get('student'))
        record.subject = subject
        record.student = student
        record.teacher = teacher
        record.record_date = request.POST.get('record_date') or record.record_date
        record.strengths = request.POST.get('strengths', '').strip()
        record.areas_for_improvement = request.POST.get('areas_for_improvement', '').strip()
        record.recent_improvements = request.POST.get('recent_improvements', '').strip()
        record.status = request.POST.get('status', record.status)
        record.save()
        messages.success(request, 'Progress record updated on the student dashboard.')
        return redirect('teacher_student_detail', student_id=record.student.pk)

    return render(request, 'users/teacher/progress_form.html', {
        'teacher': teacher,
        'record': record,
        'subjects': teacher_subjects(teacher),
        'students': teacher_students(teacher),
        'selected_subject': record.subject,
        'selected_student': record.student,
        'statuses': AcademicProgress.STATUS_CHOICES,
        'today': date.today(),
    })


# ==================== STUDENT VIEWS ====================

@login_required
@role_required('student')
def student_dashboard(request):
    student = _student_or_none(request)
    if student is None:
        return redirect('dashboard')

    snapshot = student_snapshot(student)
    context = {
        'student': student,
        **snapshot,
        'announcements': visible_announcements(request.user)[:4],
        'current_year': CURRENT_SCHOOL_YEAR,
        'today': date.today(),
    }
    return render(request, 'users/student/dashboard.html', context)


@login_required
@role_required('student')
def student_grades(request):
    student = _student_or_none(request)
    if student is None:
        return redirect('dashboard')

    years_list = list(
        Grade.objects.filter(student=student).values_list('school_year', flat=True).distinct().order_by('-school_year')
    )
    school_year = request.GET.get('year') or (years_list[0] if years_list else CURRENT_SCHOOL_YEAR)
    if school_year not in years_list:
        school_year = years_list[0] if years_list else CURRENT_SCHOOL_YEAR
    rows = subject_summary(student, school_year=school_year)
    grade_records = Grade.objects.filter(student=student, school_year=school_year).select_related(
        'subject', 'recorded_by'
    ).order_by('subject__name', 'quarter')

    return render(request, 'users/student/grades.html', {
        'student': student,
        'rows': rows,
        'average': overall_average(rows),
        'graded_count': len([row for row in rows if row['latest'] is not None]),
        'school_year': school_year,
        'years': years_list,
        'quarters': QUARTER_CHOICES,
        'grade_records': grade_records,
    })


@login_required
@role_required('student')
def student_assessments(request):
    student = _student_or_none(request)
    if student is None:
        return redirect('dashboard')

    subject_filter = request.GET.get('subject', '')
    subjects = teacher_subjects_for_student(student)
    rows = assessment_rows(student, subjects if subject_filter else None)
    if subject_filter:
        rows = [row for row in rows if str(row['assessment'].subject_id) == str(subject_filter)]

    return render(request, 'users/student/assessments.html', {
        'student': student,
        'rows': rows,
        'subjects': subjects,
        'subject_filter': subject_filter,
    })


@login_required
@role_required('student')
def student_progress(request):
    student = _student_or_none(request)
    if student is None:
        return redirect('dashboard')

    groups = progress_groups(student)
    history = AcademicProgress.objects.filter(student=student).select_related('subject', 'teacher')
    return render(request, 'users/student/progress.html', {
        'student': student,
        'groups': groups,
        'history': history.order_by('-record_date', '-pk'),
    })


def teacher_subjects_for_student(student):
    """Subjects offered in the student's section (read-only, for filters)."""
    return Subject.objects.filter(sections=student.section).order_by('name')
