package com.example.demo.controller;

import com.example.demo.dto.LoginRequest;
import com.example.demo.dto.AuditRequest;
import com.example.demo.model.User;
import com.example.demo.model.AuditLog;
import com.example.demo.repo.UserRepository;
import com.example.demo.repo.AuditLogRepository;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/auth")
public class AuthController {

    private final UserRepository userRepository;
    private final AuditLogRepository auditLogRepository;

    // Inject BOTH database helpers into the constructor
    public AuthController(UserRepository userRepository, AuditLogRepository auditLogRepository) {
        this.userRepository = userRepository;
        this.auditLogRepository = auditLogRepository;
    }

    @PostMapping("/register")
    public ResponseEntity<String> register(@RequestBody LoginRequest request) {
        if (userRepository.findByUsername(request.getUsername()).isPresent()) {
            return ResponseEntity.badRequest().body("{\"error\": \"Username is taken\"}");
        }
        User newUser = new User(request.getUsername(), request.getPassword());
        userRepository.save(newUser);
        
        // Audit log the registration!
        auditLogRepository.save(new AuditLog(request.getUsername(), "REGISTER", "Account created"));
        
        return ResponseEntity.ok("{\"message\": \"Registered successfully\"}");
    }

    @PostMapping("/login")
    public ResponseEntity<String> login(@RequestBody LoginRequest request) {
        Optional<User> userOpt = userRepository.findByUsername(request.getUsername());

        if (userOpt.isPresent() && userOpt.get().getPassword().equals(request.getPassword())) {
            // Audit log a successful login!
            auditLogRepository.save(new AuditLog(request.getUsername(), "LOGIN_SUCCESS", "Logged into system"));
            return ResponseEntity.ok("{\"message\": \"Login successful\"}");
        }

        return ResponseEntity.status(401).body("{\"error\": \"Invalid credentials\"}");
    }

    // 3. NEW: ENDPOINT TO SUBMIT AN AUDIT LOG FROM FRONTEND
    @PostMapping("/audit/log")
    public ResponseEntity<String> createAuditLog(@RequestBody AuditRequest request) {
        AuditLog log = new AuditLog(request.getUsername(), request.getAction(), request.getDetails());
        auditLogRepository.save(log);
        return ResponseEntity.ok("{\"message\": \"Action logged successfully\"}");
    }

    // 4. NEW: ENDPOINT TO FETCH SEPARATE DATA FOR EACH USER
    @GetMapping("/audit/history")
    public ResponseEntity<List<AuditLog>> getUserHistory(@RequestParam("username") String username) {
        // Fetches ONLY this specific user's logs, sorted by newest first
        List<AuditLog> history = auditLogRepository.findByUsernameOrderByTimestampDesc(username);
        return ResponseEntity.ok(history);
    }
}