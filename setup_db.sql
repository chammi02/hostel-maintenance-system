CREATE DATABASE IF NOT EXISTS hostel_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE hostel_db;

-- Table 1: users (5 roles: student, warden, worker, admin, guest)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) DEFAULT '',
    password VARCHAR(50) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role ENUM('student', 'warden', 'worker', 'admin', 'guest') NOT NULL,
    worker_trade VARCHAR(50) DEFAULT 'none',
    phone VARCHAR(20),
    room_no VARCHAR(50)
) ENGINE=InnoDB;

-- Table 2: requests (Maintenance Complaints Lifecycle)
CREATE TABLE IF NOT EXISTS requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    student_name VARCHAR(100),
    room_no VARCHAR(50),
    category VARCHAR(50),
    title VARCHAR(150),
    description TEXT,
    photo VARCHAR(255),
    status ENUM('PENDING_REVIEW', 'UNDER_REVIEW', 'ASSIGNED', 'SCHEDULED', 'COMPLETED', 'REJECTED') DEFAULT 'PENDING_REVIEW',
    assigned_worker_id INT NULL,
    worker_name VARCHAR(100) NULL,
    scheduled_date VARCHAR(50) NULL,
    scheduled_time VARCHAR(50) NULL,
    rejection_reason TEXT NULL,
    rating INT NULL,
    student_feedback TEXT NULL,
    completed_at VARCHAR(50) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Ensure columns exist if table was already created
ALTER TABLE users ADD COLUMN IF NOT EXISTS email VARCHAR(100) DEFAULT '' AFTER username;
ALTER TABLE requests ADD COLUMN IF NOT EXISTS rating INT NULL;
ALTER TABLE requests ADD COLUMN IF NOT EXISTS student_feedback TEXT NULL;
ALTER TABLE requests ADD COLUMN IF NOT EXISTS completed_at VARCHAR(50) NULL;

-- Insert seed users if they don't already exist (Default password: 123 or password123)
INSERT INTO users (username, email, password, full_name, role, worker_trade, phone, room_no) VALUES
('kasun', 'kasun@student.ac.lk', '123', 'Kasun Perera (Student)', 'student', 'none', '0771112233', 'U112'),
('student_kasun', 'student@hostel.ac.lk', 'password123', 'Kasun Perera (Student)', 'student', 'none', '0771112233', 'U112'),
('warden', 'warden@hostel.ac.lk', '123', 'Dr. Sunil (Sub Warden)', 'warden', 'none', '0712223344', 'Office'),
('subwarden', 'subwarden@hostel.ac.lk', 'password123', 'Dr. Sunil (Sub Warden)', 'warden', 'none', '0712223344', 'Office'),
('kamal', 'kamal@hostel.ac.lk', '123', 'Kamal Bandara (Electrician)', 'worker', 'electrician', '0763334455', 'Workshop'),
('electrician_kamal', 'electrician@hostel.ac.lk', 'password123', 'Kamal Bandara (Electrician)', 'worker', 'electrician', '0763334455', 'Workshop'),
('nimal', 'nimal@hostel.ac.lk', '123', 'Nimal Silva (Carpenter)', 'worker', 'carpenter', '0754445566', 'Workshop'),
('carpenter_nimal', 'carpenter@hostel.ac.lk', 'password123', 'Nimal Silva (Carpenter)', 'worker', 'carpenter', '0754445566', 'Workshop'),
('saman', 'saman@hostel.ac.lk', '123', 'Saman Kumara (Plumber)', 'worker', 'plumber', '0785556677', 'Workshop'),
('plumber_saman', 'plumber@hostel.ac.lk', 'password123', 'Saman Kumara (Plumber)', 'worker', 'plumber', '0785556677', 'Workshop'),
('admin', 'admin@hostel.ac.lk', '123', 'System Administrator', 'admin', 'none', '0779998877', 'HQ')
ON DUPLICATE KEY UPDATE full_name=VALUES(full_name), worker_trade=VALUES(worker_trade);

-- Insert initial sample requests
INSERT INTO requests (student_id, student_name, room_no, category, title, description, status, assigned_worker_id, worker_name, scheduled_date, scheduled_time) VALUES
(1, 'Kasun Perera (Student)', 'U112', 'electrical', 'Ceiling Fan Sparking & Speed Issue', 'Fan makes sparks and stops rotating on speed 3.', 'SCHEDULED', 3, 'Kamal Bandara (Electrician)', '2026-11-28', '10:00 AM'),
(1, 'Kasun Perera (Student)', 'U112', 'plumbing', 'Bathroom Tap Leaking Continuously', 'Washbasin tap is leaking heavily causing floor overflow.', 'SCHEDULED', 10, 'Saman Kumara (Plumber)', '2026-11-29', '02:00 PM')
ON DUPLICATE KEY UPDATE title=VALUES(title);
