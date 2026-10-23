from django.contrib import admin
from apps.users.models import Student, Teacher, Subject, Grade, LearningAssessment, AcademicProgress

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_number', 'first_name', 'last_name', 'course', 'year_level', 'section']
    search_fields = ['student_number', 'first_name', 'last_name', 'email']
    list_filter = ['course', 'year_level', 'section']

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['teacher_id', 'first_name', 'last_name', 'email', 'department']
    search_fields = ['first_name', 'last_name', 'email']
    list_filter = ['department']

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['subject_code', 'subject_name', 'units', 'teacher']
    search_fields = ['subject_code', 'subject_name']
    list_filter = ['teacher']

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'school_year', 'semester', 'final_grade', 'remarks']
    search_fields = ['student__student_number', 'subject__subject_code']
    list_filter = ['school_year', 'semester', 'remarks']

@admin.register(LearningAssessment)
class LearningAssessmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'skill_area', 'assessment_date', 'score', 'max_score']
    search_fields = ['student__student_number', 'subject__subject_code', 'skill_area']
    list_filter = ['assessment_date', 'assessment_type']

@admin.register(AcademicProgress)
class AcademicProgressAdmin(admin.ModelAdmin):
    list_display = ['student', 'assessment_date', 'progress_category', 'status', 'teacher']
    search_fields = ['student__student_number', 'progress_category']
    list_filter = ['status', 'assessment_date']
