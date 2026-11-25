/**
 * Hostel Maintenance Request Management System
 * Shared API & State Management Layer
 * Supports Live Backend API + Auto-Fallback Mock Storage for Seamless Demos
 */

const API_BASE = 'http://127.0.0.1:5000/api';

// -------------------------------------------------------------
// 1. Initial Mock Database Seeding
// -------------------------------------------------------------
function initMockData() {
    if (!localStorage.getItem('hostel_users')) {
        const users = [
            { id: 1, username: 'admin', role: 'admin', full_name: 'System Administrator', email: 'admin@hostel.ac.lk', phone: '+94 77 111 2233', status: 'active', department: 'Hostel Administration HQ' },
            { id: 2, username: 'subwarden', role: 'warden', full_name: 'Dr. Sunil Perera (Sub Warden)', email: 'warden@hostel.ac.lk', phone: '+94 71 222 3344', status: 'active', department: 'Warden Office, Block A' },
            { id: 3, username: 'electrician_kamal', role: 'worker', worker_trade: 'electrician', full_name: 'Kamal Bandara (Electrician)', email: 'kamal@hostel.ac.lk', phone: '+94 76 333 4455', status: 'active', department: 'Maintenance Workshop M-01' },
            { id: 4, username: 'carpenter_nimal', role: 'worker', worker_trade: 'carpenter', full_name: 'Nimal Silva (Carpenter)', email: 'nimal@hostel.ac.lk', phone: '+94 75 444 5566', status: 'active', department: 'Maintenance Workshop M-02' },
            { id: 5, username: 'plumber_saman', role: 'worker', worker_trade: 'plumber', full_name: 'Saman Kumara (Plumber)', email: 'saman@hostel.ac.lk', phone: '+94 78 555 6677', status: 'active', department: 'Maintenance Workshop M-03' },
            { id: 6, username: 'student_kasun', role: 'student', full_name: 'Kasun Jayawardena', email: 'kasun@student.ac.lk', phone: '+94 70 666 7788', hostel_block: 'Block G', room_number: 'U112', status: 'active' },
            { id: 7, username: 'student_amaya', role: 'student', full_name: 'Amaya Wickramasinghe', email: 'amaya@student.ac.lk', phone: '+94 72 777 8899', hostel_block: 'Block A', room_number: 'D113', status: 'active' }
        ];
        localStorage.setItem('hostel_users', JSON.stringify(users));
    } else {
        // Ensure guest users cannot have login sessions in localStorage
        const storedUsers = JSON.parse(localStorage.getItem('hostel_users') || '[]');
        const sanitized = storedUsers.filter(u => u.role !== 'guest' && u.username !== 'guest_user');
        if (sanitized.length !== storedUsers.length) {
            localStorage.setItem('hostel_users', JSON.stringify(sanitized));
        }
    }

    // Requests seed with active lifecycle, ratings, and past 7+ days history
    if (!localStorage.getItem('hostel_requests')) {
        const requests = [
            {
                id: 1,
                request_code: 'REQ-2026-001',
                student_id: 6,
                student_name: 'Kasun Jayawardena',
                student_phone: '+94 70 666 7788',
                student_room: 'U112',
                category: 'electrical',
                title: 'Ceiling Fan Not Working & Sparking',
                description: 'The ceiling fan regulator gives sparks when turned to speed 3 and does not rotate at all.',
                location: 'Block G, 2nd Floor, U112',
                photo_path: 'https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=300',
                priority: 'high',
                status: 'SCHEDULED',
                assigned_worker_id: 3,
                worker_name: 'Kamal Bandara (Electrician)',
                worker_trade: 'electrician',
                scheduled_date: '2026-11-15',
                scheduled_time: '10:00 AM - 11:30 AM',
                worker_notes: 'Will bring replacement regulator and multimeter.',
                created_at: '2026-11-14 09:30'
            },
            {
                id: 2,
                request_code: 'REQ-2026-002',
                student_id: 6,
                student_name: 'Kasun Jayawardena',
                student_phone: '+94 70 666 7788',
                student_room: 'Room U112',
                category: 'carpentry',
                title: 'Broken Study Table Drawer & Lock',
                description: 'The wooden drawer is stuck and the lock mechanism is broken.',
                location: 'Block G, 2nd Floor, U112',
                photo_path: 'https://images.unsplash.com/photo-1538688525198-9b88f6f53126?w=300',
                priority: 'medium',
                status: 'ASSIGNED',
                assigned_worker_id: 4,
                worker_name: 'Nimal Silva (Carpenter)',
                worker_trade: 'carpenter',
                created_at: '2026-11-14 10:15'
            },
            {
                id: 3,
                request_code: 'REQ-2026-003',
                student_id: 7,
                student_name: 'Amaya Wickramasinghe',
                student_phone: '+94 72 777 8899',
                student_room: 'D113',
                category: 'plumbing',
                title: 'Water Tap Leaking in Bathroom',
                description: 'Continuous water leakage from wash basin tap causing floor flooding.',
                location: 'Block B, 1st Floor, Room 112',
                photo_path: 'https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=300',
                priority: 'medium',
                status: 'SCHEDULED',
                assigned_worker_id: 5,
                worker_name: 'Saman Kumara (Plumber)',
                worker_trade: 'plumber',
                scheduled_date: '2026-11-15',
                scheduled_time: '02:00 PM - 03:30 PM',
                worker_notes: 'Will replace rubber washer and inspect tap valve.',
                created_at: '2026-11-14 08:20'
            },
            {
                id: 4,
                request_code: 'REQ-2026-004',
                student_id: 7,
                student_name: 'Amaya Wickramasinghe',
                student_phone: '+94 72 777 8899',
                student_room: 'D113',
                category: 'electrical',
                title: 'Personal AC Installation Request',
                description: 'Student requested unauthorized AC unit repair.',
                location: 'Block A, 1st Floor, D113',
                priority: 'low',
                status: 'REJECTED',
                rejection_reason: 'Air conditioning units are not permitted in standard hostel rooms per hostel rule 4.2.',
                created_at: '2026-11-13 14:00'
            },
            {
                id: 5,
                request_code: 'REQ-2026-005',
                student_id: 6,
                student_name: 'Kasun Jayawardena',
                student_phone: '+94 70 666 7788',
                student_room: 'U112',
                category: 'electrical',
                title: 'Fluorescent Tube Light Blinking',
                description: 'Tube light in study corner keeps flickering continuously.',
                location: 'Block G, 2nd Floor, U112',
                priority: 'low',
                status: 'PENDING_REVIEW',
                created_at: '2026-11-14 09:45'
            },
            {
                id: 6,
                request_code: 'REQ-2026-006',
                student_id: 7,
                student_name: 'Amaya Wickramasinghe',
                student_phone: '+94 72 777 8899',
                student_room: 'D113',
                category: 'carpentry',
                title: 'Room Door Lock Jammed',
                description: 'The key won’t turn smoothly in the door lock.',
                location: 'Block B, 1st Floor, Room 112',
                priority: 'medium',
                status: 'UNDER_REVIEW',
                created_at: '2026-11-14 07:15'
            },
            {
                id: 7,
                request_code: 'REQ-2026-007',
                student_id: 6,
                student_name: 'Kasun Jayawardena',
                student_phone: '+94 70 666 7788',
                student_room: 'U112',
                category: 'electrical',
                title: 'Desk Study Lamp Socket Repair',
                description: 'Socket short-circuit repaired, tested with fuse replacement.',
                location: 'Block G, 2nd Floor, U112',
                priority: 'medium',
                status: 'COMPLETED',
                assigned_worker_id: 3,
                worker_name: 'Kamal Bandara (Electrician)',
                worker_trade: 'electrician',
                scheduled_date: '2026-11-13',
                scheduled_time: '11:00 AM',
                completed_at: '2026-11-13 11:45',
                worker_notes: 'Replaced internal socket contact plates and tested output.',
                rating: null, // Ready for student to submit star rating!
                student_feedback: '',
                created_at: '2026-11-12 08:30'
            },
            {
                id: 8,
                request_code: 'REQ-2026-008',
                student_id: 6,
                student_name: 'Kasun Jayawardena',
                student_phone: '+94 70 666 7788',
                student_room: 'U112',
                category: 'carpentry',
                title: 'Hostel Bed Wooden Slat Replacement',
                description: 'Middle wooden slat cracked and replaced with solid teak slat.',
                location: 'Block G, 2nd Floor, U112',
                priority: 'medium',
                status: 'COMPLETED',
                assigned_worker_id: 4,
                worker_name: 'Nimal Silva (Carpenter)',
                worker_trade: 'carpenter',
                scheduled_date: '2026-11-11',
                scheduled_time: '02:00 PM',
                completed_at: '2026-11-11 15:00', // Completed 3 days ago (< 7 days, active dashboard)
                worker_notes: 'Installed reinforced support slat and verified weight test.',
                rating: 5,
                student_feedback: 'Nimal fixed the bed quickly and tested it before leaving. Very polite!',
                rated_at: '2026-11-11 16:30',
                created_at: '2026-11-10 11:00'
            },
            {
                id: 9,
                request_code: 'REQ-2026-009',
                student_id: 7,
                student_name: 'Amaya Wickramasinghe',
                student_phone: '+94 72 777 8899',
                student_room: 'D113',
                category: 'plumbing',
                title: 'Bathroom Overhead Shower Head Replacement',
                description: 'Severe limescale blockage causing zero water flow.',
                location: 'Block A, 1st Floor, D113',
                priority: 'low',
                status: 'COMPLETED',
                assigned_worker_id: 5,
                worker_name: 'Saman Kumara (Plumber)',
                worker_trade: 'plumber',
                scheduled_date: '2026-10-25',
                scheduled_time: '10:00 AM',
                completed_at: '2026-10-25 10:45', // Completed 20 days ago (> 7 days, auto-archived to HISTORY!)
                worker_notes: 'Replaced shower rose with new brass fitting.',
                rating: 5,
                student_feedback: 'Excellent work, high water pressure restored!',
                rated_at: '2026-10-25 12:00',
                created_at: '2026-10-24 09:00'
            }
        ];
        localStorage.setItem('hostel_requests', JSON.stringify(requests));
    } else {
        // Ensure upgraded requests (with completed and rated demo records) are present
        const currentReqs = JSON.parse(localStorage.getItem('hostel_requests') || '[]');
        if (!currentReqs.some(r => r.id === 7 || r.id === 8)) {
            const extra = [
                {
                    id: 7,
                    request_code: 'REQ-2026-007',
                    student_id: 6,
                    student_name: 'Kasun Jayawardena',
                    student_phone: '+94 70 666 7788',
                    student_room: 'U112',
                    category: 'electrical',
                    title: 'Desk Study Lamp Socket Repair',
                    description: 'Socket short-circuit repaired, tested with fuse replacement.',
                    location: 'Block G, 2nd Floor, U112',
                    priority: 'medium',
                    status: 'COMPLETED',
                    assigned_worker_id: 3,
                    worker_name: 'Kamal Bandara (Electrician)',
                    worker_trade: 'electrician',
                    scheduled_date: '2026-11-13',
                    scheduled_time: '11:00 AM',
                    completed_at: '2026-11-13 11:45',
                    worker_notes: 'Replaced internal socket contact plates and tested output.',
                    rating: null,
                    student_feedback: '',
                    created_at: '2026-11-12 08:30'
                },
                {
                    id: 8,
                    request_code: 'REQ-2026-008',
                    student_id: 6,
                    student_name: 'Kasun Jayawardena',
                    student_phone: '+94 70 666 7788',
                    student_room: 'U112',
                    category: 'carpentry',
                    title: 'Hostel Bed Wooden Slat Replacement',
                    description: 'Middle wooden slat cracked and replaced with solid teak slat.',
                    location: 'Block G, 2nd Floor, U112',
                    priority: 'medium',
                    status: 'COMPLETED',
                    assigned_worker_id: 4,
                    worker_name: 'Nimal Silva (Carpenter)',
                    worker_trade: 'carpenter',
                    scheduled_date: '2026-11-11',
                    scheduled_time: '02:00 PM',
                    completed_at: '2026-11-11 15:00',
                    worker_notes: 'Installed reinforced support slat and verified weight test.',
                    rating: 5,
                    student_feedback: 'Nimal fixed the bed quickly and tested it before leaving. Very polite!',
                    rated_at: '2026-11-11 16:30',
                    created_at: '2026-11-10 11:00'
                },
                {
                    id: 9,
                    request_code: 'REQ-2026-009',
                    student_id: 7,
                    student_name: 'Amaya Wickramasinghe',
                    student_phone: '+94 72 777 8899',
                    student_room: 'D113',
                    category: 'plumbing',
                    title: 'Bathroom Overhead Shower Head Replacement',
                    description: 'Severe limescale blockage causing zero water flow.',
                    location: 'Block A, 1st Floor, D113',
                    priority: 'low',
                    status: 'COMPLETED',
                    assigned_worker_id: 5,
                    worker_name: 'Saman Kumara (Plumber)',
                    worker_trade: 'plumber',
                    scheduled_date: '2026-10-25',
                    scheduled_time: '10:00 AM',
                    completed_at: '2026-10-25 10:45',
                    worker_notes: 'Replaced shower rose with new brass fitting.',
                    rating: 5,
                    student_feedback: 'Excellent work, high water pressure restored!',
                    rated_at: '2026-10-25 12:00',
                    created_at: '2026-10-24 09:00'
                }
            ];
            localStorage.setItem('hostel_requests', JSON.stringify([...currentReqs, ...extra]));
        }
    }
}

// -------------------------------------------------------------
// 2. Initial Public Portal Content Seeding (Admin Editable)
// -------------------------------------------------------------
function initPortalContent() {
    if (!localStorage.getItem('hostel_portal_content')) {
        const defaultContent = {
            facility_showcase: {
                title: "University Hostel Facilities & Maintenance System",
                description: "The University Hostel provides modern residential facilities for undergraduates. To maintain standard living conditions, our automated maintenance system allows students to report faults immediately with photos and exact room numbers.",
                electrical_text: "Ceiling fans, room lights, socket outlets, main breakers.",
                carpentry_text: "Beds, study tables, chairs, door locks, cupboard hinges.",
                plumbing_text: "Water taps, bathroom drainage, water tank lines, low pressure fixes.",
                warden_text: "Fast approvals, policy verification, technician assignment.",
                image_caption: "📍 Official University Hostel Residential Complex"
            },
            user_roles: {
                title: "System Architecture & User Roles (5 Roles)",
                subtitle: "Designed strictly per Activity Swimlane & State Transition Diagrams",
                student_desc: "Submits complaints with photos & location, tracks scheduled time, and edits their student profile.",
                warden_desc: "Reviews requests, assigns skilled workers (Electrician, Carpenter, Plumber), rejects policy violations.",
                worker_desc: "Provides inspection date & time slot, completes repair work upon fix verification.",
                admin_desc: "Manages user accounts, trades, roles, public portal content, and maintenance records.",
                guest_desc: "Views public hostel maintenance rules, emergency guidelines, and registers for student access."
            },
            guidelines: {
                title: "Hostel Maintenance Regulations & Guest Guidelines",
                safety_text: "Only certified campus technicians are permitted to open electrical fixtures. Students must not tamper with wiring.",
                prohibited_text: "High wattage immersion heaters, hotplates, and private air conditioners are strictly forbidden; requests related to unauthorized items will be REJECTED.",
                attendance_text: "When a repair slot is scheduled by a technician, the resident student or a room partner must remain present."
            }
        };
        localStorage.setItem('hostel_portal_content', JSON.stringify(defaultContent));
    }
}

initMockData();
initPortalContent();

// -------------------------------------------------------------
// 3. Api Object Definition
// -------------------------------------------------------------
const Api = {
    // ---------------------------------------------------------
    // Authentication
    // ---------------------------------------------------------
    async login(username, password) {
        // Fast instant login for local file usage
        if (typeof window !== 'undefined' && window.location.protocol === 'file:') {
            return this.mockLogin(username, password);
        }

        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 800);
            const res = await fetch(`${API_BASE}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password }),
                signal: controller.signal
            });
            clearTimeout(timeoutId);
            const data = await res.json();
            if (data.success) {
                localStorage.setItem('currentUser', JSON.stringify(data.user));
                return data;
            }
        } catch (e) {
            console.warn('Backend server not responding, falling back to local simulation mode:', e.message);
        }

        return this.mockLogin(username, password);
    },

    mockLogin(username, password) {
        initMockData();
        const term = (username || '').toLowerCase().trim();

        // Guest users cannot sign in (guests only view public portal and register as students)
        if (term === 'guest' || term === 'guest_user') {
            return {
                success: false,
                message: 'Guest users do not have a sign-in account. Guests can view the public portal and register as a student.'
            };
        }

        const users = JSON.parse(localStorage.getItem('hostel_users') || '[]');
        const user = users.find(u => 
            u.username.toLowerCase() === term ||
            (u.email && u.email.toLowerCase() === term) ||
            u.role.toLowerCase() === term ||
            (u.worker_trade && u.worker_trade.toLowerCase() === term) ||
            (term === 'kasun' && u.username === 'student_kasun') ||
            (term === 'warden' && u.username === 'subwarden') ||
            (term === 'kamal' && u.username === 'electrician_kamal') ||
            (term === 'nimal' && u.username === 'carpenter_nimal') ||
            (term === 'saman' && u.username === 'plumber_saman') ||
            (term === 'plumber' && u.worker_trade === 'plumber')
        );

        if (user) {
            if (user.role === 'guest') {
                return {
                    success: false,
                    message: 'Guest users do not have a sign-in account. Guests can view the public portal and register as a student.'
                };
            }
            localStorage.setItem('currentUser', JSON.stringify(user));
            return { success: true, message: `Welcome back, ${user.full_name}!`, user };
        }
        return { success: false, message: 'Invalid username or password' };
    },

    // ---------------------------------------------------------
    // Student Registration (Only Students Can Register)
    // ---------------------------------------------------------
    async register(data) {
        initMockData();
        const users = JSON.parse(localStorage.getItem('hostel_users') || '[]');
        const username = (data.username || '').trim().toLowerCase();

        if (!username || !data.password || !data.fullName) {
            return { success: false, message: 'Please fill all required fields.' };
        }

        const exists = users.find(u => u.username.toLowerCase() === username);
        if (exists) {
            return { success: false, message: 'Username is already taken. Please choose another.' };
        }

        // Strictly register as student
        const newUser = {
            id: Date.now(),
            username: (data.username || '').trim(),
            password: (data.password || 'password123').trim(),
            full_name: (data.fullName || '').trim(),
            email: (data.email || `${username}@student.ac.lk`).trim(),
            role: 'student', // ONLY STUDENTS CAN REGISTER
            worker_trade: 'none',
            phone: (data.phone || '').trim(),
            hostel_block: data.hostelBlock || 'Block A',
            room_number: (data.roomNumber || 'Room 101').trim(),
            status: 'active'
        };

        users.push(newUser);
        localStorage.setItem('hostel_users', JSON.stringify(users));

        // Sync with backend if reachable
        try {
            if (typeof window !== 'undefined' && window.location.protocol !== 'file:') {
                fetch(`${API_BASE}/register`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(newUser)
                }).catch(() => {});
            }
        } catch (e) {}

        return { success: true, message: 'Registration successful! You can now sign in.', user: newUser };
    },

    // ---------------------------------------------------------
    // Student Profile Management (Edit Profile After Registration)
    // ---------------------------------------------------------
    async updateProfile(userId, profileData) {
        initMockData();
        const users = JSON.parse(localStorage.getItem('hostel_users') || '[]');
        const idx = users.findIndex(u => u.id === Number(userId));

        if (idx === -1) {
            return { success: false, message: 'User record not found.' };
        }

        if (profileData.fullName) users[idx].full_name = profileData.fullName.trim();
        if (profileData.email) users[idx].email = profileData.email.trim();
        if (profileData.phone) users[idx].phone = profileData.phone.trim();
        if (profileData.hostelBlock) users[idx].hostel_block = profileData.hostelBlock;
        if (profileData.roomNumber) users[idx].room_number = profileData.roomNumber.trim();
        if (profileData.department) users[idx].department = profileData.department.trim();
        if (profileData.workerTrade) users[idx].worker_trade = profileData.workerTrade.trim();
        if (profileData.password && profileData.password.trim() !== '') {
            users[idx].password = profileData.password.trim();
        }

        localStorage.setItem('hostel_users', JSON.stringify(users));

        // If updating the currently logged-in user, refresh session
        const current = this.getCurrentUser();
        if (current && Number(current.id) === Number(userId)) {
            const updatedCurrent = { ...current, ...users[idx] };
            localStorage.setItem('currentUser', JSON.stringify(updatedCurrent));
        }

        return { success: true, message: 'Account details updated successfully!', user: users[idx] };
    },

    getCurrentUser() {
        const u = localStorage.getItem('currentUser');
        return u ? JSON.parse(u) : null;
    },

    logout() {
        localStorage.removeItem('currentUser');
        window.location.href = 'login.html';
    },

    checkAuth(allowedRoles = []) {
        const user = this.getCurrentUser();
        if (!user) {
            window.location.href = 'login.html';
            return null;
        }
        if (allowedRoles.length > 0 && !allowedRoles.includes(user.role)) {
            alert(`Access Denied! Your role (${user.role}) is not authorized for this portal.`);
            this.redirectByRole(user.role);
            return null;
        }
        return user;
    },

    redirectByRole(role) {
        switch (role) {
            case 'student': window.location.href = 'student-dashboard.html'; break;
            case 'warden': window.location.href = 'warden-dashboard.html'; break;
            case 'worker': window.location.href = 'worker-dashboard.html'; break;
            case 'admin': window.location.href = 'admin-dashboard.html'; break;
            default: window.location.href = 'index.html';
        }
    },

    // ---------------------------------------------------------
    // Student Methods
    // ---------------------------------------------------------
    async getStudentRequests(studentId) {
        try {
            const res = await fetch(`${API_BASE}/student/requests?student_id=${studentId}`);
            const data = await res.json();
            if (data.success) return data.data;
        } catch (e) {}

        const all = JSON.parse(localStorage.getItem('hostel_requests') || '[]');
        return all.filter(r => r.student_id === studentId);
    },

    async submitRequest(formData) {
        try {
            const res = await fetch(`${API_BASE}/student/requests`, {
                method: 'POST',
                body: formData
            });
            const data = await res.json();
            if (data.success) return data;
        } catch (e) {}

        const all = JSON.parse(localStorage.getItem('hostel_requests') || '[]');
        const newId = all.length > 0 ? Math.max(...all.map(r => r.id)) + 1 : 1;
        const newCode = `REQ-2026-${String(newId).padStart(3, '0')}`;

        const reqObj = {
            id: newId,
            request_code: newCode,
            status: 'PENDING_REVIEW',
            created_at: new Date().toISOString().replace('T', ' ').substring(0, 16)
        };

        if (typeof FormData !== 'undefined' && formData instanceof FormData) {
            for (let pair of formData.entries()) {
                if (pair[0] === 'photo' && pair[1].name) {
                    reqObj.photo_path = URL.createObjectURL(pair[1]);
                } else {
                    reqObj[pair[0]] = pair[1];
                }
            }
        } else if (typeof formData === 'object' && formData !== null) {
            Object.assign(reqObj, formData);
            if (formData.photo_preview) {
                reqObj.photo_path = formData.photo_preview;
            }
        }

        reqObj.student_id = Number(reqObj.student_id);
        all.unshift(reqObj);
        localStorage.setItem('hostel_requests', JSON.stringify(all));
        return { success: true, message: 'Maintenance request submitted successfully!', request: reqObj };
    },

    // ---------------------------------------------------------
    // 7-Day Completed Requests Archive & History Management
    // ---------------------------------------------------------
    isOlderThan7Days(req) {
        if (req.status !== 'COMPLETED') return false;
        const compDateStr = req.completed_at || req.scheduled_date || req.created_at;
        if (!compDateStr) return false;
        const parts = compDateStr.split(' ')[0].split('-');
        if (parts.length === 3) {
            const compTime = new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2])).getTime();
            const now = Date.now();
            const diffDays = (now - compTime) / (1000 * 60 * 60 * 24);
            return diffDays >= 7;
        }
        return false;
    },

    getActiveRequests() {
        initMockData();
        const all = JSON.parse(localStorage.getItem('hostel_requests') || '[]');
        return all.filter(r => !this.isOlderThan7Days(r));
    },

    getRequestHistory() {
        initMockData();
        const all = JSON.parse(localStorage.getItem('hostel_requests') || '[]');
        return all.filter(r => r.status === 'COMPLETED');
    },

    // ---------------------------------------------------------
    // Student Star Rating System
    // ---------------------------------------------------------
    rateRequest(reqId, rating, feedback) {
        initMockData();
        const all = JSON.parse(localStorage.getItem('hostel_requests') || '[]');
        const req = all.find(r => r.id === Number(reqId));
        if (!req) return { success: false, message: 'Request not found' };

        req.rating = Number(rating);
        req.student_feedback = (feedback || '').trim();
        req.rated_at = new Date().toISOString().replace('T', ' ').substring(0, 16);
        localStorage.setItem('hostel_requests', JSON.stringify(all));
        return { success: true, message: 'Thank you! Rating & feedback submitted successfully.', request: req };
    },

    getWorkerRatingStats(workerId) {
        initMockData();
        const all = JSON.parse(localStorage.getItem('hostel_requests') || '[]');
        const ratedTasks = all.filter(r => r.assigned_worker_id === Number(workerId) && r.rating);
        if (ratedTasks.length === 0) {
            return { average: '5.0', count: 0, ratedTasks: [] };
        }
        const total = ratedTasks.reduce((sum, r) => sum + Number(r.rating), 0);
        const avg = (total / ratedTasks.length).toFixed(1);
        return { average: avg, count: ratedTasks.length, ratedTasks };
    },

    // ---------------------------------------------------------
    // Sub Warden Methods
    // ---------------------------------------------------------
    async getWardenRequests(includeArchived = false) {
        try {
            const res = await fetch(`${API_BASE}/warden/requests`);
            const data = await res.json();
            if (data.success) return data.data;
        } catch (e) {}

        const all = JSON.parse(localStorage.getItem('hostel_requests') || '[]');
        if (includeArchived) return all;
        // Automatically remove completed maintenance requests from dashboard after 7 days!
        return all.filter(r => !this.isOlderThan7Days(r));
    },

    async reviewRequest(reqId) {
        try {
            const res = await fetch(`${API_BASE}/warden/requests/${reqId}/review`, { method: 'PUT' });
            const data = await res.json();
            if (data.success) return data;
        } catch (e) {}

        const all = JSON.parse(localStorage.getItem('hostel_requests') || '[]');
        const item = all.find(r => r.id === reqId);
        if (item && item.status === 'PENDING_REVIEW') {
            item.status = 'UNDER_REVIEW';
            localStorage.setItem('hostel_requests', JSON.stringify(all));
        }
        return { success: true, message: 'Request status changed to UNDER_REVIEW' };
    },

    async rejectRequest(reqId, reason) {
        try {
            const res = await fetch(`${API_BASE}/warden/requests/${reqId}/reject`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ reason })
            });
            const data = await res.json();
            if (data.success) return data;
        } catch (e) {}

        const all = JSON.parse(localStorage.getItem('hostel_requests') || '[]');
        const item = all.find(r => r.id === reqId);
        if (item) {
            item.status = 'REJECTED';
            item.rejection_reason = reason;
        }
        localStorage.setItem('hostel_requests', JSON.stringify(all));
        return { success: true, message: 'Request REJECTED with reason recorded' };
    },

    async assignWorker(reqId, workerId) {
        try {
            const res = await fetch(`${API_BASE}/warden/requests/${reqId}/assign`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ worker_id: workerId })
            });
            const data = await res.json();
            if (data.success) return data;
        } catch (e) {}

        const all = JSON.parse(localStorage.getItem('hostel_requests') || '[]');
        const users = JSON.parse(localStorage.getItem('hostel_users') || '[]');
        const item = all.find(r => r.id === reqId);
        const worker = users.find(u => u.id === Number(workerId));

        if (item && worker) {
            item.assigned_worker_id = worker.id;
            item.worker_name = worker.full_name;
            item.worker_trade = worker.worker_trade;
            item.status = 'ASSIGNED';
        }
        localStorage.setItem('hostel_requests', JSON.stringify(all));
        return { success: true, message: `Request successfully ASSIGNED to ${worker ? worker.full_name : 'Staff'}` };
    },

    // ---------------------------------------------------------
    // Maintenance Worker Methods
    // ---------------------------------------------------------
    async getWorkerTasks(workerId) {
        try {
            const res = await fetch(`${API_BASE}/worker/tasks?worker_id=${workerId}`);
            const data = await res.json();
            if (data.success) return data.data;
        } catch (e) {}

        const all = JSON.parse(localStorage.getItem('hostel_requests') || '[]');
        return all.filter(r => r.assigned_worker_id === workerId);
    },

    async scheduleRepair(reqId, scheduledDate, scheduledTime, workerNotes) {
        try {
            const res = await fetch(`${API_BASE}/worker/tasks/${reqId}/schedule`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    scheduled_date: scheduledDate,
                    scheduled_time: scheduledTime,
                    worker_notes: workerNotes
                })
            });
            const data = await res.json();
            if (data.success) return data;
        } catch (e) {}

        const all = JSON.parse(localStorage.getItem('hostel_requests') || '[]');
        const item = all.find(r => r.id === reqId);
        if (item) {
            item.scheduled_date = scheduledDate;
            item.scheduled_time = scheduledTime;
            item.worker_notes = workerNotes;
            item.status = 'SCHEDULED';
        }
        localStorage.setItem('hostel_requests', JSON.stringify(all));
        return { success: true, message: 'Repair scheduled! Date & Time notified to Student & Warden' };
    },

    async completeRepair(reqId, notes) {
        try {
            const res = await fetch(`${API_BASE}/worker/tasks/${reqId}/complete`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ worker_notes: notes })
            });
            const data = await res.json();
            if (data.success) return data;
        } catch (e) {}

        const all = JSON.parse(localStorage.getItem('hostel_requests') || '[]');
        const item = all.find(r => r.id === reqId);
        if (item) {
            item.status = 'COMPLETED';
            item.completed_at = new Date().toISOString().replace('T', ' ').substring(0, 16);
            item.worker_notes = notes || 'Maintenance successfully finished.';
        }
        localStorage.setItem('hostel_requests', JSON.stringify(all));
        return { success: true, message: 'Maintenance marked as COMPLETED!' };
    },

    // ---------------------------------------------------------
    // Admin & General Methods (Manage Users & Content)
    // ---------------------------------------------------------
    getUsers() {
        initMockData();
        return JSON.parse(localStorage.getItem('hostel_users') || '[]');
    },

    getWorkers() {
        const users = this.getUsers();
        return users.filter(u => u.role === 'worker');
    },

    addUser(userData) {
        const users = this.getUsers();
        const newUser = {
            id: Date.now(),
            ...userData,
            status: 'active'
        };
        users.push(newUser);
        localStorage.setItem('hostel_users', JSON.stringify(users));
        return { success: true, message: 'User added successfully', user: newUser };
    },

    deleteUser(id) {
        let users = this.getUsers();
        users = users.filter(u => u.id !== id);
        localStorage.setItem('hostel_users', JSON.stringify(users));
        return { success: true, message: 'User deleted' };
    },

    // ---------------------------------------------------------
    // Public Portal Content Management (Admin Can Edit)
    // ---------------------------------------------------------
    getPortalContent() {
        initPortalContent();
        return JSON.parse(localStorage.getItem('hostel_portal_content') || '{}');
    },

    updatePortalContent(newContent) {
        initPortalContent();
        const current = this.getPortalContent();
        const merged = { ...current, ...newContent };
        localStorage.setItem('hostel_portal_content', JSON.stringify(merged));
        return { success: true, message: 'Public portal content updated successfully!' };
    },

    resetPortalContent() {
        localStorage.removeItem('hostel_portal_content');
        initPortalContent();
        return { success: true, message: 'Public portal content restored to defaults!' };
    }
};

// Export globally for browser scripts
window.Api = Api;
window.AppAPI = Api;
