-- SQL to create attendance table

CREATE TABLE IF NOT EXISTS users_attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id BIGINT NOT NULL,
    subject_id BIGINT NOT NULL,
    teacher_id BIGINT NULL,
    date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'Present',
    notes TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_attendance (student_id, subject_id, date),
    FOREIGN KEY (student_id) REFERENCES users_student(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES users_subject(id) ON DELETE CASCADE,
    FOREIGN KEY (teacher_id) REFERENCES users_teacher(id) ON DELETE SET NULL,
    INDEX idx_student (student_id),
    INDEX idx_subject (subject_id),
    INDEX idx_date (date),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Add some comments
ALTER TABLE users_attendance 
    COMMENT = 'Daily student attendance records for each subject';
