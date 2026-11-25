import os
import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from config import Config
from database import get_db_connection, init_db

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def dict_row_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def execute_query(query, params=None, fetch_all=False, fetch_one=False, commit=False):
    """Universal query runner supporting both MySQL and SQLite seamlessly."""
    conn, engine = get_db_connection()
    try:
        # If SQLite, replace %s with ?
        if engine == 'sqlite':
            query = query.replace('%s', '?')
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        
        if fetch_one:
            row = cursor.fetchone()
            if engine == 'sqlite' and row:
                return dict(row)
            return row
        if fetch_all:
            rows = cursor.fetchall()
            if engine == 'sqlite':
                return [dict(r) for r in rows]
            return rows
        if commit:
            if engine == 'sqlite':
                conn.commit()
            last_id = cursor.lastrowid
            return last_id
    finally:
        conn.close()

# Initialize DB on start
init_db()

# ---------------------------------------------------------
# Static Uploads File Serving
# ---------------------------------------------------------
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ---------------------------------------------------------
# Authentication Routes
# ---------------------------------------------------------
@app.route('/api/auth/login', methods=['POST'])
def login():
    """
    Validates user credentials against username and password.
    Returns user role and profile details.
    """
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password are required'}), 400

    user = execute_query(
        "SELECT id, username, email, role, full_name, hostel_block, room_number, worker_trade, status FROM users WHERE username = %s AND password_hash = %s",
        (username, password),
        fetch_one=True
    )

    if not user:
        return jsonify({'success': False, 'message': 'Invalid username or password'}), 401

    if user.get('status') != 'active':
        return jsonify({'success': False, 'message': 'Account is inactive or pending approval'}), 403

    return jsonify({
        'success': True,
        'message': f'Welcome back, {user["full_name"]}!',
        'user': user
    })

@app.route('/api/auth/register', methods=['POST'])
def register():
    """
    Guest self-registration for new students or guests.
    """
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    full_name = data.get('full_name', '').strip()
    phone = data.get('phone', '').strip()
    role = data.get('role', 'student')
    hostel_block = data.get('hostel_block', 'Block A')
    room_number = data.get('room_number', '')

    if not username or not email or not password or not full_name:
        return jsonify({'success': False, 'message': 'Please fill all required fields'}), 400

    existing = execute_query(
        "SELECT id FROM users WHERE username = %s OR email = %s",
        (username, email),
        fetch_one=True
    )
    if existing:
        return jsonify({'success': False, 'message': 'Username or Email is already registered'}), 400

    user_id = execute_query(
        "INSERT INTO users (username, email, password_hash, role, full_name, phone, hostel_block, room_number, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'active')",
        (username, email, password, role, full_name, phone, hostel_block, room_number),
        commit=True
    )

    return jsonify({
        'success': True,
        'message': 'Registration successful! You may now login.',
        'user_id': user_id
    })

# ---------------------------------------------------------
# Public Announcements (Guest & All Users)
# ---------------------------------------------------------
@app.route('/api/announcements', methods=['GET'])
def get_announcements():
    announcements = execute_query(
        "SELECT id, title, content, created_at FROM hostel_announcements ORDER BY id DESC LIMIT 10",
        fetch_all=True
    )
    return jsonify({'success': True, 'data': announcements or []})

# ---------------------------------------------------------
# Student Routes
# ---------------------------------------------------------
@app.route('/api/student/requests', methods=['GET'])
def get_student_requests():
    student_id = request.args.get('student_id', type=int)
    if not student_id:
        return jsonify({'success': False, 'message': 'student_id is required'}), 400

    requests = execute_query(
        """
        SELECT r.*, w.full_name AS worker_name, w.worker_trade, w.phone AS worker_phone
        FROM maintenance_requests r
        LEFT JOIN users w ON r.assigned_worker_id = w.id
        WHERE r.student_id = %s
        ORDER BY r.id DESC
        """,
        (student_id,),
        fetch_all=True
    )
    return jsonify({'success': True, 'data': requests or []})

@app.route('/api/student/requests', methods=['POST'])
def submit_maintenance_request():
    """
    Submits a new maintenance request with photo upload, location, and description.
    Sets status to 'PENDING_REVIEW' as per the state diagram.
    """
    student_id = request.form.get('student_id', type=int)
    title = request.form.get('title', '').strip()
    category = request.form.get('category', 'general').strip()
    description = request.form.get('description', '').strip()
    location = request.form.get('location', '').strip()
    priority = request.form.get('priority', 'medium').strip()

    if not student_id or not title or not description or not location:
        return jsonify({'success': False, 'message': 'Missing mandatory fields'}), 400

    photo_path = None
    if 'photo' in request.files:
        file = request.files['photo']
        if file and file.filename and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"req_{student_id}_{timestamp}.{ext}"
            saved_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(saved_path)
            photo_path = f"uploads/{filename}"

    # Generate sequential request code
    code = f"REQ-{datetime.datetime.now().year}-{int(datetime.datetime.now().timestamp()) % 10000:04d}"

    req_id = execute_query(
        """
        INSERT INTO maintenance_requests 
        (request_code, student_id, category, title, description, location, photo_path, priority, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'PENDING_REVIEW')
        """,
        (code, student_id, category, title, description, location, photo_path, priority),
        commit=True
    )

    return jsonify({
        'success': True,
        'message': 'Maintenance request submitted successfully! Pending Sub Warden review.',
        'request_id': req_id,
        'request_code': code
    })

# ---------------------------------------------------------
# Sub Warden Routes
# ---------------------------------------------------------
@app.route('/api/warden/requests', methods=['GET'])
def get_warden_requests():
    status = request.args.get('status')
    if status and status != 'ALL':
        requests = execute_query(
            """
            SELECT r.*, s.full_name AS student_name, s.phone AS student_phone, s.room_number AS student_room,
                   w.full_name AS worker_name, w.worker_trade
            FROM maintenance_requests r
            JOIN users s ON r.student_id = s.id
            LEFT JOIN users w ON r.assigned_worker_id = w.id
            WHERE r.status = %s
            ORDER BY r.id DESC
            """,
            (status,),
            fetch_all=True
        )
    else:
        requests = execute_query(
            """
            SELECT r.*, s.full_name AS student_name, s.phone AS student_phone, s.room_number AS student_room,
                   w.full_name AS worker_name, w.worker_trade
            FROM maintenance_requests r
            JOIN users s ON r.student_id = s.id
            LEFT JOIN users w ON r.assigned_worker_id = w.id
            ORDER BY r.id DESC
            """,
            fetch_all=True
        )
    return jsonify({'success': True, 'data': requests or []})

@app.route('/api/warden/requests/<int:req_id>/review', methods=['POST'])
def review_request(req_id):
    """Moves status from PENDING_REVIEW to UNDER_REVIEW."""
    execute_query(
        "UPDATE maintenance_requests SET status = 'UNDER_REVIEW' WHERE id = %s",
        (req_id,),
        commit=True
    )
    return jsonify({'success': True, 'message': 'Request marked as Under Review.'})

@app.route('/api/warden/requests/<int:req_id>/reject', methods=['POST'])
def reject_request(req_id):
    """Rejects request with explanation note."""
    data = request.get_json() or {}
    reason = data.get('reason', 'Request rejected by Sub Warden').strip()

    execute_query(
        "UPDATE maintenance_requests SET status = 'REJECTED', rejection_reason = %s WHERE id = %s",
        (reason, req_id),
        commit=True
    )
    return jsonify({'success': True, 'message': 'Request rejected.'})

@app.route('/api/warden/requests/<int:req_id>/assign', methods=['POST'])
def assign_worker(req_id):
    """
    Warden assigns the request to suitable maintenance worker (electrician, carpenter, etc.).
    Moves status from UNDER_REVIEW to ASSIGNED.
    """
    data = request.get_json() or {}
    worker_id = data.get('worker_id')
    warden_id = data.get('warden_id')

    if not worker_id:
        return jsonify({'success': False, 'message': 'Worker ID is required'}), 400

    execute_query(
        """
        UPDATE maintenance_requests 
        SET assigned_worker_id = %s, assigned_by_warden_id = %s, status = 'ASSIGNED'
        WHERE id = %s
        """,
        (worker_id, warden_id, req_id),
        commit=True
    )
    return jsonify({'success': True, 'message': 'Request assigned to maintenance worker.'})

@app.route('/api/workers', methods=['GET'])
def get_workers():
    """Returns list of active maintenance staff."""
    trade = request.args.get('trade')
    if trade:
        workers = execute_query(
            "SELECT id, full_name, worker_trade, phone FROM users WHERE role = 'worker' AND worker_trade = %s AND status = 'active'",
            (trade,),
            fetch_all=True
        )
    else:
        workers = execute_query(
            "SELECT id, full_name, worker_trade, phone FROM users WHERE role = 'worker' AND status = 'active'",
            fetch_all=True
        )
    return jsonify({'success': True, 'data': workers or []})

# ---------------------------------------------------------
# Maintenance Worker Routes
# ---------------------------------------------------------
@app.route('/api/worker/tasks', methods=['GET'])
def get_worker_tasks():
    worker_id = request.args.get('worker_id', type=int)
    if not worker_id:
        return jsonify({'success': False, 'message': 'worker_id is required'}), 400

    tasks = execute_query(
        """
        SELECT r.*, s.full_name AS student_name, s.phone AS student_phone, s.room_number
        FROM maintenance_requests r
        JOIN users s ON r.student_id = s.id
        WHERE r.assigned_worker_id = %s
        ORDER BY r.id DESC
        """,
        (worker_id,),
        fetch_all=True
    )
    return jsonify({'success': True, 'data': tasks or []})

@app.route('/api/worker/tasks/<int:req_id>/schedule', methods=['POST'])
def schedule_task(req_id):
    """
    Worker provides date and time for the repair.
    Transitions status to SCHEDULED. Sub warden & student can view it.
    """
    data = request.get_json() or {}
    scheduled_date = data.get('scheduled_date')
    scheduled_time = data.get('scheduled_time')
    worker_notes = data.get('worker_notes', '')

    if not scheduled_date or not scheduled_time:
        return jsonify({'success': False, 'message': 'Date and Time are required'}), 400

    execute_query(
        """
        UPDATE maintenance_requests
        SET scheduled_date = %s, scheduled_time = %s, worker_notes = %s, status = 'SCHEDULED'
        WHERE id = %s
        """,
        (scheduled_date, scheduled_time, worker_notes, req_id),
        commit=True
    )
    return jsonify({'success': True, 'message': 'Repair scheduled successfully! Student and Warden notified.'})

@app.route('/api/worker/tasks/<int:req_id>/complete', methods=['POST'])
def complete_task(req_id):
    """Marks the maintenance job as COMPLETED."""
    data = request.get_json() or {}
    worker_notes = data.get('worker_notes', '')

    execute_query(
        """
        UPDATE maintenance_requests
        SET status = 'COMPLETED', worker_notes = %s
        WHERE id = %s
        """,
        (worker_notes, req_id),
        commit=True
    )
    return jsonify({'success': True, 'message': 'Maintenance marked as Completed!'})

# ---------------------------------------------------------
# Administrator Routes
# ---------------------------------------------------------
@app.route('/api/admin/users', methods=['GET'])
def get_all_users():
    users = execute_query(
        "SELECT id, username, email, role, full_name, phone, hostel_block, room_number, worker_trade, status, created_at FROM users ORDER BY id ASC",
        fetch_all=True
    )
    return jsonify({'success': True, 'data': users or []})

@app.route('/api/admin/users', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    username = data.get('username')
    email = data.get('email')
    password = data.get('password', 'password123')
    role = data.get('role', 'student')
    full_name = data.get('full_name')
    phone = data.get('phone', '')
    hostel_block = data.get('hostel_block', '')
    room_number = data.get('room_number', '')
    worker_trade = data.get('worker_trade', 'none')

    if not username or not email or not full_name:
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    user_id = execute_query(
        """
        INSERT INTO users (username, email, password_hash, role, full_name, phone, hostel_block, room_number, worker_trade, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'active')
        """,
        (username, email, password, role, full_name, phone, hostel_block, room_number, worker_trade),
        commit=True
    )
    return jsonify({'success': True, 'message': 'User created successfully', 'user_id': user_id})

@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    execute_query("DELETE FROM users WHERE id = %s", (user_id,), commit=True)
    return jsonify({'success': True, 'message': 'User deleted successfully'})

@app.route('/api/admin/stats', methods=['GET'])
def get_stats():
    total_requests = execute_query("SELECT COUNT(*) as count FROM maintenance_requests", fetch_one=True)['count']
    pending_count = execute_query("SELECT COUNT(*) as count FROM maintenance_requests WHERE status IN ('PENDING_REVIEW', 'UNDER_REVIEW')", fetch_one=True)['count']
    scheduled_count = execute_query("SELECT COUNT(*) as count FROM maintenance_requests WHERE status = 'SCHEDULED'", fetch_one=True)['count']
    completed_count = execute_query("SELECT COUNT(*) as count FROM maintenance_requests WHERE status = 'COMPLETED'", fetch_one=True)['count']
    total_users = execute_query("SELECT COUNT(*) as count FROM users", fetch_one=True)['count']
    workers_count = execute_query("SELECT COUNT(*) as count FROM users WHERE role = 'worker'", fetch_one=True)['count']

    return jsonify({
        'success': True,
        'data': {
            'total_requests': total_requests,
            'pending_review': pending_count,
            'scheduled': scheduled_count,
            'completed': completed_count,
            'total_users': total_users,
            'workers': workers_count
        }
    })

if __name__ == '__main__':
    print("==================================================================")
    print(" Hostel Maintenance Request Management System (Backend API Server)")
    print(" Running at: http://127.0.0.1:5000")
    print("==================================================================")
    app.run(host='0.0.0.0', port=5000, debug=True)
