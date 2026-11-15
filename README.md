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

  MINDMAP: A STUDENT ACADEMIC PROGRESS MONITORING SYSTEM

INTRODUCTION
Background of the Project
Monitoring students' academic performance will play an important role in identifying their strengths, weaknesses, and areas that need improvement. In many high schools, teachers will still rely on manual records, spreadsheets, and traditional methods to monitor and evaluate student performance. These methods may make it difficult to organize academic information, track individual progress, and maintain updated performance records.
To address these challenges, the proposed project will focus on developing MindMap: A Student Academic Progress Monitoring System, a web-based application designed to help teachers monitor and manage the academic progress of high school students. The system will provide a centralized platform where teachers will be able to record and update students' academic performance, including their strengths, areas for improvement, and recent improvements.
The system will also provide individual teacher accounts, allowing each teacher to access and manage only their assigned subjects and student performance records. Through this proposed system, academic information will be organized and accessible, making student progress monitoring more efficient and systematic.

STATEMENT OF THE PROBLEM OR PROJECT OBJECTIVES
The main objective of this project will be to design and develop a web-based Student Academic Progress Monitoring System that will help high school teachers record, manage, and monitor students' academic performance, strengths, and areas that need improvement.
Specifically, the project will aim to accomplish the following objectives:
1.	Develop a student information management module that will store and organize students' personal and academic information.
2.	Implement a teacher account management module that will allow three teachers to have individual accounts and dashboards.
3.	Develop a subject management feature that will allow teachers to access and manage their assigned subjects, including Mathematics, Science, English, Filipino, Araling Panlipunan, and Edukasyon sa Pagpapakatao (ESP).
4.	Implement an academic performance monitoring module that will allow teachers to record and update students' strengths, areas for improvement, and recent improvements.
5.	Develop a centralized monitoring dashboard that will allow the administrator to manage student records, teacher accounts, subjects, and academic information.

SIGNIFICANCE OF THE PROJECT
The proposed system will provide practical benefits to the following beneficiaries:
High School Teachers: The system will help teachers record, update, and monitor students' academic performance. It will also allow them to identify students' strengths and areas that need improvement in their assigned subjects.
High School Students: The system will help students become more aware of their academic performance, strengths, weaknesses, and improvements. It will encourage them to recognize the areas where they need to focus more.
School Administrators: The system will provide an organized platform for managing teacher accounts, student information, subject assignments, and academic progress records.

ALIGNMENT WITH INSTITUTIONAL RESEARCH AGENDA AND SUSTAINABLE DEVELOPMENT GOALS
Institutional Research Agenda Alignment: The proposed project will align with the Institutional Information Technology and Educational Technology Research priorities by using web-based technologies to improve academic record management and student progress monitoring.
Sustainable Development Goal Alignment:
Quality Education: The system will support quality education by providing teachers with a tool to monitor student performance, recognize learning difficulties, and identify areas that require improvement.
Industry, Innovation, and Infrastructure: The project will contribute to technological innovation in educational institutions through the development of a web-based academic monitoring platform.
Peace, Justice, and Strong Institutions: The system will promote organized and responsible management of academic information through controlled user access and systematic record-keeping.

SCOPE AND LIMITATIONS
System Scope & Technical Architecture
The proposed system will be designed to support the monitoring and management of high school students' academic progress. It will provide separate accounts for teachers and administrators to ensure that users will only access the features and information assigned to their respective roles.
Component	Description & Coverage
Student Information Management	The system will store and manage students' personal information, grade level, section, and academic records.
Teacher Account Management	The system will provide three individual teacher accounts, each with a separate dashboard.
Subject Management	Each teacher will be assigned two subjects from Mathematics, Science, English, Filipino, Araling Panlipunan, and ESP.
Academic Performance Monitoring	Teachers will be able to record and update students' strengths, areas for improvement, and recent improvements in their assigned subjects.
Administrator Dashboard	The administrator will manage teacher accounts, student records, subject assignments, and overall system information.
Progress Monitoring	The system will organize academic progress records to help teachers monitor students' development over time.

Technology Stack
The proposed system will utilize the following technologies:
Technology	Purpose
Python	Main programming language
Django	Backend web framework
MySQL	Relational database management
HTML5	Webpage structure
CSS3	Website styling
JavaScript	Interactive website features
Bootstrap	Responsive user interface
Visual Studio Code	Development environment

Target Users
The proposed system will have the following target users:
1.	Administrator – Will manage the overall system, student information, teacher accounts, and subject assignments.
2.	Teachers – Three teachers will have their own accounts and dashboards. Each teacher will manage two assigned subjects and will be responsible for recording and updating the academic performance of their students.
3.	High School Students – Their academic information and progress will be monitored through the system. They will serve as the primary subjects of academic performance monitoring.
Limitations
The proposed system will have the following limitations:
1.	The system will primarily focus on monitoring high school students' academic performance and progress.
2.	The system will support only three teacher accounts during the initial development phase.
3.	Each teacher will be assigned only two subjects from the six selected subjects.
4.	Teachers will only be allowed to manage academic records under their assigned subjects.
5.	The system will focus on recording strengths, areas for improvement, and recent improvements rather than providing automated psychological or intelligence assessments.
6.	The system will require an internet connection or access to the local network, depending on its deployment setup.
7.	Online payment, SMS notifications, and integration with external school management systems will not be included in the initial development phase.
