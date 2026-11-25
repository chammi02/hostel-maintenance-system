package com.hostel.maintenance.repository;

import com.hostel.maintenance.model.MaintenanceRequest;
import com.hostel.maintenance.model.RequestStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface MaintenanceRequestRepository extends JpaRepository<MaintenanceRequest, Long> {
    List<MaintenanceRequest> findByStudentIdOrderByIdDesc(Long studentId);
    List<MaintenanceRequest> findByAssignedWorkerIdOrderByIdDesc(Long workerId);
    List<MaintenanceRequest> findByStatusOrderByIdDesc(RequestStatus status);
    List<MaintenanceRequest> findAllByOrderByIdDesc();
}
