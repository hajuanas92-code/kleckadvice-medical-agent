package com.example.demo.dto;

public class AuditRequest {
    private String username;
    private String action;
    private String details;

    // Getters and Setters
    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }
    public String getAction() { return action; }
    public void setAction(String action) { this.action = action; }
    public String getDetails() { return details; }
}