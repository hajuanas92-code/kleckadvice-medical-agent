package com.example.demo.model;
import jakarta.persistence.*;

@Entity
@Table(name = "users") // Creates a table named "users" in PostgreSQL
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, nullable = false)
    private String username;

    @Column(nullable = false)
    private String password; // In a production app, this would be hashed

    // Constructor for Spring Boot
    public User() {}

    // Constructor for us to use
    public User(String username, String password) {
        this.username = username;
        this.password = password;
    }

    // Getters and Setters (so other files can read/write data)
    public Long getId() { return id; }
    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }
    public String getPassword() { return password; }
    public void setPassword(String password) { this.password = password; }
}