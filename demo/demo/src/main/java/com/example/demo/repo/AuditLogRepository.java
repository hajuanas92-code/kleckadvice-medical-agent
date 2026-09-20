package com.example.demo.repo;

import com.example.demo.model.AuditLog;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface AuditLogRepository extends JpaRepository<AuditLog, Long> {
    // Finds logs for a specific person so users only see their own history
    List<AuditLog> findByUsernameOrderByTimestampDesc(String username);
}