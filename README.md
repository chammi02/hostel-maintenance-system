# Hostel Maintenance Request Management System

> **Final Year Project Codebase & Comprehensive Technical Documentation**  
> **Technologies:** Python (Flask), Java (Spring Boot), HTML5, CSS3, JavaScript, MySQL  
> **Architecture:** Complies strictly with the Activity Swimlane Diagram and State Machine Lifecycle.

---

## 📌 1. Project Overview

The **Hostel Maintenance Request Management System** is an automated web platform designed to streamline and digitize facility maintenance, problem reporting, and repair scheduling within university or college hostels.

It replaces inefficient paper logbooks and manual complaints with a transparent, role-based digital tracking platform connecting students, hostel administration, and technical staff.

### The 5 System User Roles:
1. **🎓 Student**:
   - Logs in securely and accesses the student dashboard.
   - Submits maintenance complaints specifying problem category (electrical, carpentry, plumbing, etc.), room/hostel location, priority, and problem description.
   - Attaches and uploads photographs of damaged fixtures.
   - Tracks complaint status in real-time and views scheduled repair appointment dates and time slots.
2. **🛡️ Sub Warden / Warden**:
   - Reviews incoming student complaints (`UNDER_REVIEW`).
   - Evaluates complaints against hostel policy and rejects unauthorized requests (e.g., unauthorized private appliances) with a documented reason (`REJECTED`).
   - Assigns legitimate complaints to appropriate skilled maintenance technicians (Electrician, Carpenter, Plumber) (`ASSIGNED`).
   - Confirms repair schedules submitted by workers and relays appointment details to students.
3. **⚡ Maintenance Worker (Technicians - Electrician, Carpenter, Plumber)**:
   - Accesses assigned work orders filtered by their specific trade/specialty.
   - Inspects work requirements and proposes scheduled repair dates and time slots (`SCHEDULED`).
   - Adds technical preparation notes (e.g., required parts, tools).
   - Updates progress and marks tasks as completed upon testing and verification (`COMPLETED`).
4. **⚙️ System Administrator**:
   - Manages user accounts across all 5 roles (Create, Read, Update, Delete - CRUD).
   - Assigns technical trades and specialties to maintenance staff.
   - Monitors overall hostel maintenance KPIs, request volumes, and system health.
5. **👤 Guest User**:
   - Browses public hostel rules, maintenance guidelines, and official announcements.
   - Registers for a new student or guest account via the self-registration portal.

---

## 📊 2. UML Diagram Implementation & Workflow Mapping

### A. Activity Diagram (Swimlane Flow)
The workflow follows a 4-swimlane structure matching the operational actors:

```
+-------------------+-------------------+-----------------------+-----------------------+
|      Student      |      System       |      Sub Warden       |  Maintenance Workers  |
+-------------------+-------------------+-----------------------+-----------------------+
|  1. Login         |                   |                       |                       |
|  2. Enter U/P     | 3. Validates Cred |                       |                       |
|  4. View Dashboard|                   |                       |                       |
|  5. Submit Request| 6. Saves Request  |                       |                       |
|     (Photo+Loc)   |    (PENDING_REV)  | 7. Reviews Request    |                       |
|                   |                   | 8. Assigns Worker     |                       |
|                   |                   |    (By Specialty)     | 9. Views Work Order   |
|                   |                   |                       | 10. Sets Date & Time  |
|                   |                   | 11. Relays Schedule   |                       |
| 12. Views Schedule|                   |     to Student        |                       |
+-------------------+-------------------+-----------------------+-----------------------+
```

### B. State Machine Diagram (Request Lifecycle)
Requests transition strictly through discrete states:

```
  [Start] 
     │
     ▼
[PENDING_REVIEW] ──(Rejected by Warden with Reason)──► [REJECTED] ──► [End]
     │
     │ (Warden inspects request details & photo)
     ▼
[UNDER_REVIEW]
     │
     │ (Warden assigns to Electrician/Carpenter/Plumber)
     ▼
 [ASSIGNED]
     │
     │ (Worker provides repair date and time slot)
     ▼
 [SCHEDULED]
     │
     │ (Worker executes and verifies repair work)
     ▼
 [COMPLETED] ──► [End]
```

* **`PENDING_REVIEW`**: Initial state immediately upon submission by a student.
* **`UNDER_REVIEW`**: Sub Warden opens and reviews the complaint details and uploaded photo.
* **`REJECTED`**: Sub Warden declines the request due to policy violation (with official reason recorded).
* **`ASSIGNED`**: Sub Warden delegates the job to a qualified technician based on problem category.
* **`SCHEDULED`**: Maintenance technician books an exact appointment date and time window.
* **`COMPLETED`**: Technician concludes the repair, records completion notes, and marks the task finished.

---

## 🗄️ 3. Database Architecture (MySQL)

The relational schema is configured in `database/schema.sql` (or `setup_db.sql`):

### 1. `users` Table
Stores authentication and profile information for all 5 roles:
* `id` (INT, Primary Key, Auto Increment)
* `username` (VARCHAR 50, Unique, Not Null)
* `password` / `password_hash` (VARCHAR 255, Not Null)
* `full_name` (VARCHAR 100, Not Null)
* `role` (ENUM: `'student'`, `'warden'`, `'worker'`, `'admin'`, `'guest'`)
* `worker_trade` (ENUM / VARCHAR: `'electrician'`, `'carpenter'`, `'plumber'`, `'mason'`, `'general'`, `'none'`)
* `phone` (VARCHAR 20)
* `hostel_block` (VARCHAR 50)
* `room_no` / `room_number` (VARCHAR 50)
* `status` (ENUM: `'active'`, `'inactive'`)

### 2. `requests` / `maintenance_requests` Table
Core transaction table tracking the repair lifecycle:
* `id` (INT, Primary Key, Auto Increment)
* `request_code` (VARCHAR 30, Unique)
* `student_id` (INT, Foreign Key referencing `users.id`)
* `category` (ENUM: `'electrical'`, `'carpentry'`, `'plumbing'`, `'furniture'`, `'masonry'`, `'other'`)
* `title` (VARCHAR 150, Not Null)
* `description` (TEXT, Not Null)
* `location` / `room_no` (VARCHAR 100, Not Null)
* `photo` / `photo_path` (VARCHAR 255, Stores uploaded image path)
* `priority` (ENUM: `'low'`, `'medium'`, `'high'`, `'emergency'`)
* `status` (ENUM: `'PENDING_REVIEW'`, `'UNDER_REVIEW'`, `'ASSIGNED'`, `'SCHEDULED'`, `'COMPLETED'`, `'REJECTED'`)
* `assigned_worker_id` (INT, Foreign Key referencing `users.id`)
* `assigned_by_warden_id` (INT, Foreign Key referencing `users.id`)
* `rejection_reason` (TEXT)
* `scheduled_date` (DATE / VARCHAR)
* `scheduled_time` (VARCHAR 50)
* `worker_notes` (TEXT)
* `created_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)

### 3. `hostel_announcements` Table
Stores public guidelines and notices displayed on the guest portal.

---

## 📁 4. Project Directory Structure

```
c:\hostel-maintenance-system\
├── setup_db.sql                    # Quick MySQL setup script for XAMPP
├── README.md                       # Comprehensive project documentation
├── simple-app/                     # Beginner-Friendly Unified Stack (Flask + MySQL)
│   ├── app.py                      # Flask server handling all routes, auth & MySQL queries
│   ├── RUN_PROJECT.bat             # 1-Click launcher script
│   ├── static/
│   │   ├── style.css               # Clean responsive styling
│   │   └── uploads/                # Storage directory for student damage photos
│   └── templates/
│       ├── index.html              # Guest portal & hostel maintenance rules
│       ├── login.html              # Login screen with 1-click test credentials
│       ├── student.html            # Student dashboard (Photo upload & schedule viewer)
│       ├── warden.html             # Sub Warden portal (Review, reject & assign)
│       ├── worker.html             # Technician portal (Date/time booking & completion)
│       └── admin.html              # Administrator dashboard (User management)
├── frontend/                       # Standalone Modern Web UI (HTML5, CSS3, JS)
│   ├── index.html                  # Guest portal
│   ├── login.html                  # Unified login
│   ├── register.html               # Registration form
│   ├── student-dashboard.html      # Advanced student dashboard
│   ├── warden-dashboard.html       # Advanced warden dashboard
│   ├── worker-dashboard.html       # Advanced worker dashboard
│   ├── admin-dashboard.html        # Advanced admin dashboard
│   ├── css/style.css               # Master stylesheet with status badges & modals
│   └── js/api.js                   # API client with automatic browser mock fallback
├── backend-python/                 # Modular Python REST API backend
│   ├── app.py                      # RESTful endpoints with CORS & upload support
│   ├── config.py                   # Configuration parameters
│   ├── database.py                 # PyMySQL connector with SQLite fallback
│   └── requirements.txt            # Python dependencies
├── backend-java/                   # Enterprise Java Spring Boot Backend
│   ├── pom.xml                     # Maven project configuration (JPA, MySQL)
│   └── src/main/
│       ├── resources/application.properties
│       └── java/com/hostel/maintenance/
│           ├── HostelApplication.java
│           ├── model/              # JPA Entities (User, MaintenanceRequest, Status)
│           ├── repository/         # Spring Data Repositories
│           └── controller/         # REST Controllers
└── database/
    └── schema.sql                  # Full production MySQL schema with audit tables
```

---

## 🚀 5. How to Setup and Run the Project

### Prerequisites:
* **XAMPP** (Apache & MySQL)
* **Python 3.10+** (with `flask` and `pymysql` installed)

---

### Step 1: Start XAMPP MySQL & Apache
1. Open the **XAMPP Control Panel**.
2. Click **Start** for both **Apache** (Port 80) and **MySQL** (Port 3306).
3. Ensure both indicators turn green.

### Step 2: Import Database in phpMyAdmin
1. Open your web browser and navigate to `http://localhost/phpmyadmin`.
2. Click the **SQL** tab in the top navigation bar.
3. Open `c:\hostel-maintenance-system\setup_db.sql` in a text editor, copy its contents, paste them into the SQL window, and click **Go**.
4. The database `hostel_db` will be created with all tables and pre-loaded test accounts.

### Step 3: Run the Application

#### Option A: 1-Click Launch (Recommended for Viva/Testing)
1. Navigate to `c:\hostel-maintenance-system\simple-app`.
2. Double-click `RUN_PROJECT.bat`.
3. Open your browser and visit:  
   👉 **`http://127.0.0.1:5000`**

#### Option B: Terminal Launch
```powershell
cd c:\hostel-maintenance-system\simple-app
pip install flask pymysql
python app.py
```
Visit `http://127.0.0.1:5000` in your web browser.

#### Option C: Standalone Frontend Demo (No Server Required)
1. Navigate to `c:\hostel-maintenance-system\frontend`.
2. Double-click `login.html` to open it in Chrome, Edge, or Firefox.
3. The interface will operate immediately using its built-in browser state storage!

---

## 🔑 6. Demo Accounts & Credentials

All test accounts share the standard password: **`123`** *(or `password123` in the advanced frontend)*.

| Role | Username | Full Name | Trade / Purpose |
|---|---|---|---|
| **Student** | `kasun` | Kasun Perera | Resident of Room 204; submits complaints & checks appointments |
| **Sub Warden** | `warden` | Dr. Sunil Perera | Inspects requests, approves/rejects, assigns technicians |
| **Electrician** | `kamal` | Kamal Bandara | Maintenance staff (Electrical repairs; sets date & time) |
| **Carpenter** | `nimal` | Nimal Silva | Maintenance staff (Carpentry repairs; sets date & time) |
| **Admin** | `admin` | System Administrator | Oversees all user accounts & system metrics |
| **Guest** | `guest` | Guest Applicant | Browses public guidelines & hostel rules |

> **Viva Tip:** On `http://127.0.0.1:5000/login`, you can use the **1-Click Fast Fill buttons** to immediately populate credentials for any role during your presentation without typing.

---

## 🎤 7. Viva / Oral Presentation Defense Guide

When presenting this project to your examiners, structure your answers as follows:

### Q1: Why did you choose Python Flask for this project?
**Answer:**  
*"Flask is a lightweight, clean, and highly readable micro-framework. It provides full control over HTTP routing, sessions, and multipart file uploads without the heavy boilerplate code of enterprise Java frameworks. This ensures rapid performance, clean architecture, and easy maintainability for a hostel management portal."*

### Q2: How does the system handle image uploads?
**Answer:**  
*"When a student submits a problem report with an attached photo, the form uses `enctype="multipart/form-data"`. The Flask backend retrieves the file via `request.files`, validates the extension, stores the physical image under `static/uploads/`, and saves the file reference path in the MySQL `requests.photo` column. The Sub Warden and technician can then inspect the photo before visiting the room."*

### Q3: How is role-based access control (RBAC) enforced?
**Answer:**  
*"Upon successful login, user credentials are verified against the MySQL `users` table. The authenticated user's `id`, `full_name`, and `role` are stored securely in the Flask `session`. Each dashboard route (e.g., `/student`, `/warden`, `/worker`, `/admin`) checks `session.get('role')`. If an unauthorized role attempts access, they are automatically redirected to the login view."*

### Q4: How do the Activity and State Machine diagrams connect?
**Answer:**  
*"The Activity Swimlane diagram governs the sequential interactions between the 4 actors: Student submits, System stores as `PENDING_REVIEW`, Sub Warden reviews and assigns moving it to `ASSIGNED`, Worker schedules an appointment moving it to `SCHEDULED`, which is relayed back to the student. If the Sub Warden finds an unauthorized appliance, it transitions directly to `REJECTED`."*

---

## 📄 8. License & Authorship

Developed as a Final Year Project for academic evaluation.  
All code, database schemas, and documentation are designed for academic and educational purposes.
