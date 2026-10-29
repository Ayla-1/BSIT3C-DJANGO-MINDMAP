from django.contrib import admin

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


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'grade_level', 'adviser', 'school_year']
    list_filter = ['grade_level', 'school_year']
    search_fields = ['name', 'code']


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'department', 'user']
    search_fields = ['first_name', 'last_name', 'email']
    list_filter = ['department']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_number', 'last_name', 'first_name', 'grade_level', 'section']
    search_fields = ['student_number', 'first_name', 'last_name', 'email']
    list_filter = ['grade_level', 'section']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'teacher']
    search_fields = ['code', 'name']
    list_filter = ['teacher', 'sections']


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'quarter', 'final_grade', 'remarks']
    search_fields = ['student__student_number', 'subject__code']
    list_filter = ['quarter', 'school_year', 'remarks', 'subject']


@admin.register(LearningAssessment)
class LearningAssessmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'title', 'assessment_type', 'assessment_date', 'score', 'max_score']
    search_fields = ['student__student_number', 'subject__code', 'title']
    list_filter = ['assessment_type', 'quarter', 'assessment_date', 'subject']


@admin.register(AcademicProgress)
class AcademicProgressAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'record_date', 'status', 'teacher']
    search_fields = ['student__student_number', 'subject__code']
    list_filter = ['status', 'record_date', 'subject']


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'audience', 'is_pinned', 'created_at']
    list_filter = ['audience', 'is_pinned']
    search_fields = ['title', 'body']
