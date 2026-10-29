from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count, Q
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from apps.core.models import UserProfile
from apps.users.models import (
    Student, Teacher, Subject, Grade, 
    LearningAssessment, AcademicProgress
)


def role_required(role):
    """Decorator to check user role"""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            try:
                if request.user.profile.role != role:
                    messages.error(request, 'You do not have permission to access this page.')
                    return redirect('dashboard')
            except UserProfile.DoesNotExist:
                messages.error(request, 'User profile not found.')
                return redirect('login')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# ==================== ADMIN VIEWS ====================

@login_required
@role_required('admin')
def admin_dashboard(request):
    """Admin dashboard with overview statistics"""
    context = {
        'total_students': Student.objects.count(),
        'total_teachers': Teacher.objects.count(),
        'total_subjects': Subject.objects.count(),
        'total_grades': Grade.objects.count(),
        'recent_students': Student.objects.all().order_by('-created_at')[:5],
        'recent_teachers': Teacher.objects.all().order_by('-created_at')[:5],
    }
    return render(request, 'users/admin/dashboard.html', context)


@login_required
@role_required('admin')
def admin_students(request):
    """Manage students"""
    search_query = request.GET.get('search', '')
    students = Student.objects.all()
    
    if search_query:
        students = students.filter(
            Q(student_number__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    students = students.order_by('-created_at')
    
    context = {
        'students': students,
        'search_query': search_query,
    }
    return render(request, 'users/admin/students.html', context)


@login_required
@role_required('admin')
def admin_student_create(request):
    """Create new student"""
    if request.method == 'POST':
        try:
            # Create user account
            username = request.POST.get('student_number')
            email = request.POST.get('email')
            password = request.POST.get('password', 'student123')
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name')
            )
            
            # Create user profile
            UserProfile.objects.create(user=user, role='student')
            
            # Create student record
            student = Student(
                student_number=request.POST.get('student_number'),
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                email=email,
                gender=request.POST.get('gender'),
                birthdate=request.POST.get('birthdate') or None,
                course=request.POST.get('course'),
                year_level=request.POST.get('year_level') or None,
                section=request.POST.get('section'),
                enrollment_date=request.POST.get('enrollment_date') or None
            )
            student.save()
            
            messages.success(request, f'Student {student.get_full_name()} created successfully!')
            return redirect('admin_students')
        except Exception as e:
            messages.error(request, f'Error creating student: {str(e)}')
    
    return render(request, 'users/admin/student_form.html')


@login_required
@role_required('admin')
def admin_student_edit(request, student_id):
    """Edit student"""
    student = get_object_or_404(Student, student_id=student_id)
    
    if request.method == 'POST':
        try:
            student.first_name = request.POST.get('first_name')
            student.last_name = request.POST.get('last_name')
            student.email = request.POST.get('email')
            student.gender = request.POST.get('gender')
            student.birthdate = request.POST.get('birthdate') or None
            student.course = request.POST.get('course')
            student.year_level = request.POST.get('year_level') or None
            student.section = request.POST.get('section')
            student.enrollment_date = request.POST.get('enrollment_date') or None
            student.phone = request.POST.get('phone', '')
            student.address = request.POST.get('address', '')
            student.guardian_name = request.POST.get('guardian_name', '')
            student.guardian_contact = request.POST.get('guardian_contact', '')
            
            # Handle profile picture upload
            if 'profile_picture' in request.FILES:
                student.profile_picture = request.FILES['profile_picture']
            
            student.save()
            
            messages.success(request, f'Student {student.get_full_name()} updated successfully!')
            return redirect('admin_students')
        except Exception as e:
            messages.error(request, f'Error updating student: {str(e)}')
    
    context = {'student': student}
    return render(request, 'users/admin/student_form.html', context)


@login_required
@role_required('admin')
def admin_student_delete(request, student_id):
    """Delete student"""
    student = get_object_or_404(Student, student_id=student_id)
    
    if request.method == 'POST':
        try:
            name = student.get_full_name()
            # Try to delete associated user
            try:
                user = User.objects.get(username=student.student_number)
                user.delete()
            except User.DoesNotExist:
                pass
            student.delete()
            messages.success(request, f'Student {name} deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting student: {str(e)}')
    
    return redirect('admin_students')


@login_required
@role_required('admin')
def admin_teachers(request):
    """Manage teachers"""
    search_query = request.GET.get('search', '')
    teachers = Teacher.objects.all()
    
    if search_query:
        teachers = teachers.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(department__icontains=search_query)
        )
    
    teachers = teachers.order_by('-created_at')
    
    context = {
        'teachers': teachers,
        'search_query': search_query,
    }
    return render(request, 'users/admin/teachers.html', context)


@login_required
@role_required('admin')
def admin_teacher_create(request):
    """Create new teacher"""
    if request.method == 'POST':
        try:
            # Create user account
            email = request.POST.get('email')
            username = email.split('@')[0]
            password = request.POST.get('password', 'teacher123')
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name')
            )
            
            # Create user profile
            UserProfile.objects.create(user=user, role='teacher')
            
            # Create teacher record
            teacher = Teacher(
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                email=email,
                department=request.POST.get('department')
            )
            teacher.save()
            
            messages.success(request, f'Teacher {teacher.get_full_name()} created successfully!')
            return redirect('admin_teachers')
        except Exception as e:
            messages.error(request, f'Error creating teacher: {str(e)}')
    
    return render(request, 'users/admin/teacher_form.html')


@login_required
@role_required('admin')
def admin_teacher_edit(request, teacher_id):
    """Edit teacher"""
    teacher = get_object_or_404(Teacher, teacher_id=teacher_id)
    
    if request.method == 'POST':
        try:
            teacher.first_name = request.POST.get('first_name')
            teacher.last_name = request.POST.get('last_name')
            teacher.email = request.POST.get('email')
            teacher.department = request.POST.get('department')
            teacher.phone = request.POST.get('phone', '')
            teacher.specialization = request.POST.get('specialization', '')
            teacher.qualification = request.POST.get('qualification', '')
            teacher.bio = request.POST.get('bio', '')
            
            # Handle profile picture upload
            if 'profile_picture' in request.FILES:
                teacher.profile_picture = request.FILES['profile_picture']
            
            teacher.save()
            
            messages.success(request, f'Teacher {teacher.get_full_name()} updated successfully!')
            return redirect('admin_teachers')
        except Exception as e:
            messages.error(request, f'Error updating teacher: {str(e)}')
    
    context = {'teacher': teacher}
    return render(request, 'users/admin/teacher_form.html', context)


@login_required
@role_required('admin')
def admin_teacher_delete(request, teacher_id):
    """Delete teacher"""
    teacher = get_object_or_404(Teacher, teacher_id=teacher_id)
    
    if request.method == 'POST':
        try:
            name = teacher.get_full_name()
            # Try to delete associated user
            try:
                username = teacher.email.split('@')[0]
                user = User.objects.get(username=username)
                user.delete()
            except User.DoesNotExist:
                pass
            teacher.delete()
            messages.success(request, f'Teacher {name} deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting teacher: {str(e)}')
    
    return redirect('admin_teachers')


@login_required
@role_required('admin')
def admin_subjects(request):
    """Manage subjects"""
    search_query = request.GET.get('search', '')
    subjects = Subject.objects.select_related('teacher').all()
    
    if search_query:
        subjects = subjects.filter(
            Q(subject_code__icontains=search_query) |
            Q(subject_name__icontains=search_query)
        )
    
    subjects = subjects.order_by('subject_code')
    teachers = Teacher.objects.all().order_by('first_name')
    
    context = {
        'subjects': subjects,
        'teachers': teachers,
        'search_query': search_query,
    }
    return render(request, 'users/admin/subjects.html', context)


@login_required
@role_required('admin')
def admin_subject_create(request):
    """Create new subject"""
    if request.method == 'POST':
        try:
            teacher_id = request.POST.get('teacher_id')
            teacher = Teacher.objects.get(teacher_id=teacher_id) if teacher_id else None
            
            subject = Subject(
                subject_code=request.POST.get('subject_code'),
                subject_name=request.POST.get('subject_name'),
                units=request.POST.get('units', 3),
                teacher=teacher
            )
            subject.save()
            
            messages.success(request, f'Subject {subject.subject_code} created successfully!')
            return redirect('admin_subjects')
        except Exception as e:
            messages.error(request, f'Error creating subject: {str(e)}')
    
    teachers = Teacher.objects.all().order_by('first_name')
    context = {'teachers': teachers}
    return render(request, 'users/admin/subject_form.html', context)


@login_required
@role_required('admin')
def admin_subject_edit(request, subject_id):
    """Edit subject"""
    subject = get_object_or_404(Subject, subject_id=subject_id)
    
    if request.method == 'POST':
        try:
            teacher_id = request.POST.get('teacher_id')
            teacher = Teacher.objects.get(teacher_id=teacher_id) if teacher_id else None
            
            subject.subject_code = request.POST.get('subject_code')
            subject.subject_name = request.POST.get('subject_name')
            subject.units = request.POST.get('units', 3)
            subject.teacher = teacher
            subject.save()
            
            messages.success(request, f'Subject {subject.subject_code} updated successfully!')
            return redirect('admin_subjects')
        except Exception as e:
            messages.error(request, f'Error updating subject: {str(e)}')
    
    teachers = Teacher.objects.all().order_by('first_name')
    context = {'subject': subject, 'teachers': teachers}
    return render(request, 'users/admin/subject_form.html', context)


@login_required
@role_required('admin')
def admin_subject_delete(request, subject_id):
    """Delete subject"""
    subject = get_object_or_404(Subject, subject_id=subject_id)
    
    if request.method == 'POST':
        try:
            code = subject.subject_code
            subject.delete()
            messages.success(request, f'Subject {code} deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting subject: {str(e)}')
    
    return redirect('admin_subjects')


# ==================== TEACHER VIEWS ====================

@login_required
@role_required('teacher')
def teacher_dashboard(request):
    """Teacher dashboard with student management and filtering"""
    try:
        # Find teacher by matching user's username with email prefix
        username = request.user.username
        teacher = Teacher.objects.get(email__startswith=username)
        
        # Get filter parameters
        section_filter = request.GET.get('section', '')
        course_filter = request.GET.get('course', '')
        year_filter = request.GET.get('year', '')
        
        # Get all students with optional filters
        students = Student.objects.all()
        
        if section_filter:
            students = students.filter(section=section_filter)
        if course_filter:
            students = students.filter(course=course_filter)
        if year_filter:
            students = students.filter(year_level=year_filter)
        
        students = students.order_by('course', 'year_level', 'section', 'last_name')
        
        # Get distinct filter options
        all_sections = Student.objects.exclude(section__isnull=True).exclude(section='').values_list('section', flat=True).distinct().order_by('section')
        all_courses = Student.objects.exclude(course__isnull=True).exclude(course='').values_list('course', flat=True).distinct().order_by('course')
        all_years = Student.objects.exclude(year_level__isnull=True).values_list('year_level', flat=True).distinct().order_by('year_level')
        
        my_subjects = Subject.objects.filter(teacher=teacher)
        recent_grades = Grade.objects.filter(recorded_by=teacher).order_by('-created_at')[:10]
        recent_assessments = LearningAssessment.objects.filter(teacher=teacher).order_by('-assessment_date')[:10]
        
        from datetime import date
        
        context = {
            'teacher': teacher,
            'my_subjects': my_subjects,
            'recent_grades': recent_grades,
            'recent_assessments': recent_assessments,
            'total_subjects': my_subjects.count(),
            'students': students,
            'total_students': students.count(),
            'all_sections': all_sections,
            'all_courses': all_courses,
            'all_years': all_years,
            'section_filter': section_filter,
            'course_filter': course_filter,
            'year_filter': year_filter,
            'today': date.today(),
        }
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher profile not found.')
        return redirect('dashboard')
    
    return render(request, 'users/teacher/dashboard.html', context)


@login_required
@role_required('teacher')
def teacher_students(request):
    """View all students"""
    search_query = request.GET.get('search', '')
    students = Student.objects.all()
    
    if search_query:
        students = students.filter(
            Q(student_number__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    students = students.order_by('last_name', 'first_name')
    
    context = {
        'students': students,
        'search_query': search_query,
    }
    return render(request, 'users/teacher/students.html', context)


@login_required
@role_required('teacher')
def teacher_add_student(request):
    """Add a new student (teacher function)"""
    if request.method == 'POST':
        try:
            # Create student record in database
            student = Student(
                student_number=request.POST.get('student_number'),
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                email=request.POST.get('email') or None,
                gender=request.POST.get('gender') or None,
                birthdate=request.POST.get('birthdate') or None,
                course=request.POST.get('course'),
                year_level=request.POST.get('year_level'),
                section=request.POST.get('section'),
                enrollment_date=request.POST.get('enrollment_date') or None,
            )
            
            # Execute raw SQL to insert student
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO students 
                    (student_number, first_name, last_name, email, gender, birthdate, 
                     course, year_level, section, enrollment_date, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                """, [
                    student.student_number,
                    student.first_name,
                    student.last_name,
                    student.email,
                    student.gender,
                    student.birthdate,
                    student.course,
                    student.year_level,
                    student.section,
                    student.enrollment_date
                ])
            
            # Create user account
            try:
                user = User.objects.create_user(
                    username=student.student_number,
                    email=student.email or f"{student.student_number}@mindmap.edu",
                    password='student123',
                    first_name=student.first_name,
                    last_name=student.last_name
                )
                
                # Create user profile
                UserProfile.objects.create(user=user, role='student')
                
                messages.success(request, f'Student {student.get_full_name()} added successfully! Login credentials: {student.student_number}/student123')
            except Exception as e:
                messages.warning(request, f'Student added to database but user account creation failed: {str(e)}')
            
            return redirect('teacher_dashboard')
            
        except Exception as e:
            messages.error(request, f'Error adding student: {str(e)}')
            return redirect('teacher_dashboard')
    
    return redirect('teacher_dashboard')


@login_required
@role_required('teacher')
def teacher_grades(request):
    """Manage grades"""
    try:
        username = request.user.username
        teacher = Teacher.objects.get(email__startswith=username)
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher profile not found.')
        return redirect('dashboard')
    
    my_subjects = Subject.objects.filter(teacher=teacher)
    
    subject_filter = request.GET.get('subject', '')
    search_query = request.GET.get('search', '')
    
    grades = Grade.objects.filter(recorded_by=teacher).select_related('student', 'subject')
    
    if subject_filter:
        grades = grades.filter(subject_id=subject_filter)
    
    if search_query:
        grades = grades.filter(
            Q(student__student_number__icontains=search_query) |
            Q(student__first_name__icontains=search_query) |
            Q(student__last_name__icontains=search_query)
        )
    
    grades = grades.order_by('-created_at')
    
    context = {
        'grades': grades,
        'my_subjects': my_subjects,
        'subject_filter': subject_filter,
        'search_query': search_query,
    }
    return render(request, 'users/teacher/grades.html', context)


@login_required
@role_required('teacher')
def teacher_grade_create(request):
    """Add new grade"""
    try:
        username = request.user.username
        teacher = Teacher.objects.get(email__startswith=username)
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher profile not found.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        try:
            student = Student.objects.get(student_id=request.POST.get('student_id'))
            subject = Subject.objects.get(subject_id=request.POST.get('subject_id'))
            
            prelim = request.POST.get('prelim') or None
            midterm = request.POST.get('midterm') or None
            finals = request.POST.get('finals') or None
            
            # Calculate final grade
            grades_list = [float(g) for g in [prelim, midterm, finals] if g]
            final_grade = sum(grades_list) / len(grades_list) if grades_list else None
            
            # Determine remarks
            remarks = ''
            if final_grade:
                if final_grade >= 75:
                    remarks = 'PASSED'
                else:
                    remarks = 'FAILED'
            
            grade = Grade(
                student=student,
                subject=subject,
                school_year=request.POST.get('school_year'),
                semester=request.POST.get('semester'),
                prelim=prelim,
                midterm=midterm,
                finals=finals,
                final_grade=final_grade,
                remarks=remarks,
                recorded_by=teacher
            )
            grade.save()
            
            messages.success(request, 'Grade added successfully!')
            return redirect('teacher_grades')
        except Exception as e:
            messages.error(request, f'Error adding grade: {str(e)}')
    
    students = Student.objects.all().order_by('last_name')
    subjects = Subject.objects.filter(teacher=teacher)
    
    context = {
        'students': students,
        'subjects': subjects,
    }
    return render(request, 'users/teacher/grade_form.html', context)


@login_required
@role_required('teacher')
def teacher_grade_edit(request, grade_id):
    """Edit grade"""
    try:
        username = request.user.username
        teacher = Teacher.objects.get(email__startswith=username)
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher profile not found.')
        return redirect('dashboard')
    
    grade = get_object_or_404(Grade, grade_id=grade_id, recorded_by=teacher)
    
    if request.method == 'POST':
        try:
            prelim = request.POST.get('prelim') or None
            midterm = request.POST.get('midterm') or None
            finals = request.POST.get('finals') or None
            
            # Calculate final grade
            grades_list = [float(g) for g in [prelim, midterm, finals] if g]
            final_grade = sum(grades_list) / len(grades_list) if grades_list else None
            
            # Determine remarks
            remarks = ''
            if final_grade:
                if final_grade >= 75:
                    remarks = 'PASSED'
                else:
                    remarks = 'FAILED'
            
            grade.prelim = prelim
            grade.midterm = midterm
            grade.finals = finals
            grade.final_grade = final_grade
            grade.remarks = remarks
            grade.school_year = request.POST.get('school_year')
            grade.semester = request.POST.get('semester')
            grade.save()
            
            messages.success(request, 'Grade updated successfully!')
            return redirect('teacher_grades')
        except Exception as e:
            messages.error(request, f'Error updating grade: {str(e)}')
    
    subjects = Subject.objects.filter(teacher=teacher)
    
    context = {
        'grade': grade,
        'subjects': subjects,
    }
    return render(request, 'users/teacher/grade_form.html', context)


@login_required
@role_required('teacher')
def teacher_assessments(request):
    """Manage assessments"""
    try:
        username = request.user.username
        teacher = Teacher.objects.get(email__startswith=username)
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher profile not found.')
        return redirect('dashboard')
    
    subject_filter = request.GET.get('subject', '')
    search_query = request.GET.get('search', '')
    
    assessments = LearningAssessment.objects.filter(teacher=teacher).select_related('student', 'subject')
    
    if subject_filter:
        assessments = assessments.filter(subject_id=subject_filter)
    
    if search_query:
        assessments = assessments.filter(
            Q(student__student_number__icontains=search_query) |
            Q(student__first_name__icontains=search_query) |
            Q(student__last_name__icontains=search_query)
        )
    
    assessments = assessments.order_by('-assessment_date')
    my_subjects = Subject.objects.filter(teacher=teacher)
    
    context = {
        'assessments': assessments,
        'my_subjects': my_subjects,
        'subject_filter': subject_filter,
        'search_query': search_query,
    }
    return render(request, 'users/teacher/assessments.html', context)


@login_required
@role_required('teacher')
def teacher_assessment_create(request):
    """Add new assessment"""
    try:
        username = request.user.username
        teacher = Teacher.objects.get(email__startswith=username)
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher profile not found.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        try:
            student = Student.objects.get(student_id=request.POST.get('student_id'))
            subject = Subject.objects.get(subject_id=request.POST.get('subject_id'))
            
            assessment = LearningAssessment(
                student=student,
                subject=subject,
                teacher=teacher,
                assessment_date=request.POST.get('assessment_date'),
                skill_area=request.POST.get('skill_area'),
                assessment_type=request.POST.get('assessment_type'),
                score=request.POST.get('score') or None,
                max_score=request.POST.get('max_score') or None,
                strengths=request.POST.get('strengths'),
                areas_to_improve=request.POST.get('areas_to_improve'),
                notes=request.POST.get('notes')
            )
            assessment.save()
            
            messages.success(request, 'Assessment added successfully!')
            return redirect('teacher_assessments')
        except Exception as e:
            messages.error(request, f'Error adding assessment: {str(e)}')
    
    students = Student.objects.all().order_by('last_name')
    subjects = Subject.objects.filter(teacher=teacher)
    
    context = {
        'students': students,
        'subjects': subjects,
    }
    return render(request, 'users/teacher/assessment_form.html', context)


@login_required
@role_required('teacher')
def teacher_assessment_edit(request, assessment_id):
    """Edit assessment"""
    try:
        username = request.user.username
        teacher = Teacher.objects.get(email__startswith=username)
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher profile not found.')
        return redirect('dashboard')
    
    assessment = get_object_or_404(LearningAssessment, assessment_id=assessment_id, teacher=teacher)
    
    if request.method == 'POST':
        try:
            assessment.assessment_date = request.POST.get('assessment_date')
            assessment.skill_area = request.POST.get('skill_area')
            assessment.assessment_type = request.POST.get('assessment_type')
            assessment.score = request.POST.get('score') or None
            assessment.max_score = request.POST.get('max_score') or None
            assessment.strengths = request.POST.get('strengths')
            assessment.areas_to_improve = request.POST.get('areas_to_improve')
            assessment.notes = request.POST.get('notes')
            assessment.save()
            
            messages.success(request, 'Assessment updated successfully!')
            return redirect('teacher_assessments')
        except Exception as e:
            messages.error(request, f'Error updating assessment: {str(e)}')
    
    subjects = Subject.objects.filter(teacher=teacher)
    
    context = {
        'assessment': assessment,
        'subjects': subjects,
    }
    return render(request, 'users/teacher/assessment_form.html', context)


@login_required
@role_required('teacher')
def teacher_progress(request):
    """View academic progress records"""
    try:
        username = request.user.username
        teacher = Teacher.objects.get(email__startswith=username)
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher profile not found.')
        return redirect('dashboard')
    
    search_query = request.GET.get('search', '')
    progress_records = AcademicProgress.objects.filter(teacher=teacher).select_related('student')
    
    if search_query:
        progress_records = progress_records.filter(
            Q(student__student_number__icontains=search_query) |
            Q(student__first_name__icontains=search_query) |
            Q(student__last_name__icontains=search_query)
        )
    
    progress_records = progress_records.order_by('-assessment_date')
    
    context = {
        'progress_records': progress_records,
        'search_query': search_query,
    }
    return render(request, 'users/teacher/progress.html', context)


@login_required
@role_required('teacher')
def teacher_progress_create(request):
    """Add progress record"""
    try:
        username = request.user.username
        teacher = Teacher.objects.get(email__startswith=username)
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher profile not found.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        try:
            student = Student.objects.get(student_id=request.POST.get('student_id'))
            
            progress = AcademicProgress(
                student=student,
                teacher=teacher,
                assessment_date=request.POST.get('assessment_date'),
                progress_category=request.POST.get('progress_category'),
                observation=request.POST.get('observation'),
                recommendation=request.POST.get('recommendation'),
                status=request.POST.get('status')
            )
            progress.save()
            
            messages.success(request, 'Progress record added successfully!')
            return redirect('teacher_progress')
        except Exception as e:
            messages.error(request, f'Error adding progress record: {str(e)}')
    
    students = Student.objects.all().order_by('last_name')
    
    context = {'students': students}
    return render(request, 'users/teacher/progress_form.html', context)


# ==================== STUDENT VIEWS ====================

@login_required
@role_required('student')
def student_dashboard(request):
    """Student dashboard"""
    try:
        # Find student by matching username with student_number
        student = Student.objects.get(student_number=request.user.username)
        
        # Get recent grades
        recent_grades = Grade.objects.filter(student=student).select_related('subject').order_by('-created_at')[:5]
        
        # Calculate average grade
        all_grades = Grade.objects.filter(student=student, final_grade__isnull=False)
        avg_grade = all_grades.aggregate(Avg('final_grade'))['final_grade__avg']
        
        # Get recent assessments
        recent_assessments = LearningAssessment.objects.filter(student=student).order_by('-assessment_date')[:5]
        
        # Get recent progress
        recent_progress = AcademicProgress.objects.filter(student=student).order_by('-assessment_date')[:5]
        
        context = {
            'student': student,
            'recent_grades': recent_grades,
            'avg_grade': avg_grade,
            'recent_assessments': recent_assessments,
            'recent_progress': recent_progress,
            'total_grades': all_grades.count(),
        }
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('dashboard')
    
    return render(request, 'users/student/dashboard.html', context)


@login_required
@role_required('student')
def student_grades(request):
    """View my grades"""
    student = Student.objects.get(student_number=request.user.username)
    
    subject_filter = request.GET.get('subject', '')
    semester_filter = request.GET.get('semester', '')
    
    grades = Grade.objects.filter(student=student).select_related('subject', 'recorded_by')
    
    if subject_filter:
        grades = grades.filter(subject_id=subject_filter)
    
    if semester_filter:
        grades = grades.filter(semester=semester_filter)
    
    grades = grades.order_by('-school_year', '-semester')
    
    # Get unique subjects and semesters for filters
    subjects = Subject.objects.filter(grade__student=student).distinct()
    semesters = Grade.objects.filter(student=student).values_list('semester', flat=True).distinct()
    
    # Calculate statistics
    avg_grade = grades.filter(final_grade__isnull=False).aggregate(Avg('final_grade'))['final_grade__avg']
    
    context = {
        'grades': grades,
        'subjects': subjects,
        'semesters': semesters,
        'subject_filter': subject_filter,
        'semester_filter': semester_filter,
        'avg_grade': avg_grade,
    }
    return render(request, 'users/student/grades.html', context)


@login_required
@role_required('student')
def student_assessments(request):
    """View my assessments"""
    student = Student.objects.get(student_number=request.user.username)
    
    subject_filter = request.GET.get('subject', '')
    
    assessments = LearningAssessment.objects.filter(student=student).select_related('subject', 'teacher')
    
    if subject_filter:
        assessments = assessments.filter(subject_id=subject_filter)
    
    assessments = assessments.order_by('-assessment_date')
    
    # Get unique subjects for filter
    subjects = Subject.objects.filter(learningassessment__student=student).distinct()
    
    context = {
        'assessments': assessments,
        'subjects': subjects,
        'subject_filter': subject_filter,
    }
    return render(request, 'users/student/assessments.html', context)


@login_required
@role_required('student')
def student_progress(request):
    """View my academic progress"""
    student = Student.objects.get(student_number=request.user.username)
    
    status_filter = request.GET.get('status', '')
    
    progress_records = AcademicProgress.objects.filter(student=student).select_related('teacher')
    
    if status_filter:
        progress_records = progress_records.filter(status=status_filter)
    
    progress_records = progress_records.order_by('-assessment_date')
    
    # Status statistics
    status_stats = AcademicProgress.objects.filter(student=student).values('status').annotate(count=Count('status'))
    
    context = {
        'progress_records': progress_records,
        'status_filter': status_filter,
        'status_stats': status_stats,
    }
    return render(request, 'users/student/progress.html', context)


@login_required
@role_required('student')
def student_report(request):
    """View comprehensive progress report"""
    student = Student.objects.get(student_number=request.user.username)
    
    # Grades summary
    all_grades = Grade.objects.filter(student=student, final_grade__isnull=False).select_related('subject')
    avg_grade = all_grades.aggregate(Avg('final_grade'))['final_grade__avg']
    passed_count = all_grades.filter(final_grade__gte=75).count()
    failed_count = all_grades.filter(final_grade__lt=75).count()
    
    # Assessment summary
    all_assessments = LearningAssessment.objects.filter(student=student, score__isnull=False, max_score__isnull=False)
    
    # Progress summary
    progress_summary = AcademicProgress.objects.filter(student=student).values('status').annotate(count=Count('status'))
    latest_progress = AcademicProgress.objects.filter(student=student).order_by('-assessment_date')[:5]
    
    # Strengths and areas to improve from assessments
    strengths_list = []
    improvements_list = []
    
    for assessment in all_assessments[:10]:
        if assessment.strengths:
            strengths_list.append(assessment.strengths)
        if assessment.areas_to_improve:
            improvements_list.append(assessment.areas_to_improve)
    
    context = {
        'student': student,
        'all_grades': all_grades,
        'avg_grade': avg_grade,
        'passed_count': passed_count,
        'failed_count': failed_count,
        'total_assessments': all_assessments.count(),
        'progress_summary': progress_summary,
        'latest_progress': latest_progress,
        'strengths_list': strengths_list[:5],
        'improvements_list': improvements_list[:5],
    }
    return render(request, 'users/student/report.html', context)
