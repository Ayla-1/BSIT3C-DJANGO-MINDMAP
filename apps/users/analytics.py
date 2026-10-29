"""Read-only helpers that build the academic views used by dashboards."""

from decimal import Decimal

from .models import (
    QUARTER_CHOICES,
    AcademicProgress,
    Grade,
    LearningAssessment,
    Subject,
    descriptive_rating,
)

CURRENT_SCHOOL_YEAR = '2026-2027'
QUARTERS = [value for value, _ in QUARTER_CHOICES]


def bar_class(percent):
    if percent is None:
        return 'secondary'
    if percent >= 90:
        return 'success'
    if percent >= 85:
        return 'info'
    if percent >= 80:
        return 'primary'
    if percent >= 75:
        return 'warning'
    return 'danger'


def percent_of(grade):
    if grade is None:
        return 0
    return max(0, min(100, int(round(float(grade)))))


def subject_summary(student, school_year=CURRENT_SCHOOL_YEAR, subjects=None):
    """Per-subject grade rows (quarters + average) for one student."""
    queryset_subjects = subjects
    if queryset_subjects is None:
        queryset_subjects = Subject.objects.all()

    grades = Grade.objects.filter(student=student, school_year=school_year).select_related('subject')
    by_subject = {}
    for grade in grades:
        by_subject.setdefault(grade.subject_id, {})[grade.quarter] = grade

    rows = []
    for subject in queryset_subjects.order_by('name'):
        quarter_grades = by_subject.get(subject.pk, {})
        values = [g.final_grade for g in quarter_grades.values() if g.final_grade is not None]
        average = (sum(values) / len(values)).quantize(Decimal('0.01')) if values else None
        latest = quarter_grades.get(max(quarter_grades)) if quarter_grades else None
        rows.append({
            'subject': subject,
            'grades': {q: quarter_grades.get(q) for q in QUARTERS},
            'latest': latest,
            'average': average,
            'percent': percent_of(latest.final_grade if latest else None),
            'rating': descriptive_rating(latest.final_grade if latest else None),
            'bar_class': bar_class(percent_of(latest.final_grade if latest else None)),
            'status': (
                'Pending' if latest is None else ('Passed' if latest.passed else 'Failed')
            ),
        })
    return rows


def overall_average(rows):
    values = [row['average'] for row in rows if row['average'] is not None]
    if not values:
        return None
    return (sum(values) / len(values)).quantize(Decimal('0.01'))


def trend_series(student):
    """Average grade per quarter across the previous and current school year."""
    labels = []
    values = []
    for year, short in (('2025-2026', 'SY 2025-26'), (CURRENT_SCHOOL_YEAR, 'SY 2026-27')):
        for quarter in QUARTERS:
            grades = [
                g.final_grade
                for g in Grade.objects.filter(
                    student=student, school_year=year, quarter=quarter, final_grade__isnull=False,
                )
            ]
            if not grades:
                continue
            labels.append(f'{short} Q{quarter}')
            values.append(float((sum(grades) / len(grades)).quantize(Decimal('0.01'))))
    return {'labels': labels, 'values': values}


def latest_progress_by_subject(student, subjects=None):
    """Latest teacher-written progress note per subject."""
    records = AcademicProgress.objects.filter(student=student).select_related('subject', 'teacher')
    if subjects is not None:
        records = records.filter(subject__in=subjects)
    latest = {}
    for record in records.order_by('-record_date', '-pk'):
        latest.setdefault(record.subject_id, record)
    return list(latest.values())


def progress_groups(student, subjects=None):
    """Split progress notes into the three required sections."""
    records = latest_progress_by_subject(student, subjects)
    return {
        'strengths': [r for r in records if r.strengths],
        'improvements_needed': [r for r in records if r.areas_for_improvement],
        'recent_improvements': [r for r in records if r.recent_improvements],
    }


def assessment_rows(student, subjects=None, limit=None):
    assessments = LearningAssessment.objects.filter(student=student).select_related('subject', 'teacher')
    if subjects is not None:
        assessments = assessments.filter(subject__in=subjects)
    assessments = assessments.order_by('-assessment_date', '-pk')
    if limit:
        assessments = assessments[:limit]
    rows = []
    for assessment in assessments:
        percentage = assessment.get_percentage()
        rows.append({
            'assessment': assessment,
            'percentage': percentage,
            'percent': percent_of(percentage),
            'bar_class': bar_class(percent_of(percentage)),
        })
    return rows


def student_snapshot(student, subjects=None):
    """Everything a student dashboard needs."""
    rows = subject_summary(student, subjects=subjects)
    average = overall_average(rows)
    graded = [row for row in rows if row['latest'] is not None]
    passed = [row for row in graded if row['latest'].passed]
    return {
        'rows': rows,
        'average': average,
        'graded_count': len(graded),
        'passed_count': len(passed),
        'failed_count': len(graded) - len(passed),
        'pending_count': len(rows) - len(graded),
        'percent': percent_of(average),
        'bar_class': bar_class(percent_of(average)),
        'rating': descriptive_rating(average),
        'trend': trend_series(student),
        'progress_groups': progress_groups(student, subjects),
        'assessments': assessment_rows(student, subjects, limit=8),
    }
