from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.core.models import UserProfile

from .models import (
    AcademicProgress,
    Announcement,
    Grade,
    LearningAssessment,
    Section,
    Student,
    Subject,
    Teacher,
)


def make_user(username, role, password='testpass123', **extra):
    user = User.objects.create_user(username=username, password=password, **extra)
    UserProfile.objects.create(user=user, role=role)
    return user


class BaseSchoolData(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.section_a = Section.objects.create(name='Section A', code='A', grade_level='Grade 11')
        cls.section_b = Section.objects.create(name='Section B', code='B', grade_level='Grade 11')

        cls.ayla_user = make_user('ayla.cayao', 'teacher', password='lala123', first_name='Ayla', last_name='Cayao')
        cls.ash_user = make_user('ash.claro', 'teacher', password='ash123', first_name='Ash', last_name='Claro')
        cls.ayla = Teacher.objects.create(
            user=cls.ayla_user, first_name='Ayla', last_name='Cayao', email='ayla@example.com',
        )
        cls.ash = Teacher.objects.create(
            user=cls.ash_user, first_name='Ash', last_name='Claro', email='ash@example.com',
        )

        cls.math = Subject.objects.create(code='MATH', name='Mathematics', teacher=cls.ayla)
        cls.math.sections.set([cls.section_a])
        cls.science = Subject.objects.create(code='SCI', name='Science', teacher=cls.ayla)
        cls.science.sections.set([cls.section_a])
        cls.english = Subject.objects.create(code='ENG', name='English', teacher=cls.ash)
        cls.english.sections.set([cls.section_b])

        cls.student_a_user = make_user('2026-0001', 'student', password='student123', first_name='Juan', last_name='Dela Cruz')
        cls.student_a = Student.objects.create(
            user=cls.student_a_user, student_number='2026-0001', first_name='Juan', last_name='Dela Cruz',
            section=cls.section_a,
        )
        cls.student_b_user = make_user('2026-0012', 'student', password='student123', first_name='Jasmine', last_name='Lim')
        cls.student_b = Student.objects.create(
            user=cls.student_b_user, student_number='2026-0012', first_name='Jasmine', last_name='Lim',
            section=cls.section_b,
        )

        cls.admin_user = make_user('admin', 'admin', password='admin123', is_staff=True, is_superuser=True)

        cls.ash_progress = AcademicProgress.objects.create(
            student=cls.student_b,
            subject=cls.english,
            teacher=cls.ash,
            record_date=date(2026, 10, 1),
            strengths='Reads fluently.',
            areas_for_improvement='Needs more practice in grammar.',
            recent_improvements='Improved essay scores.',
            status='Improving',
        )


class GradeModelTests(BaseSchoolData):
    def test_weighted_grade_and_remarks(self):
        grade = Grade(student=self.student_a, subject=self.math, quarter=1, written_work=90, performance_task=80, quarterly_assessment=70)
        grade.save()
        # 90*0.3 + 80*0.5 + 70*0.2 = 27 + 40 + 14 = 81
        self.assertEqual(grade.final_grade, Decimal('81.00'))
        self.assertEqual(grade.remarks, 'PASSED')

    def test_failing_grade_remarks(self):
        grade = Grade(student=self.student_a, subject=self.math, quarter=2, written_work=70, performance_task=70, quarterly_assessment=70)
        grade.save()
        self.assertEqual(grade.remarks, 'FAILED')

    def test_student_grade_level_follows_section(self):
        self.assertEqual(self.student_a.grade_level, 'Grade 11')


class TeacherPermissionTests(BaseSchoolData):
    def test_teacher_dashboard_requires_teacher_role(self):
        self.client.force_login(self.student_a_user)
        response = self.client.get(reverse('teacher_dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_teacher_sees_only_students_in_own_sections(self):
        self.client.force_login(self.ayla_user)
        response = self.client.get(reverse('teacher_students'))
        self.assertContains(response, 'Juan Dela Cruz')
        # Jasmine only takes English (Ash's subject), so she is not Ayla's student.
        self.assertNotContains(response, 'Jasmine Lim')

    def test_teacher_cannot_open_student_outside_assignment(self):
        self.client.force_login(self.ayla_user)
        response = self.client.get(reverse('teacher_student_detail', args=[self.student_b.pk]))
        self.assertEqual(response.status_code, 404)

    def test_teacher_cannot_open_other_teachers_subject_gradebook(self):
        self.client.force_login(self.ayla_user)
        response = self.client.get(reverse('teacher_gradebook'), {'subject': self.english.pk})
        self.assertEqual(response.status_code, 404)

    def test_teacher_cannot_submit_grades_for_foreign_subject(self):
        self.client.force_login(self.ayla_user)
        response = self.client.post(reverse('teacher_gradebook'), {
            'subject': self.english.pk,
            'section': self.section_b.pk,
            'quarter': 1,
            'school_year': '2026-2027',
            f'ww_{self.student_b.pk}': 95,
            f'pt_{self.student_b.pk}': 95,
            f'qa_{self.student_b.pk}': 95,
        })
        self.assertEqual(response.status_code, 404)
        self.assertFalse(Grade.objects.filter(student=self.student_b, subject=self.english).exists())

    def test_teacher_can_save_grades_for_own_subject(self):
        self.client.force_login(self.ayla_user)
        response = self.client.post(reverse('teacher_gradebook'), {
            'subject': self.math.pk,
            'section': self.section_a.pk,
            'quarter': 1,
            'school_year': '2026-2027',
            f'ww_{self.student_a.pk}': '90',
            f'pt_{self.student_a.pk}': '85',
            f'qa_{self.student_a.pk}': '80',
        })
        self.assertEqual(response.status_code, 302)
        grade = Grade.objects.get(student=self.student_a, subject=self.math, quarter=1)
        self.assertEqual(grade.final_grade, Decimal('85.50'))
        self.assertEqual(grade.recorded_by, self.ayla)

    def test_teacher_cannot_create_progress_for_foreign_subject(self):
        self.client.force_login(self.ayla_user)
        response = self.client.post(reverse('teacher_progress_create'), {
            'subject': self.english.pk,
            'student': self.student_b.pk,
            'record_date': '2026-10-20',
            'strengths': 'x',
            'areas_for_improvement': 'y',
            'recent_improvements': 'z',
            'status': 'Improving',
        })
        self.assertEqual(response.status_code, 404)
        self.assertEqual(AcademicProgress.objects.filter(subject=self.english).count(), 1)

    def test_teacher_cannot_edit_other_teachers_progress(self):
        self.client.force_login(self.ayla_user)
        response = self.client.get(reverse('teacher_progress_edit', args=[self.ash_progress.pk]))
        self.assertEqual(response.status_code, 404)

    def test_teacher_progress_update_is_visible_on_student_dashboard(self):
        self.client.force_login(self.ayla_user)
        response = self.client.post(reverse('teacher_progress_create'), {
            'subject': self.math.pk,
            'student': self.student_a.pk,
            'record_date': '2026-10-20',
            'strengths': 'Strong algebra skills.',
            'areas_for_improvement': 'Practice geometry proofs.',
            'recent_improvements': 'Quiz scores improved by 8 points.',
            'status': 'Improving',
        })
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.student_a_user)
        dashboard = self.client.get(reverse('student_dashboard'))
        self.assertContains(dashboard, 'Strong algebra skills.')
        self.assertContains(dashboard, 'Practice geometry proofs.')
        self.assertContains(dashboard, 'Quiz scores improved by 8 points.')


class StudentPermissionTests(BaseSchoolData):
    def test_student_dashboard_only_shows_own_records(self):
        self.client.force_login(self.student_a_user)
        response = self.client.get(reverse('student_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Jasmine Lim')

    def test_student_cannot_access_admin_pages(self):
        self.client.force_login(self.student_a_user)
        for url in ['admin_dashboard', 'admin_students', 'admin_teachers', 'admin_subjects', 'admin_sections']:
            response = self.client.get(reverse(url))
            self.assertEqual(response.status_code, 302, url)

    def test_student_cannot_create_progress_records(self):
        self.client.force_login(self.student_a_user)
        before = AcademicProgress.objects.count()
        response = self.client.post(reverse('teacher_progress_create'), {
            'subject': self.math.pk,
            'student': self.student_a.pk,
            'record_date': '2026-10-20',
            'strengths': 'self written',
            'areas_for_improvement': 'self written',
            'recent_improvements': 'self written',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(AcademicProgress.objects.count(), before)

    def test_student_can_change_own_password(self):
        self.client.force_login(self.student_a_user)
        response = self.client.post(reverse('user_profile'), {
            'action': 'change_password',
            'current_password': 'student123',
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123',
        })
        self.assertEqual(response.status_code, 302)
        self.student_a_user.refresh_from_db()
        self.assertTrue(self.student_a_user.check_password('newpassword123'))

    def test_student_cannot_change_password_without_current_password(self):
        self.client.force_login(self.student_a_user)
        self.client.post(reverse('user_profile'), {
            'action': 'change_password',
            'current_password': 'wrong',
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123',
        })
        self.student_a_user.refresh_from_db()
        self.assertTrue(self.student_a_user.check_password('student123'))

    def test_teacher_cannot_read_student_dashboard(self):
        self.client.force_login(self.ayla_user)
        response = self.client.get(reverse('student_dashboard'))
        self.assertEqual(response.status_code, 302)


class AdminPermissionTests(BaseSchoolData):
    def test_admin_can_open_management_pages(self):
        self.client.force_login(self.admin_user)
        for url in [
            'admin_dashboard', 'admin_students', 'admin_teachers', 'admin_subjects',
            'admin_sections', 'admin_announcements', 'admin_assignments',
        ]:
            response = self.client.get(reverse(url))
            self.assertEqual(response.status_code, 200, url)

    def test_teacher_cannot_open_admin_pages(self):
        self.client.force_login(self.ayla_user)
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_admin_can_create_section_and_teacher(self):
        self.client.force_login(self.admin_user)
        response = self.client.post(reverse('admin_teacher_create'), {
            'username': 'wende.fernandez',
            'password': 'wen123',
            'first_name': 'Wende',
            'last_name': 'Fernandez',
            'email': 'wende@example.com',
            'department': 'Social Sciences',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Teacher.objects.filter(email='wende@example.com').exists())

    def test_admin_can_post_announcement_visible_to_students(self):
        self.client.force_login(self.admin_user)
        self.client.post(reverse('admin_announcement_create'), {
            'title': 'Quarter 2 begins',
            'body': 'Classes resume on Monday.',
            'audience': 'students',
        })
        self.assertTrue(Announcement.objects.filter(title='Quarter 2 begins').exists())

        self.client.force_login(self.student_a_user)
        response = self.client.get(reverse('student_dashboard'))
        self.assertContains(response, 'Quarter 2 begins')
