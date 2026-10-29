from django.urls import path

from apps.users import views as user_views

urlpatterns = [
    # Admin
    path('admin/dashboard/', user_views.admin_dashboard, name='admin_dashboard'),
    path('admin/students/', user_views.admin_students, name='admin_students'),
    path('admin/students/create/', user_views.admin_student_create, name='admin_student_create'),
    path('admin/students/<int:student_id>/edit/', user_views.admin_student_edit, name='admin_student_edit'),
    path('admin/students/<int:student_id>/delete/', user_views.admin_student_delete, name='admin_student_delete'),
    path('admin/teachers/', user_views.admin_teachers, name='admin_teachers'),
    path('admin/teachers/create/', user_views.admin_teacher_create, name='admin_teacher_create'),
    path('admin/teachers/<int:teacher_id>/edit/', user_views.admin_teacher_edit, name='admin_teacher_edit'),
    path('admin/teachers/<int:teacher_id>/delete/', user_views.admin_teacher_delete, name='admin_teacher_delete'),
    path('admin/assignments/', user_views.admin_teacher_assignments, name='admin_assignments'),
    path('admin/subjects/', user_views.admin_subjects, name='admin_subjects'),
    path('admin/subjects/create/', user_views.admin_subject_create, name='admin_subject_create'),
    path('admin/subjects/<int:subject_id>/edit/', user_views.admin_subject_edit, name='admin_subject_edit'),
    path('admin/subjects/<int:subject_id>/delete/', user_views.admin_subject_delete, name='admin_subject_delete'),
    path('admin/sections/', user_views.admin_sections, name='admin_sections'),
    path('admin/sections/create/', user_views.admin_section_create, name='admin_section_create'),
    path('admin/sections/<int:section_id>/edit/', user_views.admin_section_edit, name='admin_section_edit'),
    path('admin/sections/<int:section_id>/delete/', user_views.admin_section_delete, name='admin_section_delete'),
    path('admin/announcements/', user_views.admin_announcements, name='admin_announcements'),
    path('admin/announcements/create/', user_views.admin_announcement_create, name='admin_announcement_create'),
    path(
        'admin/announcements/<int:announcement_id>/delete/',
        user_views.admin_announcement_delete,
        name='admin_announcement_delete',
    ),

    # Teacher
    path('teacher/dashboard/', user_views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/students/', user_views.teacher_students_view, name='teacher_students'),
    path('teacher/students/<int:student_id>/', user_views.teacher_student_detail, name='teacher_student_detail'),
    path('teacher/gradebook/', user_views.teacher_gradebook, name='teacher_gradebook'),
    path('teacher/grades/', user_views.teacher_grades, name='teacher_grades'),
    path('teacher/assessments/', user_views.teacher_assessments, name='teacher_assessments'),
    path('teacher/assessments/create/', user_views.teacher_assessment_create, name='teacher_assessment_create'),
    path(
        'teacher/assessments/<int:assessment_id>/edit/',
        user_views.teacher_assessment_edit,
        name='teacher_assessment_edit',
    ),
    path('teacher/progress/', user_views.teacher_progress, name='teacher_progress'),
    path('teacher/progress/create/', user_views.teacher_progress_create, name='teacher_progress_create'),
    path('teacher/progress/<int:progress_id>/edit/', user_views.teacher_progress_edit, name='teacher_progress_edit'),

    # Student
    path('student/dashboard/', user_views.student_dashboard, name='student_dashboard'),
    path('student/grades/', user_views.student_grades, name='student_grades'),
    path('student/assessments/', user_views.student_assessments, name='student_assessments'),
    path('student/progress/', user_views.student_progress, name='student_progress'),
]
