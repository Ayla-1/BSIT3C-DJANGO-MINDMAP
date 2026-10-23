from django.urls import path
from apps.users import views as user_views

urlpatterns = [
    # Admin URLs
    path('admin/dashboard/', user_views.admin_dashboard, name='admin_dashboard'),
    path('admin/students/', user_views.admin_students, name='admin_students'),
    path('admin/students/create/', user_views.admin_student_create, name='admin_student_create'),
    path('admin/students/<int:student_id>/edit/', user_views.admin_student_edit, name='admin_student_edit'),
    path('admin/students/<int:student_id>/delete/', user_views.admin_student_delete, name='admin_student_delete'),
    path('admin/teachers/', user_views.admin_teachers, name='admin_teachers'),
    path('admin/teachers/create/', user_views.admin_teacher_create, name='admin_teacher_create'),
    path('admin/teachers/<int:teacher_id>/edit/', user_views.admin_teacher_edit, name='admin_teacher_edit'),
    path('admin/teachers/<int:teacher_id>/delete/', user_views.admin_teacher_delete, name='admin_teacher_delete'),
    path('admin/subjects/', user_views.admin_subjects, name='admin_subjects'),
    path('admin/subjects/create/', user_views.admin_subject_create, name='admin_subject_create'),
    path('admin/subjects/<int:subject_id>/edit/', user_views.admin_subject_edit, name='admin_subject_edit'),
    path('admin/subjects/<int:subject_id>/delete/', user_views.admin_subject_delete, name='admin_subject_delete'),
    
    # Teacher URLs
    path('teacher/dashboard/', user_views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/students/', user_views.teacher_students, name='teacher_students'),
    path('teacher/students/add/', user_views.teacher_add_student, name='teacher_add_student'),
    path('teacher/grades/', user_views.teacher_grades, name='teacher_grades'),
    path('teacher/grades/create/', user_views.teacher_grade_create, name='teacher_grade_create'),
    path('teacher/grades/<int:grade_id>/edit/', user_views.teacher_grade_edit, name='teacher_grade_edit'),
    path('teacher/assessments/', user_views.teacher_assessments, name='teacher_assessments'),
    path('teacher/assessments/create/', user_views.teacher_assessment_create, name='teacher_assessment_create'),
    path('teacher/assessments/<int:assessment_id>/edit/', user_views.teacher_assessment_edit, name='teacher_assessment_edit'),
    path('teacher/progress/', user_views.teacher_progress, name='teacher_progress'),
    path('teacher/progress/create/', user_views.teacher_progress_create, name='teacher_progress_create'),
    
    # Student URLs
    path('student/dashboard/', user_views.student_dashboard, name='student_dashboard'),
    path('student/grades/', user_views.student_grades, name='student_grades'),
    path('student/assessments/', user_views.student_assessments, name='student_assessments'),
    path('student/progress/', user_views.student_progress, name='student_progress'),
    path('student/report/', user_views.student_report, name='student_report'),
]