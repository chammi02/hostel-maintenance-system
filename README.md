# Hostel Maintenance Request Management System (නේවාසිකාගාර නඩත්තු කළමනාකරණ පද්ධතිය)

> **Final Year Project Codebase & Comprehensive Viva Documentation**  
> Technologies: **Python, Java (Spring Boot), HTML5, CSS3, JavaScript, MySQL**  
> Based directly on the provided **Activity Swimlane Diagram** and **State Transition Diagram**.

---

## 📌 1. Project Overview (පද්ධතිය පිළිබඳ හැඳින්වීම)

The **Hostel Maintenance Request Management System** is a full-stack web application developed to automate and streamline facility maintenance and repair workflows within university or college hostels. It replaces manual paper logbooks and informal verbal complaints with a digital, transparent, role-based tracking platform.

### 5 System Roles (පද්ධතියේ පරිශීලක වර්ග 5)
1. **🎓 Student (ශිෂ්‍යයා)**: Submits complaints with problem category, detailed description, exact room location, and uploaded photos of damaged items. Tracks live status and views scheduled repair appointments.
2. **🛡️ Sub Warden / Warden (උප වාර්ඩන්)**: Reviews incoming complaints, approves or rejects unauthorized requests, assigns appropriate technicians (e.g., Electrician, Carpenter, Plumber), and relays scheduled repair appointments to students.
3. **⚡ Maintenance Worker (නඩත්තු සේවකයා / කාර්මිකයා)**: Views assigned work orders, sets available repair dates and time slots, updates work progress, and marks jobs as completed upon testing.
4. **⚙️ Administrator (පද්ධති පරිපාලක)**: Full user management (CRUD) across all roles, assigns technician trades/skills, monitors system uptime and maintenance KPIs.
5. **👤 Guest User (අමුත්තා)**: Views public hostel maintenance rules, emergency contacts, announcements, and accesses the student registration form.

---

## 📊 2. UML Diagrams Implementation Mapping

### A. Activity Diagram (Swimlane Flow)
As specified in your swimlane diagram, the workflow is distributed across 4 distinct actors:
```
+---------------+---------------+-------------------+-----------------------+
|    Student    |    System     |    Sub Warden     |  Maintenance Workers  |
+---------------+---------------+-------------------+-----------------------+
|  1. Login     |               |                   |                       |
|  2. Enter U/P | 3. Validates  |                   |                       |
|  4. Dashboard |               |                   |                       |
|  5. Submit Req| 6. Saves Req  |                   |                       |
|               |               | 7. Views Req      |                       |
|               |               | 8. Assigns Staff  |                       |
|               |               |                   | 9. Views Assigned Req |
|               |               |                   | 10. Sets Date & Time  |
|               |               | 11. Relays Sched  |                       |
| 12. Views Sched|              |                   |                       |
+---------------+---------------+-------------------+-----------------------+
```

### B. State Machine Diagram (Request Lifecycle)
The request moves strictly through the states specified in your state diagram:
* `PENDING_REVIEW`: Initial state upon submission.
* `UNDER_REVIEW`: Sub Warden inspects request details and uploaded photo.
* `REJECTED`: Sub Warden rejects policy-violating requests (e.g., unauthorized AC/heater) with a written reason.
* `ASSIGNED`: Sub Warden assigns request to a carpenter, electrician, plumber, etc.
* `SCHEDULED`: Maintenance worker provides exact inspection date and time slot.
* `COMPLETED`: Maintenance worker finishes repair, records notes, and verifies fix.

---

## 🗄️ 3. Database Schema (MySQL - `database/schema.sql`)

### Tables:
1. `users`: Stores login credentials, role (`student`, `warden`, `worker`, `admin`, `guest`), trade (`electrician`, `carpenter`, `plumber`, etc.), contact details, and assigned hostel block/room.
2. `maintenance_requests`: Primary transaction table recording request code, student FK, category, title, description, location, photo path, priority, status enum, assigned worker FK, scheduled date, time slot, and completion remarks.
3. `request_status_history`: Audit trail table logging who changed what state and when.
4. `hostel_announcements`: Public notices visible to students and guest users.

---

## 🚀 4. Step-by-Step Setup & Execution (පද්ධතිය ක්‍රියාත්මක කරන ආකාරය)

### Option 1: Standalone Instant Demo (No Installation Required)
For instant testing or presenting during viva:
1. Navigate to the `frontend/` directory.
2. Open `login.html` directly in any web browser (Google Chrome, Edge, Firefox).
3. Click any of the **1-Click Demo Fill buttons** (Student, Sub Warden, Electrician, Carpenter, Admin, Guest).
4. The system includes an automatic local storage engine that replicates all backend and database workflows instantly!

### Option 2: Running with Python Backend
1. **Database Setup**:
   - Start MySQL (e.g., via XAMPP Control Panel).
   - Open phpMyAdmin or MySQL CLI and run the script:
     ```sql
     SOURCE /path/to/database/schema.sql;
     ```
2. **Start Python Server**:
   ```bash
   cd backend-python
   pip install -r requirements.txt
   python app.py
   ```
   *The server runs at `http://127.0.0.1:5000` (automatically connects to MySQL or falls back gracefully to local SQLite).*

### Option 3: Running with Java Spring Boot Backend
1. Ensure JDK 17+ and Maven are installed.
2. Configure your MySQL credentials in `backend-java/src/main/resources/application.properties`.
3. Build and launch:
   ```bash
   cd backend-java
   mvn spring-boot:run
   ```
   *The Spring Boot server runs at `http://localhost:8080`.*

---

## 🇱🇰 5. Detailed Sinhala Explanation (සිංහල භාෂාවෙන් සවිස්තරාත්මක පැහැදිලි කිරීම)

මෙම ව්‍යාපෘතිය (Hostel Maintenance Request Management System) විශ්වවිද්‍යාල හෝ උසස් අධ්‍යාපන ආයතන වල නේවාසිකාගාර නඩත්තු කටයුතු කාර්යක්ෂමව පවත්වාගෙන යාම සඳහා නිර්මාණය කරන ලද්දකි.

### 1. පද්ධතියේ ප්‍රධාන පරිශීලකයින් 5 දෙනා (5 System Roles):
1. **ශිෂ්‍යයා (Student)**: නේවාසිකාගාරයේ පවතින විදුලි, වඩු, ජලනල හෝ වෙනත් කැඩීම්/බිඳීම් පිළිබඳ විස්තර, ඡායාරූප (Photo Upload) සහ කාමර අංකය ඇතුළත් කර Maintenance Request එකක් ඉදිරිපත් කරයි.
2. **උප වාර්ඩන් (Sub Warden)**: ශිෂ්‍යයා එවූ Request එක පරීක්ෂා කර බලා (Under Review), එය නේවාසිකාගාර නීතිවලට එකඟ නම් සුදුසු කාර්මිකයාට (Electrician / Carpenter / Plumber) පවරයි (Assign). නීති විරෝධී නම් Reject කරයි.
3. **නඩත්තු කාර්මිකයා (Maintenance Worker)**: තමන්ට පවරා ඇති වැඩ පරීක්ෂා කර, අලුත්වැඩියාව සඳහා පැමිණෙන දිනය සහ වේලාව (Date & Time) උප වාර්ඩන් හරහා ශිෂ්‍යයා වෙත දැනුම් දෙයි. අලුත්වැඩියාව අවසන් වූ පසු Completed ලෙස සලකුණු කරයි.
4. **පරිපාලක (Administrator)**: පද්ධතියේ සියලුම Users (Students, Wardens, Workers) එකතු කිරීම, වෙනස් කිරීම සහ ඉවත් කිරීම සිදු කරයි.
5. **අමුත්තා (Guest User)**: ලියාපදිංචි නොවූ අයට නේවාසිකාගාර නීති, නිවේදන සහ Register වීමේ පහසුකම ලබා දෙයි.

### 2. Activity Diagram එක Code එක සමඟ සම්බන්ධ වන ආකාරය:
* **Student Swimlane**: ශිෂ්‍යයා Login වී Dashboard එකට ගොස් `submit-request-form` එක හරහා විස්තර හා photo එකක් submit කරයි.
* **System Swimlane**: පද්ධතිය දත්ත Database එකේ `maintenance_requests` table එකට ඇතුළත් කර එහි Status එක `PENDING_REVIEW` බවට පත් කරයි.
* **Sub Warden Swimlane**: උප වාර්ඩන් Login වී pending requests පරීක්ෂා කර, සුදුසු කාර්මිකයා තෝරා Assign කරයි.
* **Maintenance Worker Swimlane**: කාර්මිකයා තමන්ගේ Dashboard එකෙන් request එක බලා "Set Date & Time" මඟින් දිනයක් හා වේලාවක් නියම කරයි.
* මෙම දිනය හා වේලාව ක්ෂණිකව ශිෂ්‍යයාගේ Dashboard එකෙහි "📅 Scheduled Appointment" ලෙස දිස්වේ.

### 3. State Diagram එක ක්‍රියාත්මක වන ආකාරය (Status Lifecycle):
1. `PENDING_REVIEW`: ශිෂ්‍යයා request එක submit කළ සැණින් ලැබෙන මුල් අවස්ථාව.
2. `UNDER_REVIEW`: උප වාර්ඩන් එය පරීක්ෂා කිරීම ආරම්භ කරන විට.
3. `REJECTED`: නීති විරෝධී ඉල්ලීමක් නම් හේතුවක් (Reason) සහිතව ප්‍රතික්ෂේප කිරීම.
4. `ASSIGNED`: සුදුසු කාර්මිකයෙකුට (Worker) වැඩේ පැවරූ පසු.
5. `SCHEDULED`: කාර්මිකයා වැඩ කරන දිනය හා වේලාව (Date & Time) ඇතුළත් කළ පසු.
6. `COMPLETED`: අලුත්වැඩියා කටයුත්ත සාර්ථකව අවසන් කළ පසු.

---

## 🔑 Demo Login Accounts (පරීක්ෂා කිරීම සඳහා ගිණුම්)
සියලුම ගිණුම් සඳහා පෙරනිමි මුරපදය (Default Password): `password123`

| Role | Username | Purpose |
|---|---|---|
| **Student** | `student_kasun` | කාමර 204 හි ශිෂ්‍යයා (ඉල්ලීම් ඉදිරිපත් කිරීම හා දිනය බැලීම) |
| **Sub Warden** | `subwarden` | ඉල්ලීම් පරීක්ෂා කිරීම, ප්‍රතික්ෂේප කිරීම හා assign කිරීම |
| **Electrician** | `electrician_kamal` | විදුලි කාර්මිකයා (දිනය හා වේලාව ලබා දීම) |
| **Carpenter** | `carpenter_nimal` | වඩු කාර්මිකයා (මේස, දොර ජනෙල් අලුත්වැඩියාව) |
| **Administrator** | `admin` | සියලුම පරිශීලකයින් කළමනාකරණය |
| **Guest** | `guest_user` | තොරතුරු බැලීම හා ලියාපදිංචිය |
