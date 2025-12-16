package com.zombieworldwar.controller;

import com.zombieworldwar.dto.AuthResponse;
import com.zombieworldwar.dto.LoginRequest;
import com.zombieworldwar.dto.RegisterRequest;
import com.zombieworldwar.service.AuthService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * Authentication controller for user registration, login, and token refresh.
 * Requirements: 8.1, 8.2, 8.4
 */
@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private final AuthService authService;

    public AuthController(AuthService authService) {
        this.authService = authService;
    }

    /**
     * Register a new user.
     * Requirements: 8.1 - Validate email format and password strength
     * 
     * @param request Registration request with username, email, and password
     * @return AuthResponse with JWT token on success
     */
    @PostMapping("/register")
    public ResponseEntity<AuthResponse> register(@Valid @RequestBody RegisterRequest request) {
        AuthResponse response = authService.register(request);
        
        if (response.getSuccess()) {
            return ResponseEntity.status(HttpStatus.CREATED).body(response);
        } else {
            return ResponseEntity.badRequest().body(response);
        }
    }

    /**
     * Login user with credentials.
     * Requirements: 8.2 - Issue JWT token valid for 24 hours
     * Requirements: 8.3 - Return opaque error without revealing which field is incorrect
     * 
     * @param request Login request with username/email and password
     * @return AuthResponse with JWT token on success
     */
    @PostMapping("/login")
    public ResponseEntity<AuthResponse> login(@Valid @RequestBody LoginRequest request) {
        AuthResponse response = authService.login(request);
        
        if (response.getSuccess()) {
            return ResponseEntity.ok(response);
        } else {
            // Requirements: 8.3 - Return 401 for invalid credentials
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(response);
        }
    }

    /**
     * Refresh JWT token.
     * Requirements: 8.4 - Handle token expiration and refresh
     * 
     * @param authHeader Authorization header with Bearer token
     * @return AuthResponse with new JWT token on success
     */
    @PostMapping("/refresh")
    public ResponseEntity<AuthResponse> refreshToken(
            @RequestHeader("Authorization") String authHeader) {
        AuthResponse response = authService.refreshToken(authHeader);
        
        if (response.getSuccess()) {
            return ResponseEntity.ok(response);
        } else {
            // Requirements: 8.4 - Return 401 for expired/invalid tokens
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(response);
        }
    }
}
