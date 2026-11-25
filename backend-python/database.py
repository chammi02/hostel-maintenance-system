import pymysql
import sqlite3
import os
from config import Config

def get_db_connection():
    """
    Attempts to connect to MySQL first.
    If MySQL is unavailable (e.g. XAMPP not started), falls back to SQLite seamlessly.
    """
    try:
        conn = pymysql.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
        return conn, 'mysql'
    except Exception as e:
        # Fallback to local SQLite for instant presentation and testing
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hostel_local.db')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn, 'sqlite'

def init_db():
    """Initializes tables and seeds initial data if using SQLite or fresh MySQL."""
    conn, engine = get_db_connection()
    cursor = conn.cursor()
    
    if engine == 'sqlite':
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            full_name TEXT NOT NULL,
            phone TEXT,
            hostel_block TEXT,
            room_number TEXT,
            worker_trade TEXT DEFAULT 'none',
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS maintenance_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_code TEXT UNIQUE NOT NULL,
            student_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            location TEXT NOT NULL,
            photo_path TEXT,
            priority TEXT DEFAULT 'medium',
            status TEXT DEFAULT 'PENDING_REVIEW',
            assigned_worker_id INTEGER,
            assigned_by_warden_id INTEGER,
            rejection_reason TEXT,
            scheduled_date TEXT,
            scheduled_time TEXT,
            worker_notes TEXT,
            student_feedback TEXT,
            student_rating INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users(id)
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS hostel_announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            published_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Check if users already seeded
        cursor.execute("SELECT COUNT(*) as count FROM users")
        row = cursor.fetchone()
        count = row['count'] if isinstance(row, dict) else row[0]
        
        if count == 0:
            seed_users = [
                ('admin', 'admin@hostel.ac.lk', 'password123', 'admin', 'System Administrator', '+94 77 111 2233', 'HQ', 'HQ-1', 'none'),
                ('subwarden', 'warden@hostel.ac.lk', 'password123', 'warden', 'Dr. Sunil Perera (Sub Warden)', '+94 71 222 3344', 'Block A', 'W-101', 'none'),
                ('electrician_kamal', 'kamal@hostel.ac.lk', 'password123', 'worker', 'Kamal Bandara (Electrician)', '+94 76 333 4455', 'Maintenance Dept', 'M-01', 'electrician'),
                ('carpenter_nimal', 'nimal@hostel.ac.lk', 'password123', 'worker', 'Nimal Silva (Carpenter)', '+94 75 444 5566', 'Maintenance Dept', 'M-02', 'carpenter'),
                ('plumber_saman', 'saman@hostel.ac.lk', 'password123', 'worker', 'Saman Kumara (Plumber)', '+94 78 555 6677', 'Maintenance Dept', 'M-03', 'plumber'),
                ('student_kasun', 'kasun@student.ac.lk', 'password123', 'student', 'Kasun Jayawardena', '+94 70 666 7788', 'Block G', 'U112', 'none'),
                ('student_amaya', 'amaya@student.ac.lk', 'password123', 'student', 'Amaya Wickramasinghe', '+94 72 777 8899', 'Block A', 'Room D113', 'none'),
                ('guest_user', 'guest@visitor.ac.lk', 'password123', 'guest', 'Guest Visitor / Applicant', '+94 77 888 9900', 'N/A', 'N/A', 'none')
            ]
            cursor.executemany('''
                INSERT INTO users (username, email, password_hash, role, full_name, phone, hostel_block, room_number, worker_trade)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', seed_users)

            seed_requests = [
                ('REQ-2026-001', 6, 'electrical', 'Ceiling Fan Not Working & Sparking', 'The ceiling fan regulator gives sparks when turned to speed 3 and does not rotate at all.', 'Block A, 2nd Floor, Room 204', None, 'high', 'SCHEDULED', 3, 2, None, '2026-10-30', '10:00 AM - 11:30 AM', 'Will bring a replacement capacitor and tester.'),
                ('REQ-2026-002', 6, 'carpentry', 'Broken Study Table Drawer & Lock', 'The wooden drawer is stuck and the lock mechanism is broken.', 'Block A, 2nd Floor, Room 204', None, 'medium', 'ASSIGNED', 4, 2, None, None, None, None),
                ('REQ-2026-003', 7, 'plumbing', 'Water Tap Leaking in Bathroom', 'Continuous water leakage from wash basin tap causing floor flooding.', 'Block B, 1st Floor, Room 112', None, 'medium', 'UNDER_REVIEW', None, 2, None, None, None, None),
                ('REQ-2026-004', 7, 'furniture', 'Personal AC Installation Request', 'Student requested unauthorized AC unit repair.', 'Block B, 1st Floor, Room 112', None, 'low', 'REJECTED', None, 2, 'Air conditioning units are not permitted in standard hostel rooms per hostel rule 4.2.', None, None, None),
                ('REQ-2026-005', 6, 'electrical', 'Fluorescent Tube Light Blinking', 'Tube light in study corner keeps flickering continuously.', 'Block A, 2nd Floor, Room 204', None, 'low', 'PENDING_REVIEW', None, None, None, None, None, None)
            ]
            cursor.executemany('''
                INSERT INTO maintenance_requests (request_code, student_id, category, title, description, location, photo_path, priority, status, assigned_worker_id, assigned_by_warden_id, rejection_reason, scheduled_date, scheduled_time, worker_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', seed_requests)

            cursor.execute('''
                INSERT INTO hostel_announcements (title, content, published_by)
                VALUES 
                ('Hostel Maintenance Portal Live', 'Welcome to the automated hostel maintenance system.', 1),
                ('Electrical Inspection Notice', 'Routine checks on Block A & B next week.', 2)
            ''')
            conn.commit()
    conn.close()
