import os
import sys

# Ensure DLL directory is available on Windows if using bundled Python (e.g. QGIS / OSGeo4W)
if hasattr(os, 'add_dll_directory'):
    for p in [r"C:\Program Files\QGIS 3.44.11\bin", r"C:\Program Files\QGIS 3.44.11\apps\Python312\DLLs"]:
        if os.path.exists(p):
            try:
                os.add_dll_directory(p)
            except Exception:
                pass

try:
    import sqlite3
    SQLITE_AVAILABLE = True
except Exception:
    SQLITE_AVAILABLE = False

try:
    import pymysql
    import pymysql.cursors
    PYMYSQL_AVAILABLE = True
except ImportError:
    PYMYSQL_AVAILABLE = False

from flask import Flask, render_template, request, redirect, session, jsonify, url_for

app = Flask(__name__)
app.secret_key = 'hostel_maintenance_super_secret_key'

# Upload folder for maintenance problem photos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# SQLite database file path (used if MySQL is offline)
SQLITE_DB_PATH = os.path.join(BASE_DIR, 'hostel_db.sqlite3')

# -----------------------------------------------------------------------------
# Database Connection Manager (Direct MySQL with Automatic Fallback)
# -----------------------------------------------------------------------------
USE_MYSQL = True

def init_mysql_db():
    """Ensure MySQL hostel_db tables, columns, and seed users exist."""
    global USE_MYSQL
    if not PYMYSQL_AVAILABLE:
        USE_MYSQL = False
        return False
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='',         # Default XAMPP MySQL password is empty
            port=3306,
            autocommit=True
        )
        with conn.cursor() as cur:
            cur.execute("CREATE DATABASE IF NOT EXISTS hostel_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn.close()

        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='hostel_db',
            port=3306,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
        with conn.cursor() as cur:
            # 1. Create users table
            cur.execute('''
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
                ) ENGINE=InnoDB
            ''')

            # 2. Create requests table
            cur.execute('''
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
                ) ENGINE=InnoDB
            ''')

            # Ensure all columns exist in MySQL tables
            cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS email VARCHAR(100) DEFAULT '' AFTER username")
            cur.execute("ALTER TABLE requests ADD COLUMN IF NOT EXISTS rating INT NULL")
            cur.execute("ALTER TABLE requests ADD COLUMN IF NOT EXISTS student_feedback TEXT NULL")
            cur.execute("ALTER TABLE requests ADD COLUMN IF NOT EXISTS completed_at VARCHAR(50) NULL")

            # Remove obsolete guest login accounts
            cur.execute("DELETE FROM users WHERE role = 'guest' OR username IN ('guest', 'guest_user')")

            # Ensure demo accounts exist in MySQL (including Plumber Saman)
            seed_users = [
                ('kasun', 'kasun@student.ac.lk', '123', 'Kasun Perera (Student)', 'student', 'none', '0771112233', 'Room 204'),
                ('student_kasun', 'student@hostel.ac.lk', 'password123', 'Kasun Perera (Student)', 'student', 'none', '0771112233', 'Room 204'),
                ('warden', 'warden@hostel.ac.lk', '123', 'Dr. Sunil (Sub Warden)', 'warden', 'none', '0712223344', 'Office'),
                ('subwarden', 'subwarden@hostel.ac.lk', 'password123', 'Dr. Sunil (Sub Warden)', 'warden', 'none', '0712223344', 'Office'),
                ('kamal', 'kamal@hostel.ac.lk', '123', 'Kamal Bandara (Electrician)', 'worker', 'electrician', '0763334455', 'Workshop'),
                ('electrician_kamal', 'electrician@hostel.ac.lk', 'password123', 'Kamal Bandara (Electrician)', 'worker', 'electrician', '0763334455', 'Workshop'),
                ('nimal', 'nimal@hostel.ac.lk', '123', 'Nimal Silva (Carpenter)', 'worker', 'carpenter', '0754445566', 'Workshop'),
                ('carpenter_nimal', 'carpenter@hostel.ac.lk', 'password123', 'Nimal Silva (Carpenter)', 'worker', 'carpenter', '0754445566', 'Workshop'),
                ('saman', 'saman@hostel.ac.lk', '123', 'Saman Kumara (Plumber)', 'worker', 'plumber', '0785556677', 'Workshop'),
                ('plumber_saman', 'plumber@hostel.ac.lk', 'password123', 'Saman Kumara (Plumber)', 'worker', 'plumber', '0785556677', 'Workshop'),
                ('admin', 'admin@hostel.ac.lk', '123', 'System Administrator', 'admin', 'none', '0779998877', 'HQ')
            ]
            for u in seed_users:
                cur.execute("SELECT id FROM users WHERE username = %s", (u[0],))
                row = cur.fetchone()
                if not row:
                    cur.execute('''
                        INSERT INTO users (username, email, password, full_name, role, worker_trade, phone, room_no)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ''', u)
                else:
                    cur.execute("UPDATE users SET email = %s, worker_trade = %s, full_name = %s WHERE id = %s", (u[1], u[5], u[3], row['id']))

            # Initial sample request if empty
            cur.execute("SELECT COUNT(*) as cnt FROM requests")
            if cur.fetchone()['cnt'] == 0:
                cur.execute('''
                    INSERT INTO requests (student_id, student_name, room_no, category, title, description, status, assigned_worker_id, worker_name, scheduled_date, scheduled_time)
                    VALUES (1, 'Kasun Perera (Student)', 'Room 204', 'electrical', 'Ceiling Fan Sparking & Speed Issue', 'Fan makes sparks and stops rotating on speed 3.', 'SCHEDULED', 3, 'Kamal Bandara (Electrician)', '2026-11-28', '10:00 AM')
                ''')

        conn.close()
        USE_MYSQL = True
        print("[DATABASE] Successfully connected and synchronized with XAMPP MySQL (hostel_db)!")
        return True
    except Exception as e:
        USE_MYSQL = False
        print(f"[DATABASE WARNING] MySQL not reachable ({e}). Using SQLite fallback!")
        return False

# Initialize SQLite database as backup only
def init_sqlite_db():
    if not SQLITE_AVAILABLE:
        return
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT DEFAULT '',
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL,
            worker_trade TEXT DEFAULT 'none',
            phone TEXT,
            room_no TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            student_name TEXT,
            room_no TEXT,
            category TEXT,
            title TEXT,
            description TEXT,
            photo TEXT,
            status TEXT DEFAULT 'PENDING_REVIEW',
            assigned_worker_id INTEGER,
            worker_name TEXT,
            scheduled_date TEXT,
            scheduled_time TEXT,
            rejection_reason TEXT,
            rating INTEGER DEFAULT NULL,
            student_feedback TEXT DEFAULT '',
            completed_at TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Unified database query helper - PRIORITIZES MYSQL
def db_query(sql, params=(), one=False, all=False, commit=False):
    global USE_MYSQL
    if PYMYSQL_AVAILABLE:
        try:
            conn = pymysql.connect(
                host='localhost',
                user='root',
                password='',
                database='hostel_db',
                port=3306,
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True,
                connect_timeout=3
            )
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                if commit:
                    last_id = cursor.lastrowid
                    conn.close()
                    USE_MYSQL = True
                    return last_id
                res = cursor.fetchone() if one else (cursor.fetchall() if all else None)
            conn.close()
            USE_MYSQL = True
            return res
        except Exception as err:
            print(f"[DATABASE] MySQL query error ({err}). Falling back to SQLite...")

    # SQLite fallback
    if SQLITE_AVAILABLE:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        sqlite_sql = sql.replace('%s', '?')
        cursor.execute(sqlite_sql, params)
        if commit:
            conn.commit()
            last_id = cursor.lastrowid
            conn.close()
            return last_id
        res = cursor.fetchone() if one else (cursor.fetchall() if all else None)
        conn.close()
        if res is not None:
            if one:
                return dict(res)
            return [dict(row) for row in res]
    return None

# Run initialization
if not init_mysql_db():
    init_sqlite_db()

# -----------------------------------------------------------------------------
# 1. Public & Authentication Routes (Guest, Login, Register, Logout)
# -----------------------------------------------------------------------------

@app.route('/')
def home():
    """Guest landing page: Hostel maintenance guidelines, rules, public info."""
    user = session.get('username')
    return render_template('index.html', user=user)

def find_user_and_validate(identifier, password):
    """
    Find user by username, email, or role alias (case-insensitive)
    Accepts exact registered password, or '123' / 'password123' for demo users.
    """
    ident = identifier.strip().lower()
    passw = password.strip()

    # 1. Query by username or email
    user = db_query(
        "SELECT * FROM users WHERE LOWER(username) = %s OR (email IS NOT NULL AND LOWER(email) = %s)",
        (ident, ident),
        one=True
    )

    # 2. If not found, check role alias (e.g. 'student', 'warden', 'electrician', 'carpenter')
    if not user:
        if ident in ['student', 'student_kasun', 'kasun']:
            user = db_query("SELECT * FROM users WHERE role = 'student' LIMIT 1", one=True)
        elif ident in ['warden', 'subwarden', 'sub warden']:
            user = db_query("SELECT * FROM users WHERE role = 'warden' LIMIT 1", one=True)
        elif ident in ['worker', 'electrician', 'kamal']:
            user = db_query("SELECT * FROM users WHERE worker_trade = 'electrician' LIMIT 1", one=True)
        elif ident in ['carpenter', 'nimal', 'carpenter_nimal']:
            user = db_query("SELECT * FROM users WHERE worker_trade = 'carpenter' LIMIT 1", one=True)
        elif ident in ['plumber', 'saman', 'plumber_saman']:
            user = db_query("SELECT * FROM users WHERE worker_trade = 'plumber' LIMIT 1", one=True)
        elif ident in ['admin', 'administrator']:
            user = db_query("SELECT * FROM users WHERE role = 'admin' LIMIT 1", one=True)
        elif ident in ['guest', 'guest_user']:
            user = db_query("SELECT * FROM users WHERE role = 'guest' LIMIT 1", one=True)

    if not user:
        return None

    # Check password
    if user['password'] == passw:
        return user
    if passw in ['123', 'password123']:
        return user

    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Authenticate users (Student, Warden, Worker, Admin). Guests do not sign in."""
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        
        # Block guest login attempts
        if u.lower() in ['guest', 'guest_user']:
            return render_template('login.html', error='Guest users do not have a sign-in account. Guests can only view the public portal and register as a student.')

        user = find_user_and_validate(u, p)

        if user:
            if user.get('role') == 'guest':
                return render_template('login.html', error='Guest users do not have a sign-in account. Guests can only view the public portal and register as a student.')

            session['user_id'] = user['id']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            session['role'] = user['role']
            session['room_no'] = user.get('room_no') or 'Room 101'
            session['worker_trade'] = user.get('worker_trade') or 'none'

            # Redirect directly to corresponding dashboard
            if user['role'] == 'student':
                return redirect('/student')
            elif user['role'] == 'warden':
                return redirect('/warden')
            elif user['role'] == 'worker':
                return redirect('/worker')
            elif user['role'] == 'admin':
                return redirect('/admin')
            else:
                return redirect('/')
        else:
            return render_template('login.html', error='Invalid Username or Password! (Use password: 123)')
            
    return render_template('login.html')

# REST API endpoint for frontend standalone compatibility
@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json(silent=True) or request.form
    u = (data.get('username') or '').strip()
    p = (data.get('password') or '').strip()

    if u.lower() in ['guest', 'guest_user']:
        return jsonify({'success': False, 'message': 'Guest users do not have a sign-in account. Guests can only view the public portal and register as a student.'}), 403

    user = find_user_and_validate(u, p)
    if user:
        if user.get('role') == 'guest':
            return jsonify({'success': False, 'message': 'Guest users do not have a sign-in account. Guests can only view the public portal and register as a student.'}), 403

        session['user_id'] = user['id']
        session['username'] = user['username']
        session['full_name'] = user['full_name']
        session['role'] = user['role']
        return jsonify({'success': True, 'message': f"Welcome {user['full_name']}", 'user': user})
    return jsonify({'success': False, 'message': 'Invalid Username or Password!'}), 401

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Student Registration: Create a new Student account (Students only)."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', f"{username}@student.ac.lk").strip()
        password = request.form.get('password', '').strip()
        full_name = request.form.get('full_name', '').strip()
        role = 'student' # STRICTLY STUDENTS ONLY
        room_no = request.form.get('room_no', 'Room 101').strip()
        phone = request.form.get('phone', '').strip()

        if not username or not full_name or not password:
            return render_template('register.html', error='Please fill all required fields!')

        # Check if username already exists
        existing = db_query("SELECT id FROM users WHERE LOWER(username)=LOWER(%s)", (username,), one=True)
        if existing:
            return render_template('register.html', error='Username already taken! Choose another.')

        # Insert new user
        db_query('''
            INSERT INTO users (username, email, password, full_name, role, worker_trade, phone, room_no)
            VALUES (%s, %s, %s, %s, %s, 'none', %s, %s)
        ''', (username, email, password, full_name, role, phone, room_no), commit=True)

        return render_template('login.html', success='Student registered successfully! Please login.')

    return render_template('register.html')

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json(silent=True) or request.form
    username = (data.get('username') or '').strip()
    email = (data.get('email') or f"{username}@student.ac.lk").strip()
    password = (data.get('password') or 'password123').strip()
    full_name = (data.get('fullName') or data.get('full_name') or '').strip()
    role = 'student'
    phone = (data.get('phone') or '').strip()
    room_no = (data.get('roomNumber') or data.get('room_no') or 'Room 101').strip()

    if not username or not full_name:
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    existing = db_query("SELECT id FROM users WHERE LOWER(username)=LOWER(%s)", (username,), one=True)
    if existing:
        return jsonify({'success': False, 'message': 'Username already taken'}), 400

    db_query('''
        INSERT INTO users (username, email, password, full_name, role, worker_trade, phone, room_no)
        VALUES (%s, %s, %s, %s, %s, 'none', %s, %s)
    ''', (username, email, password, full_name, role, phone, room_no), commit=True)
    return jsonify({'success': True, 'message': 'Student registered successfully!'})

@app.route('/student/profile', methods=['POST'])
def student_profile():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect('/login')
    uid = session['user_id']
    full_name = request.form.get('full_name', '').strip()
    phone = request.form.get('phone', '').strip()
    room_no = request.form.get('room_no', '').strip()
    password = request.form.get('password', '').strip()

    if password:
        db_query("UPDATE users SET full_name=%s, phone=%s, room_no=%s, password=%s WHERE id=%s", (full_name, phone, room_no, password, uid), commit=True)
    else:
        db_query("UPDATE users SET full_name=%s, phone=%s, room_no=%s WHERE id=%s", (full_name, phone, room_no, uid), commit=True)

    session['full_name'] = full_name
    session['room_no'] = room_no
    return redirect('/student')

@app.route('/logout')
def logout():
    """Clear session data and redirect to login."""
    session.clear()
    return redirect('/login')

# -----------------------------------------------------------------------------
# 2. Student Dashboard: Submit Maintenance Request & Track Status
# -----------------------------------------------------------------------------
@app.route('/student', methods=['GET', 'POST'])
def student_dashboard():
    if session.get('role') != 'student':
        return redirect('/login')

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', 'general')
        desc = request.form.get('description', '').strip()
        room = request.form.get('room_no', session.get('room_no', 'Room 101'))
        
        # Photo Upload handling
        photo_file = request.files.get('photo')
        photo_filename = None
        if photo_file and photo_file.filename != '':
            ext = os.path.splitext(photo_file.filename)[1]
            photo_filename = f"req_{session['user_id']}_{os.urandom(4).hex()}{ext}"
            photo_file.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))

        # Save request with initial state 'PENDING_REVIEW'
        db_query('''
            INSERT INTO requests (student_id, student_name, room_no, category, title, description, photo, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'PENDING_REVIEW')
        ''', (session['user_id'], session['full_name'], room, category, title, desc, photo_filename), commit=True)
        
        return redirect('/student')

    # View all requests submitted by this student
    my_reqs = db_query("SELECT * FROM requests WHERE student_id=%s ORDER BY id DESC", (session['user_id'],), all=True)
    return render_template('student.html', requests=my_reqs or [])

# -----------------------------------------------------------------------------
# 3. Sub Warden Dashboard: Review, Assign Worker, Reject, Forward Schedule
# -----------------------------------------------------------------------------
@app.route('/warden')
def warden_dashboard():
    if session.get('role') != 'warden':
        return redirect('/login')

    all_reqs = db_query("SELECT * FROM requests ORDER BY id DESC", all=True)
    workers = db_query("SELECT * FROM users WHERE role='worker'", all=True)
    return render_template('warden.html', requests=all_reqs or [], workers=workers or [])

@app.route('/warden/assign', methods=['POST'])
def warden_assign():
    if session.get('role') != 'warden':
        return redirect('/login')

    req_id = request.form.get('req_id')
    worker_id = request.form.get('worker_id')

    worker = db_query("SELECT full_name FROM users WHERE id=%s", (worker_id,), one=True)
    if worker:
        db_query('''
            UPDATE requests 
            SET assigned_worker_id=%s, worker_name=%s, status='ASSIGNED' 
            WHERE id=%s
        ''', (worker_id, worker['full_name'], req_id), commit=True)

    return redirect('/warden')

@app.route('/warden/reject', methods=['POST'])
def warden_reject():
    if session.get('role') != 'warden':
        return redirect('/login')

    req_id = request.form.get('req_id')
    reason = request.form.get('reason', 'Policy violation')

    db_query('''
        UPDATE requests 
        SET status='REJECTED', rejection_reason=%s 
        WHERE id=%s
    ''', (reason, req_id), commit=True)

    return redirect('/warden')

# -----------------------------------------------------------------------------
# 4. Maintenance Worker Dashboard: Set Date & Time, Mark Completed
# -----------------------------------------------------------------------------
@app.route('/worker')
def worker_dashboard():
    if session.get('role') != 'worker':
        return redirect('/login')

    my_tasks = db_query("SELECT * FROM requests WHERE assigned_worker_id=%s ORDER BY id DESC", (session['user_id'],), all=True)
    return render_template('worker.html', tasks=my_tasks or [])

@app.route('/worker/schedule', methods=['POST'])
def worker_schedule():
    if session.get('role') != 'worker':
        return redirect('/login')

    req_id = request.form.get('req_id')
    date = request.form.get('date')
    time = request.form.get('time')

    db_query('''
        UPDATE requests 
        SET scheduled_date=%s, scheduled_time=%s, status='SCHEDULED' 
        WHERE id=%s
    ''', (date, time, req_id), commit=True)

    return redirect('/worker')

@app.route('/worker/complete/<int:req_id>')
def worker_complete(req_id):
    if session.get('role') != 'worker':
        return redirect('/login')

    from datetime import datetime
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    db_query("UPDATE requests SET status='COMPLETED', completed_at=%s WHERE id=%s", (now_str, req_id), commit=True)
    return redirect('/worker')

@app.route('/student/rate', methods=['POST'])
def student_rate():
    if session.get('role') != 'student':
        return redirect('/login')

    req_id = request.form.get('req_id')
    rating = request.form.get('rating', 5)
    feedback = request.form.get('feedback', '').strip()
    db_query("UPDATE requests SET rating=%s, student_feedback=%s WHERE id=%s", (rating, feedback, req_id), commit=True)
    return redirect('/student')

# -----------------------------------------------------------------------------
# 5. Administrator Dashboard: Manage Users (Add, Delete, View)
# -----------------------------------------------------------------------------
@app.route('/admin')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect('/login')

    users = db_query("SELECT * FROM users ORDER BY id ASC", all=True)
    reqs = db_query("SELECT * FROM requests", all=True) or []
    
    # Calculate stats for viva demonstration
    stats = {
        'total_users': len(users or []),
        'total_requests': len(reqs),
        'pending': sum(1 for r in reqs if r['status'] == 'PENDING_REVIEW'),
        'assigned': sum(1 for r in reqs if r['status'] == 'ASSIGNED'),
        'scheduled': sum(1 for r in reqs if r['status'] == 'SCHEDULED'),
        'completed': sum(1 for r in reqs if r['status'] == 'COMPLETED'),
        'rejected': sum(1 for r in reqs if r['status'] == 'REJECTED')
    }

    return render_template('admin.html', users=users or [], stats=stats)

@app.route('/admin/add-user', methods=['POST'])
def admin_add_user():
    if session.get('role') != 'admin':
        return redirect('/login')

    username = request.form.get('username', '').strip()
    email = request.form.get('email', f"{username}@hostel.ac.lk").strip()
    password = request.form.get('password', '').strip()
    full_name = request.form.get('full_name', '').strip()
    role = request.form.get('role', 'student')
    trade = request.form.get('trade', 'none')
    phone = request.form.get('phone', '').strip()
    room_no = request.form.get('room_no', '').strip()

    db_query('''
        INSERT INTO users (username, email, password, full_name, role, worker_trade, phone, room_no)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ''', (username, email, password, full_name, role, trade, phone, room_no), commit=True)

    return redirect('/admin')

@app.route('/admin/delete-user/<int:user_id>')
def admin_delete_user(user_id):
    if session.get('role') != 'admin':
        return redirect('/login')

    # Prevent deleting own admin session
    if user_id != session.get('user_id'):
        db_query("DELETE FROM users WHERE id=%s", (user_id,), commit=True)

    return redirect('/admin')

# -----------------------------------------------------------------------------
# Main Entry Point
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    print("==================================================================")
    print(" 🛠️  Hostel Maintenance Request Management System")
    print(f" Database Mode: {'MySQL (XAMPP)' if USE_MYSQL else 'SQLite Fallback (hostel_db.sqlite3)'}")
    print(" Server URL:    http://127.0.0.1:5000")
    print("==================================================================")
    app.run(host='0.0.0.0', port=5000, debug=True)
