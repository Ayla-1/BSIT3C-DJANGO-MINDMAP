"""High school academic models: sections, teachers, students, subjects, grades,
learning assessments, academic progress and announcements."""

from decimal import Decimal

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


GRADE_LEVEL_CHOICES = [
    ('Grade 7', 'Grade 7'),
    ('Grade 8', 'Grade 8'),
    ('Grade 9', 'Grade 9'),
    ('Grade 10', 'Grade 10'),
    ('Grade 11', 'Grade 11'),
    ('Grade 12', 'Grade 12'),
]

SCHOOL_YEAR_DEFAULT = '2026-2027'
QUARTER_CHOICES = [
    (1, 'Quarter 1'),
    (2, 'Quarter 2'),
    (3, 'Quarter 3'),
    (4, 'Quarter 4'),
]

PASSING_GRADE = Decimal('75')


def descriptive_rating(grade):
    """Return the DepEd descriptive rating for a grade."""
    if grade is None:
        return 'No grade yet'
    if grade >= 90:
        return 'Outstanding'
    if grade >= 85:
        return 'Very Satisfactory'
    if grade >= 80:
        return 'Satisfactory'
    if grade >= 75:
        return 'Fairly Satisfactory'
    return 'Did Not Meet Expectations'


class Section(models.Model):
    """A high school class section (Section A, Section B)."""

    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=10, unique=True)
    grade_level = models.CharField(max_length=20, choices=GRADE_LEVEL_CHOICES, default='Grade 11')
    adviser = models.ForeignKey(
        'Teacher', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='advised_sections',
    )
    room = models.CharField(max_length=50, null=True, blank=True)
    school_year = models.CharField(max_length=20, default=SCHOOL_YEAR_DEFAULT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['grade_level', 'name']

    def __str__(self):
        return self.name

    @property
    def display_name(self):
        return f'{self.grade_level} - {self.name}'

    def student_count(self):
        return self.students.count()


class Teacher(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True,
        related_name='teacher_profile',
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=150, unique=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    specialization = models.CharField(max_length=200, null=True, blank=True)
    qualification = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='teachers/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def full_name(self):
        return self.get_full_name()

    def get_profile_picture_url(self):
        if self.profile_picture:
            return self.profile_picture.url
        return '/static/img/default-avatar.svg'

    @property
    def assigned_subjects(self):
        return self.subjects.select_related('teacher').order_by('name')

    def assigned_students(self):
        """Students enrolled in the sections where this teacher handles a subject."""
        return Student.objects.filter(
            section__subjects__teacher=self,
        ).distinct().order_by('last_name', 'first_name')


class Student(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True,
        related_name='student_profile',
    )
    student_number = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=150, null=True, blank=True)
    gender = models.CharField(max_length=20, null=True, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    grade_level = models.CharField(max_length=20, choices=GRADE_LEVEL_CHOICES, default='Grade 11')
    section = models.ForeignKey(
        Section, on_delete=models.PROTECT, related_name='students',
        db_column='section_id',
    )
    enrollment_date = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='students/', null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    guardian_name = models.CharField(max_length=200, null=True, blank=True)
    guardian_contact = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f'{self.student_number} - {self.get_full_name()}'

    def save(self, *args, **kwargs):
        # A student's grade level always follows the section they belong to.
        if self.section_id:
            self.grade_level = self.section.grade_level
        super().save(*args, **kwargs)

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def full_name(self):
        return self.get_full_name()

    def get_user(self):
        return self.user

    def get_profile_picture_url(self):
        if self.profile_picture:
            return self.profile_picture.url
        return '/static/img/default-avatar.svg'

    def average_grade(self, school_year=None):
        grades = self.grades.filter(final_grade__isnull=False)
        if school_year:
            grades = grades.filter(school_year=school_year)
        values = [g.final_grade for g in grades]
        if not values:
            return None
        return (sum(values) / len(values)).quantize(Decimal('0.01'))

    def performance_label(self):
        average = self.average_grade()
        if average is None:
            return 'No grades yet'
        if average >= 90:
            return 'Excellent'
        if average >= 85:
            return 'Very Good'
        if average >= 80:
            return 'Good'
        if average >= 75:
            return 'Satisfactory'
        return 'At Risk'


class Subject(models.Model):
    """A high school subject handled by exactly one teacher."""

    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    teacher = models.ForeignKey(
        Teacher, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='subjects',
    )
    sections = models.ManyToManyField(
        Section, related_name='subjects', blank=True,
        help_text='Sections that take this subject.',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Grade(models.Model):
    """Quarterly grade of a student in one subject."""

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='grades')
    quarter = models.PositiveSmallIntegerField(choices=QUARTER_CHOICES, default=1)
    school_year = models.CharField(max_length=20, default=SCHOOL_YEAR_DEFAULT)
    written_work = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Average written work score (30%).',
    )
    performance_task = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Average performance task score (50%).',
    )
    quarterly_assessment = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Quarterly assessment score (20%).',
    )
    final_grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    remarks = models.CharField(max_length=30, null=True, blank=True)
    recorded_by = models.ForeignKey(
        Teacher, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='recorded_grades',
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['subject__name', 'quarter']
        unique_together = ('student', 'subject', 'quarter', 'school_year')

    def __str__(self):
        return f'{self.student.student_number} - {self.subject.name} - Q{self.quarter}'

    def compute_final_grade(self):
        """Weighted quarterly grade: WW 30%, PT 50%, QA 20%."""
        parts = [
            (self.written_work, Decimal('0.30')),
            (self.performance_task, Decimal('0.50')),
            (self.quarterly_assessment, Decimal('0.20')),
        ]
        present = [(value, weight) for value, weight in parts if value is not None]
        if not present:
            return None
        total_weight = sum(weight for _, weight in present)
        weighted = sum(Decimal(value) * weight for value, weight in present)
        return (weighted / total_weight).quantize(Decimal('0.01'))

    @property
    def rating(self):
        return descriptive_rating(self.final_grade)

    @property
    def passed(self):
        return self.final_grade is not None and self.final_grade >= PASSING_GRADE

    def save(self, *args, **kwargs):
        final_grade = self.compute_final_grade()
        if final_grade is None:
            self.final_grade = None
            self.remarks = 'No grade yet'
        else:
            self.final_grade = final_grade
            self.remarks = 'PASSED' if final_grade >= PASSING_GRADE else 'FAILED'

        # update_or_create() may restrict the UPDATE to the default fields; make
        # sure the derived grade and remarks are always persisted as well.
        update_fields = kwargs.get('update_fields')
        if update_fields is not None:
            kwargs['update_fields'] = set(update_fields) | {'final_grade', 'remarks'}

        super().save(*args, **kwargs)


class LearningAssessment(models.Model):
    """A learning assessment result recorded by a subject teacher."""

    ASSESSMENT_TYPES = [
        ('Quiz', 'Quiz'),
        ('Activity', 'Activity'),
        ('Performance Task', 'Performance Task'),
        ('Project', 'Project'),
        ('Exam', 'Exam'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='assessments')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='assessments')
    teacher = models.ForeignKey(
        Teacher, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assessments',
    )
    assessment_date = models.DateField()
    title = models.CharField(max_length=200)
    assessment_type = models.CharField(max_length=50, choices=ASSESSMENT_TYPES, default='Quiz')
    quarter = models.PositiveSmallIntegerField(choices=QUARTER_CHOICES, default=1)
    score = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0)],
    )
    max_score = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0)],
    )
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-assessment_date', '-pk']

    def __str__(self):
        return f'{self.student.student_number} - {self.title}'

    def get_percentage(self):
        if self.score is not None and self.max_score:
            return (self.score / self.max_score) * 100
        return None

    @property
    def percentage(self):
        return self.get_percentage()


class AcademicProgress(models.Model):
    """Teacher-written academic progress notes for a student in a subject."""

    STATUS_CHOICES = [
        ('Improving', 'Improving'),
        ('Excellent', 'Excellent'),
        ('Stable', 'Stable'),
        ('Needs Improvement', 'Needs Improvement'),
        ('At Risk', 'At Risk'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='progress_records')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='progress_records')
    teacher = models.ForeignKey(
        Teacher, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='progress_records',
    )
    record_date = models.DateField()
    strengths = models.TextField(help_text='Skills or lessons the student performs well in.')
    areas_for_improvement = models.TextField(help_text='Skills or lessons that need support.')
    recent_improvements = models.TextField(
        help_text='Progress the student has recently made.',
    )
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Improving')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-record_date', '-pk']

    def __str__(self):
        return f'{self.student.student_number} - {self.subject.name} - {self.record_date}'


class Announcement(models.Model):
    AUDIENCE_CHOICES = [
        ('all', 'Everyone'),
        ('students', 'Students'),
        ('teachers', 'Teachers'),
    ]

    title = models.CharField(max_length=200)
    body = models.TextField()
    audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, default='all')
    is_pinned = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='announcements',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return self.title
