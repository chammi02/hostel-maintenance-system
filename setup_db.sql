CREATE DATABASE IF NOT EXISTS hostel_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE hostel_db;

-- Table 1: users
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(50) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role ENUM('student', 'warden', 'worker', 'admin', 'guest') NOT NULL,
    worker_trade VARCHAR(50) DEFAULT 'none',
    phone VARCHAR(20),
    room_no VARCHAR(50)
) ENGINE=InnoDB;

-- Table 2: requests
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Insert seed users if they don't already exist
INSERT INTO users (username, password, full_name, role, worker_trade, phone, room_no) VALUES
('kasun', '123', 'Kasun Perera (Student)', 'student', 'none', '0771112233', 'Room 204'),
('student_kasun', 'password123', 'Kasun Perera (Student)', 'student', 'none', '0771112233', 'Room 204'),
('warden', '123', 'Dr. Sunil (Sub Warden)', 'warden', 'none', '0712223344', 'Office'),
('subwarden', 'password123', 'Dr. Sunil (Sub Warden)', 'warden', 'none', '0712223344', 'Office'),
('kamal', '123', 'Kamal Bandara (Electrician)', 'worker', 'electrician', '0763334455', 'Workshop'),
('electrician_kamal', 'password123', 'Kamal Bandara (Electrician)', 'worker', 'electrician', '0763334455', 'Workshop'),
('nimal', '123', 'Nimal Silva (Carpenter)', 'worker', 'carpenter', '0754445566', 'Workshop'),
('carpenter_nimal', 'password123', 'Nimal Silva (Carpenter)', 'worker', 'carpenter', '0754445566', 'Workshop'),
('saman', '123', 'Saman Kumara (Plumber)', 'worker', 'plumber', '0785556677', 'Workshop'),
('plumber_saman', 'password123', 'Saman Kumara (Plumber)', 'worker', 'plumber', '0785556677', 'Workshop'),
('admin', '123', 'System Administrator', 'admin', 'none', '0779998877', 'HQ'),
('guest', '123', 'Guest Visitor', 'guest', 'none', '0700000000', 'None'),
('guest_user', 'password123', 'Guest Visitor', 'guest', 'none', '0700000000', 'None')
ON DUPLICATE KEY UPDATE full_name=VALUES(full_name);

-- Insert initial sample request
INSERT INTO requests (student_id, student_name, room_no, category, title, description, status, assigned_worker_id, worker_name, scheduled_date, scheduled_time) VALUES
(1, 'Kasun Perera (Student)', 'Room 204', 'electrical', 'Ceiling Fan Sparking & Speed Issue', 'Fan makes sparks and stops rotating on speed 3.', 'SCHEDULED', 3, 'Kamal Bandara (Electrician)', '2026-11-05', '10:00 AM');
