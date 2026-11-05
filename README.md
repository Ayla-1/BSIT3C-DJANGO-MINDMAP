# MindMap HS — High School Academic Monitoring System

**Developed by**: Cayao, Kristel Ayla P. / Claro, Asheralyn P. / Fernandez, Wendelyn V.

A Django web application for monitoring high school students' subjects, quarterly grades,
academic performance, learning assessments and learning progress.

## Features

### Administrator
- Manage student records (name, student ID, grade level, section, performance)
- Manage teacher accounts, usernames and passwords
- Manage subjects and assign each subject to one teacher and its sections
- Manage the two high school sections (Section A and Section B)
- Post announcements for everyone, students or teachers
- Overview of teacher loads and class averages

### Teachers
- Personal dashboard listing their own two subjects and students
- Gradebook with bulk entry of Written Work (30%), Performance Task (50%) and
  Quarterly Assessment (20%) scores; the quarter grade and remarks are computed automatically
- Record learning assessments per subject
- Record Strengths, Areas for Improvement and Recent Improvements per student/subject
- Everything is scoped on the server: a teacher can only reach their own subjects and
  the students enrolled in those subjects (foreign records return 404)

### Students
- Personal dashboard with profile, grade level and section
- Grades per subject and quarter with progress bars and a performance trend chart
- Learning assessment results
- Three clearly separated panels: Strengths, Areas for Improvement, Recent Improvements
- Announcements
- Read-only academic records; can change their own password only

## Teacher accounts

| Teacher | Username | Password | Subjects |
| --- | --- | --- | --- |
| Ayla Cayao | `ayla.cayao` | `lala123` | Mathematics, Science |
| Ash Claro | `ash.claro` | `ash123` | English, Filipino |
| Wende Fernandez | `wende.fernandez` | `wen123` | Araling Panlipunan, Edukasyon sa Pagpapakatao |

Other demo accounts:

- **Administrator**: `admin` / `admin123`
- **Students**: student ID as username (e.g. `2026-0001`), password `student123`.
  Section A: `2026-0001`–`2026-0011`, Section B: `2026-0012`–`2026-0022`.

## Technology

- Python 3.13, Django 4.2
- MySQL / MariaDB (XAMPP)
- Bootstrap 5 + custom theme, local ApexCharts for the student charts

## Quick start

1. Start MySQL in XAMPP.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Apply migrations:
   ```bash
   python manage.py migrate
   ```
4. Create the sections, teachers, subjects, students, grades, assessments,
   progress notes and announcements:
   ```bash
   python manage.py seed_highschool
   ```
5. Start the server:
   ```bash
   python manage.py runserver
   ```
6. Open <http://127.0.0.1:8000/> and sign in.

`seed_highschool` is idempotent: running it again restores the demo data set.

## Data model

| Model | Purpose |
| --- | --- |
| `Section` | Section A / Section B, grade level, adviser, room |
| `Teacher` | Teacher record linked one-to-one with a Django user |
| `Student` | Student record linked to a user, with section and grade level |
| `Subject` | Subject handled by exactly one teacher and offered to sections |
| `Grade` | Quarterly grade components, computed quarter grade and remarks |
| `LearningAssessment` | Quiz / activity / performance task / exam results |
| `AcademicProgress` | Strengths, areas for improvement and recent improvements |
| `Announcement` | Notices shown on dashboards |

A student belongs to exactly one section, and the grade level is derived from that section.

## Tests

Permission tests cover teacher/student/admin scoping and grade computation:

```bash
python manage.py test apps.users.tests --settings=mysite.settings_test
```

## Project structure

```
apps/
  core/        # authentication, profile and password page
  users/       # academic models, views, access helpers, analytics, seed command
  info/        # personal info sample app
mysite/        # settings (settings_test.py runs the suite on SQLite)
templates/     # base layout, sidebar partial, role templates
static/        # CSS, JS, vendored ApexCharts
backup/        # legacy college data exported before the conversion
```

## Notes

- Permissions are enforced in the views through `apps/users/access.py`; hiding
  buttons is never the only protection.
- Teacher progress notes are stored per student and subject. The latest note per
  subject is shown on the student dashboard immediately after saving.
- The previous college-based tables were exported to `backup/legacy_college_data.json`
  before being replaced with the high school schema.
