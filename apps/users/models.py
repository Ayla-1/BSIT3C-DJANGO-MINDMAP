from django.db import models
from django.contrib.auth.models import User


class Student(models.Model):
    student_id = models.AutoField(primary_key=True)
    student_number = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=150, unique=True, null=True, blank=True)
    gender = models.CharField(max_length=20, null=True, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    course = models.CharField(max_length=100, null=True, blank=True)
    year_level = models.IntegerField(null=True, blank=True)
    section = models.CharField(max_length=50, null=True, blank=True)
    enrollment_date = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='students/', null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    guardian_name = models.CharField(max_length=200, null=True, blank=True)
    guardian_contact = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'students'
        managed = False

    def __str__(self):
        return f"{self.student_number} - {self.first_name} {self.last_name}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_user(self):
        """Get associated Django user if exists"""
        try:
            return User.objects.get(username=self.student_number)
        except User.DoesNotExist:
            return None
    
    def get_profile_picture_url(self):
        """Get profile picture URL or default"""
        if self.profile_picture:
            return self.profile_picture.url
        return '/static/img/default-avatar.svg'


class Teacher(models.Model):
    teacher_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=150, unique=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='teachers/', null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    specialization = models.CharField(max_length=200, null=True, blank=True)
    qualification = models.CharField(max_length=200, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'teachers'
        managed = False

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_user(self):
        """Get associated Django user if exists"""
        try:
            username = self.email.split('@')[0]
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None
    
    def get_profile_picture_url(self):
        """Get profile picture URL or default"""
        if self.profile_picture:
            return self.profile_picture.url
        return '/static/img/default-avatar.svg'


class Subject(models.Model):
    subject_id = models.AutoField(primary_key=True)
    subject_code = models.CharField(max_length=30, unique=True)
    subject_name = models.CharField(max_length=150)
    units = models.IntegerField(default=3)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, db_column='teacher_id')

    class Meta:
        db_table = 'subjects'
        managed = False

    def __str__(self):
        return f"{self.subject_code} - {self.subject_name}"


class Grade(models.Model):
    grade_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, db_column='student_id')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, db_column='subject_id')
    school_year = models.CharField(max_length=20)
    semester = models.CharField(max_length=20)
    prelim = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    midterm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    finals = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    final_grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    remarks = models.CharField(max_length=30, null=True, blank=True)
    recorded_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, db_column='recorded_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'grades'
        managed = False
        unique_together = ('student', 'subject', 'school_year', 'semester')

    def __str__(self):
        return f"{self.student.student_number} - {self.subject.subject_code} - {self.school_year}"

    def calculate_final_grade(self):
        """Calculate final grade based on prelim, midterm, and finals"""
        grades = [self.prelim, self.midterm, self.finals]
        valid_grades = [g for g in grades if g is not None]
        if valid_grades:
            return sum(valid_grades) / len(valid_grades)
        return None


class LearningAssessment(models.Model):
    assessment_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, db_column='student_id')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, db_column='subject_id')
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, db_column='teacher_id')
    assessment_date = models.DateField()
    skill_area = models.CharField(max_length=150)
    assessment_type = models.CharField(max_length=100, null=True, blank=True)
    score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    max_score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    strengths = models.TextField(null=True, blank=True)
    areas_to_improve = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'learning_assessments'
        managed = False

    def __str__(self):
        return f"{self.student.student_number} - {self.skill_area}"

    def get_percentage(self):
        """Calculate percentage score"""
        if self.score and self.max_score and self.max_score > 0:
            return (self.score / self.max_score) * 100
        return None


class AcademicProgress(models.Model):
    STATUS_CHOICES = [
        ('Improving', 'Improving'),
        ('Needs Improvement', 'Needs Improvement'),
        ('Excellent', 'Excellent'),
        ('At Risk', 'At Risk'),
    ]
    
    progress_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, db_column='student_id')
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, db_column='teacher_id')
    assessment_date = models.DateField()
    progress_category = models.CharField(max_length=100, null=True, blank=True)
    observation = models.TextField()
    recommendation = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Improving')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'academic_progress'
        managed = False

    def __str__(self):
        return f"{self.student.student_number} - {self.assessment_date}"
