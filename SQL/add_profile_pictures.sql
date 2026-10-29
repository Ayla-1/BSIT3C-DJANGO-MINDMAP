-- SQL to add profile picture and additional fields to students and teachers tables

-- Add columns to students table
ALTER TABLE students 
ADD COLUMN profile_picture VARCHAR(255) NULL AFTER enrollment_date,
ADD COLUMN phone VARCHAR(20) NULL AFTER profile_picture,
ADD COLUMN address TEXT NULL AFTER phone,
ADD COLUMN guardian_name VARCHAR(200) NULL AFTER address,
ADD COLUMN guardian_contact VARCHAR(20) NULL AFTER guardian_name;

-- Add columns to teachers table
ALTER TABLE teachers 
ADD COLUMN profile_picture VARCHAR(255) NULL AFTER department,
ADD COLUMN phone VARCHAR(20) NULL AFTER profile_picture,
ADD COLUMN specialization VARCHAR(200) NULL AFTER phone,
ADD COLUMN qualification VARCHAR(200) NULL AFTER specialization,
ADD COLUMN bio TEXT NULL AFTER qualification;

-- Create media directories (Note: This needs to be done manually or via Python)
-- mkdir media
-- mkdir media/students
-- mkdir media/teachers
