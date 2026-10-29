# Profile Picture Feature Setup Guide

This guide will help you complete the setup for the profile picture management feature.

## Prerequisites

1. **Install Pillow** (required for Django ImageField):
   ```powershell
   pip install Pillow
   ```

## Database Setup

1. **Run SQL Script**:
   - Open phpMyAdmin (http://localhost/phpmyadmin/)
   - Select the `mindmap_db` database
   - Go to the "SQL" tab
   - Copy and paste the contents of `SQL/add_profile_pictures.sql`
   - Click "Go" to execute

   Alternatively, run from command line:
   ```powershell
   cd c:\xampp2\htdocs\BSIT3C-DJANGO-MINDMAP
   mysql -u root -p mindmap_db < SQL\add_profile_pictures.sql
   ```

## Features Added

### For Students:
- **Profile Picture**: Upload and display profile pictures
- **Contact Information**: Phone number and address
- **Guardian Information**: Guardian name and contact number

### For Teachers:
- **Profile Picture**: Upload and display profile pictures
- **Contact Information**: Phone number
- **Professional Details**: Specialization, qualification, and bio

## How to Use

### As Admin:

1. **Edit Student Profile**:
   - Go to Admin Dashboard → Students
   - Click "Edit" button next to a student
   - You'll see the current profile picture (or default avatar)
   - Click "Choose File" to upload a new profile picture
   - Fill in additional fields (phone, address, guardian info)
   - Click "Update Student"

2. **Edit Teacher Profile**:
   - Go to Admin Dashboard → Teachers
   - Click "Edit" button next to a teacher
   - Upload profile picture
   - Add phone, specialization, qualification, and bio
   - Click "Update Teacher"

3. **View Profile Pictures**:
   - Student and teacher lists now show profile pictures in a circular thumbnail
   - Default SVG avatar is shown if no picture is uploaded

## File Storage

- Student profile pictures: `media/students/`
- Teacher profile pictures: `media/teachers/`
- Default avatar: `static/img/default-avatar.svg`

## Recommended Image Format

- **Format**: JPG, PNG, or GIF
- **Size**: Square image, at least 200x200 pixels
- **Max File Size**: 5MB (default Django limit)

## Testing

1. **Test Student Profile Picture Upload**:
   - Login as admin (username: `admin`, password: `admin123`)
   - Navigate to Students → Edit (student ID: 1)
   - Upload a profile picture
   - Verify it displays in the form and in the student list

2. **Test Teacher Profile Picture Upload**:
   - Navigate to Teachers → Edit (teacher: Ayla Kristel)
   - Upload a profile picture
   - Add specialization, qualification, and bio
   - Verify all fields save correctly

3. **Test Default Avatar**:
   - View a student/teacher without a profile picture
   - Verify the default blue avatar SVG displays

## Troubleshooting

### Issue: Images don't upload
- Check that Pillow is installed: `pip list | grep Pillow`
- Verify media directories exist: `media/students/` and `media/teachers/`
- Check file permissions on media directories

### Issue: Images don't display
- Verify `MEDIA_URL` and `MEDIA_ROOT` in `mysite/settings.py`
- Check that `mysite/urls.py` includes static media serving
- Clear browser cache

### Issue: SQL script fails
- Ensure you're connected to the correct database (`mindmap_db`)
- Check that the columns don't already exist
- Verify MySQL is running in XAMPP

## Next Steps

After setup is complete:

1. Test all functionality with sample uploads
2. Consider adding image validation (file size, dimensions)
3. Consider adding image cropping/resizing functionality
4. Add profile picture to student/teacher dashboards
5. Show profile picture in user profile page

## Need Help?

Check these files if you need to modify the feature:
- Models: `apps/users/models.py`
- Views: `apps/users/views.py` (admin_student_edit, admin_teacher_edit)
- Templates: 
  - `templates/users/admin/student_form.html`
  - `templates/users/admin/teacher_form.html`
  - `templates/users/admin/students.html`
  - `templates/users/admin/teachers.html`
