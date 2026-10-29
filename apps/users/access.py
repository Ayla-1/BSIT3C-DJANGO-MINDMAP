"""Server-side scoping helpers.

Every teacher-facing view goes through these helpers so permissions can never
be bypassed by editing a URL, form field or hidden input.
"""

from django.shortcuts import get_object_or_404

from .models import (
    AcademicProgress,
    Announcement,
    Grade,
    LearningAssessment,
    Student,
    Subject,
    Teacher,
)


def get_teacher(user):
    """Return the Teacher record owned by this user, or None."""
    if not user.is_authenticated:
        return None
    return Teacher.objects.filter(user=user).first()


def teacher_subjects(teacher):
    if teacher is None:
        return Subject.objects.none()
    return Subject.objects.filter(teacher=teacher).order_by('name')


def teacher_students(teacher):
    if teacher is None:
        return Student.objects.none()
    return (
        Student.objects.filter(section__subjects__teacher=teacher)
        .select_related('section')
        .distinct()
        .order_by('last_name', 'first_name')
    )


def teacher_sections(teacher):
    from .models import Section

    if teacher is None:
        return Section.objects.none()
    return Section.objects.filter(subjects__teacher=teacher).distinct().order_by('name')


def teacher_subject_or_404(teacher, subject_id):
    """Only subjects assigned to this teacher are reachable."""
    return get_object_or_404(teacher_subjects(teacher), pk=subject_id)


def teacher_student_or_404(teacher, student_id):
    return get_object_or_404(teacher_students(teacher), pk=student_id)


def teacher_grade_or_404(teacher, grade_id):
    return get_object_or_404(
        Grade.objects.select_related('student', 'subject'),
        pk=grade_id,
        subject__teacher=teacher,
    )


def teacher_progress_or_404(teacher, progress_id):
    return get_object_or_404(
        AcademicProgress.objects.select_related('student', 'subject'),
        pk=progress_id,
        subject__teacher=teacher,
    )


def teacher_assessment_or_404(teacher, assessment_id):
    return get_object_or_404(
        LearningAssessment.objects.select_related('student', 'subject'),
        pk=assessment_id,
        subject__teacher=teacher,
    )


def student_for_user(user):
    if not user.is_authenticated:
        return None
    return Student.objects.filter(user=user).select_related('section', 'section__adviser').first()


def visible_announcements(user):
    """Announcements a signed-in user is allowed to read."""
    role = getattr(getattr(user, 'profile', None), 'role', None)
    if role == 'admin':
        return Announcement.objects.all()
    audience = 'teachers' if role == 'teacher' else 'students'
    return Announcement.objects.filter(audience__in=['all', audience])
