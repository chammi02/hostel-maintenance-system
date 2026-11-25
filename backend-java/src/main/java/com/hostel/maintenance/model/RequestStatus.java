package com.hostel.maintenance.model;

/**
 * Request lifecycle states directly mapping the UML State Machine Diagram.
 */
public enum RequestStatus {
    PENDING_REVIEW,
    UNDER_REVIEW,
    ASSIGNED,
    SCHEDULED,
    IN_PROGRESS,
    COMPLETED,
    REJECTED
}
