package com.hostel.maintenance.controller;

import com.hostel.maintenance.model.MaintenanceRequest;
import com.hostel.maintenance.model.RequestStatus;
import com.hostel.maintenance.model.User;
import com.hostel.maintenance.repository.MaintenanceRequestRepository;
import com.hostel.maintenance.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.time.LocalDate;
import java.util.*;

@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "*")
public class MaintenanceController {

    @Autowired
    private MaintenanceRequestRepository requestRepository;

    @Autowired
    private UserRepository userRepository;

    // -------------------------------------------------------------
    // Authentication
    // -------------------------------------------------------------
    @PostMapping("/auth/login")
    public ResponseEntity<?> login(@RequestBody Map<String, String> creds) {
        String username = creds.get("username");
        String password = creds.get("password");

        Optional<User> userOpt = userRepository.findByUsername(username);
        if (userOpt.isPresent() && userOpt.get().getPasswordHash().equals(password)) {
            User user = userOpt.get();
            Map<String, Object> resp = new HashMap<>();
            resp.put("success", true);
            resp.put("message", "Welcome " + user.getFullName());
            resp.put("user", user);
            return ResponseEntity.ok(resp);
        }
        return ResponseEntity.status(401).body(Map.of("success", false, "message", "Invalid credentials"));
    }

    // -------------------------------------------------------------
    // Student: View & Submit Maintenance Request
    // -------------------------------------------------------------
    @GetMapping("/student/requests")
    public ResponseEntity<?> getStudentRequests(@RequestParam Long student_id) {
        return ResponseEntity.ok(Map.of("success", true, "data", requestRepository.findByStudentIdOrderByIdDesc(student_id)));
    }

    @PostMapping("/student/requests")
    public ResponseEntity<?> submitRequest(
            @RequestParam("student_id") Long studentId,
            @RequestParam("category") String category,
            @RequestParam("title") String title,
            @RequestParam("description") String description,
            @RequestParam("location") String location,
            @RequestParam(value = "priority", defaultValue = "medium") String priority,
            @RequestParam(value = "photo", required = false) MultipartFile photo) throws IOException {

        User student = userRepository.findById(studentId).orElseThrow();
        MaintenanceRequest req = new MaintenanceRequest();
        req.setRequestCode("REQ-" + System.currentTimeMillis() % 100000);
        req.setStudent(student);
        req.setCategory(category);
        req.setTitle(title);
        req.setDescription(description);
        req.setLocation(location);
        req.setPriority(priority);
        req.setStatus(RequestStatus.PENDING_REVIEW);

        if (photo != null && !photo.isEmpty()) {
            String uploadDir = System.getProperty("user.dir") + "/uploads/";
            new File(uploadDir).mkdirs();
            String fileName = "req_" + studentId + "_" + System.currentTimeMillis() + "_" + photo.getOriginalFilename();
            photo.transferTo(new File(uploadDir + fileName));
            req.setPhotoPath("uploads/" + fileName);
        }

        requestRepository.save(req);
        return ResponseEntity.ok(Map.of("success", true, "message", "Request submitted successfully! PENDING_REVIEW"));
    }

    // -------------------------------------------------------------
    // Sub Warden: Review, Reject, Assign
    // -------------------------------------------------------------
    @GetMapping("/warden/requests")
    public ResponseEntity<?> getWardenRequests(@RequestParam(value = "status", required = false) String status) {
        if (status != null && !status.equalsIgnoreCase("ALL")) {
            return ResponseEntity.ok(Map.of("success", true, "data", requestRepository.findByStatusOrderByIdDesc(RequestStatus.valueOf(status))));
        }
        return ResponseEntity.ok(Map.of("success", true, "data", requestRepository.findAllByOrderByIdDesc()));
    }

    @PostMapping("/warden/requests/{id}/review")
    public ResponseEntity<?> reviewRequest(@PathVariable Long id) {
        MaintenanceRequest req = requestRepository.findById(id).orElseThrow();
        req.setStatus(RequestStatus.UNDER_REVIEW);
        requestRepository.save(req);
        return ResponseEntity.ok(Map.of("success", true, "message", "Marked as UNDER_REVIEW"));
    }

    @PostMapping("/warden/requests/{id}/reject")
    public ResponseEntity<?> rejectRequest(@PathVariable Long id, @RequestBody Map<String, String> body) {
        MaintenanceRequest req = requestRepository.findById(id).orElseThrow();
        req.setStatus(RequestStatus.REJECTED);
        req.setRejectionReason(body.getOrDefault("reason", "Rejected by Warden"));
        requestRepository.save(req);
        return ResponseEntity.ok(Map.of("success", true, "message", "Request REJECTED"));
    }

    @PostMapping("/warden/requests/{id}/assign")
    public ResponseEntity<?> assignWorker(@PathVariable Long id, @RequestBody Map<String, Long> body) {
        MaintenanceRequest req = requestRepository.findById(id).orElseThrow();
        User worker = userRepository.findById(body.get("worker_id")).orElseThrow();
        User warden = userRepository.findById(body.get("warden_id")).orElseThrow();

        req.setAssignedWorker(worker);
        req.setAssignedByWarden(warden);
        req.setStatus(RequestStatus.ASSIGNED);
        requestRepository.save(req);
        return ResponseEntity.ok(Map.of("success", true, "message", "Assigned to worker!"));
    }

    // -------------------------------------------------------------
    // Maintenance Worker: View Tasks, Schedule Date/Time, Complete
    // -------------------------------------------------------------
    @GetMapping("/worker/tasks")
    public ResponseEntity<?> getWorkerTasks(@RequestParam Long worker_id) {
        return ResponseEntity.ok(Map.of("success", true, "data", requestRepository.findByAssignedWorkerIdOrderByIdDesc(worker_id)));
    }

    @PostMapping("/worker/tasks/{id}/schedule")
    public ResponseEntity<?> scheduleTask(@PathVariable Long id, @RequestBody Map<String, String> body) {
        MaintenanceRequest req = requestRepository.findById(id).orElseThrow();
        req.setScheduledDate(LocalDate.parse(body.get("scheduled_date")));
        req.setScheduledTime(body.get("scheduled_time"));
        req.setWorkerNotes(body.getOrDefault("worker_notes", ""));
        req.setStatus(RequestStatus.SCHEDULED);
        requestRepository.save(req);
        return ResponseEntity.ok(Map.of("success", true, "message", "Repair SCHEDULED! Date/Time sent to Student & Warden"));
    }

    @PostMapping("/worker/tasks/{id}/complete")
    public ResponseEntity<?> completeTask(@PathVariable Long id, @RequestBody Map<String, String> body) {
        MaintenanceRequest req = requestRepository.findById(id).orElseThrow();
        req.setWorkerNotes(body.getOrDefault("worker_notes", "Work Completed"));
        req.setStatus(RequestStatus.COMPLETED);
        requestRepository.save(req);
        return ResponseEntity.ok(Map.of("success", true, "message", "Work marked as COMPLETED!"));
    }

    // -------------------------------------------------------------
    // Admin: Users list
    // -------------------------------------------------------------
    @GetMapping("/admin/users")
    public ResponseEntity<?> getAllUsers() {
        return ResponseEntity.ok(Map.of("success", true, "data", userRepository.findAll()));
    }
}
