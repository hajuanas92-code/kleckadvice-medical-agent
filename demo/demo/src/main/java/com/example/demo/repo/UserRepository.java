package com.example.demo.repo;

import com.example.demo.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface UserRepository extends JpaRepository<User, Long> {
    // Spring Boot automatically builds: SELECT * FROM users WHERE username = ?
    Optional<User> findByUsername(String username);
}