-- =====================================================================
-- Hostel Maintenance Request Management System - Database Schema (MySQL)
-- Designed for Final Year Academic Project
-- Complies with Activity Diagram, Swimlanes, and State Transition Model
-- =====================================================================

DROP DATABASE IF EXISTS hostel_maintenance_db;
CREATE DATABASE hostel_maintenance_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE hostel_maintenance_db;

-- ---------------------------------------------------------------------
-- Table 1: users
-- Stores all 5 system roles: student, warden, worker, admin, guest
-- ---------------------------------------------------------------------
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('student', 'warden', 'worker', 'admin', 'guest') NOT NULL DEFAULT 'guest',
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NULL,
    hostel_block VARCHAR(20) NULL,      -- e.g., 'Block A', 'Block B'
    room_number VARCHAR(20) NULL,       -- e.g., 'Room 204'
    worker_trade ENUM('electrician', 'carpenter', 'plumber', 'mason', 'general', 'none') DEFAULT 'none',
    status ENUM('active', 'inactive', 'pending_approval') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Table 2: maintenance_requests
-- Core entity tracking the entire lifecycle from state diagram:
-- PENDING_REVIEW -> UNDER_REVIEW -> ASSIGNED -> SCHEDULED -> COMPLETED (or REJECTED)
-- ---------------------------------------------------------------------
CREATE TABLE maintenance_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    request_code VARCHAR(30) UNIQUE NOT NULL, -- e.g., 'REQ-2026-001'
    student_id INT NOT NULL,
    category ENUM('electrical', 'carpentry', 'plumbing', 'masonry', 'furniture', 'other') NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    location VARCHAR(100) NOT NULL,            -- e.g., 'Block A, 2nd Floor, Room 204'
    photo_path VARCHAR(255) NULL,             -- Path to uploaded problem photo
    priority ENUM('low', 'medium', 'high', 'emergency') DEFAULT 'medium',
    status ENUM(
        'PENDING_REVIEW',
        'UNDER_REVIEW',
        'ASSIGNED',
        'SCHEDULED',
        'IN_PROGRESS',
        'COMPLETED',
        'REJECTED'
    ) NOT NULL DEFAULT 'PENDING_REVIEW',
    assigned_worker_id INT NULL,
    assigned_by_warden_id INT NULL,
    rejection_reason TEXT NULL,
    scheduled_date DATE NULL,
    scheduled_time VARCHAR(50) NULL,          -- e.g., '10:00 AM - 12:00 PM'
    worker_notes TEXT NULL,
    student_feedback TEXT NULL,
    student_rating INT NULL CHECK (student_rating BETWEEN 1 AND 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_at TIMESTAMP NULL,
    scheduled_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_req_student FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_req_worker FOREIGN KEY (assigned_worker_id) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT fk_req_warden FOREIGN KEY (assigned_by_warden_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Table 3: request_status_history (Audit Trail for State Transitions)
-- Logs every transition depicted in the State Machine Diagram
-- ---------------------------------------------------------------------
CREATE TABLE request_status_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    request_id INT NOT NULL,
    previous_status VARCHAR(50) NULL,
    new_status VARCHAR(50) NOT NULL,
    changed_by_user_id INT NOT NULL,
    remarks TEXT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_history_request FOREIGN KEY (request_id) REFERENCES maintenance_requests(id) ON DELETE CASCADE,
    CONSTRAINT fk_history_user FOREIGN KEY (changed_by_user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Table 4: hostel_announcements
-- Visible to Guest Users and all hostel residents
-- ---------------------------------------------------------------------
CREATE TABLE hostel_announcements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    content TEXT NOT NULL,
    published_by INT NOT NULL,
    is_public BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_announcement_user FOREIGN KEY (published_by) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- =====================================================================
-- SEED DATA (Ready for Demo and Viva Testing)
-- Default Password for all demo accounts: 'password123'
-- (PBKDF2/SHA256 representation or plain-text mock for quick testing)
-- =====================================================================

INSERT INTO users (id, username, email, password_hash, role, full_name, phone, hostel_block, room_number, worker_trade, status) VALUES
(1, 'admin', 'admin@hostel.ac.lk', 'password123', 'admin', 'System Administrator', '+94 77 111 2233', 'Admin Office', 'HQ-1', 'none', 'active'),
(2, 'subwarden', 'warden@hostel.ac.lk', 'password123', 'warden', 'Dr. Sunil Perera (Sub Warden)', '+94 71 222 3344', 'Block A', 'W-101', 'none', 'active'),
(3, 'electrician_kamal', 'kamal@hostel.ac.lk', 'password123', 'worker', 'Kamal Bandara (Electrician)', '+94 76 333 4455', 'Maintenance Dept', 'M-01', 'electrician', 'active'),
(4, 'carpenter_nimal', 'nimal@hostel.ac.lk', 'password123', 'worker', 'Nimal Silva (Carpenter)', '+94 75 444 5566', 'Maintenance Dept', 'M-02', 'carpenter', 'active'),
(5, 'plumber_saman', 'saman@hostel.ac.lk', 'password123', 'worker', 'Saman Kumara (Plumber)', '+94 78 555 6677', 'Maintenance Dept', 'M-03', 'plumber', 'active'),
(6, 'student_kasun', 'kasun@student.ac.lk', 'password123', 'student', 'Kasun Jayawardena', '+94 70 666 7788', 'Block G', 'U112', 'none', 'active'),
(7, 'student_amaya', 'amaya@student.ac.lk', 'password123', 'student', 'Amaya Wickramasinghe', '+94 72 777 8899', 'Block A', 'D113', 'none', 'active'),
(8, 'guest_user', 'guest@visitor.ac.lk', 'password123', 'guest', 'Guest Visitor / Applicant', '+94 77 888 9900', 'N/A', 'N/A', 'none', 'active');

-- Sample Initial Maintenance Requests matching each state
INSERT INTO maintenance_requests (id, request_code, student_id, category, title, description, location, photo_path, priority, status, assigned_worker_id, assigned_by_warden_id, rejection_reason, scheduled_date, scheduled_time, worker_notes) VALUES
(1, 'REQ-2026-001', 6, 'electrical', 'Ceiling Fan Not Working & Sparking', 'The ceiling fan regulator gives sparks when turned to speed 3 and does not rotate at all.', 'Block A, 2nd Floor, Room 204', 'uploads/sample_fan.jpg', 'high', 'SCHEDULED', 3, 2, NULL, '2026-10-30', '10:00 AM - 11:30 AM', 'Will bring a replacement capacitor and tester.'),
(2, 'REQ-2026-002', 6, 'carpentry', 'Broken Study Table Drawer & Lock', 'The wooden drawer is stuck and the lock mechanism is broken.', 'Block A, 2nd Floor, Room 204', 'uploads/sample_table.jpg', 'medium', 'ASSIGNED', 4, 2, NULL, NULL, NULL, NULL),
(3, 'REQ-2026-003', 7, 'plumbing', 'Water Tap Leaking in Bathroom', 'Continuous water leakage from wash basin tap causing floor flooding.', 'Block B, 1st Floor, Room 112', 'uploads/sample_tap.jpg', 'medium', 'UNDER_REVIEW', NULL, 2, NULL, NULL, NULL, NULL),
(4, 'REQ-2026-004', 7, 'furniture', 'Personal AC Installation Request', 'Student requested unauthorized AC unit repair.', 'Block B, 1st Floor, Room 112', NULL, 'low', 'REJECTED', NULL, 2, 'Air conditioning units are not permitted in standard hostel rooms per hostel rule 4.2.', NULL, NULL, NULL),
(5, 'REQ-2026-005', 6, 'electrical', 'Fluorescent Tube Light Blinking', 'Tube light in study corner keeps flickering continuously.', 'Block A, 2nd Floor, Room 204', NULL, 'low', 'PENDING_REVIEW', NULL, NULL, NULL, NULL, NULL, NULL);

-- Initial Announcements for Guest Portal
INSERT INTO hostel_announcements (title, content, published_by, is_public) VALUES
('Hostel Maintenance Portal Live', 'Welcome to the new Automated Hostel Maintenance Management System. Students can submit requests with photos.', 1, TRUE),
('Routine Electrical Inspection Notice', 'Annual hostel electrical grid inspection will be conducted between 1st and 5th of next month.', 2, TRUE),
('Emergency Repairs Helpline', 'For urgent midnight water burst or short-circuit emergencies, contact the Warden desk directly.', 2, TRUE);
