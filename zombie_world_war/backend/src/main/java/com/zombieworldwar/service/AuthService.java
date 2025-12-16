package com.zombieworldwar.service;

import com.zombieworldwar.dto.AuthResponse;
import com.zombieworldwar.dto.LoginRequest;
import com.zombieworldwar.dto.RegisterRequest;

/**
 * Authentication service interface.
 * Requirements: 8.1, 8.2, 8.3, 8.4
 */
public interface AuthService {
    
    /**
     * Register a new user.
     * Requirements: 8.1 - Validate email format and password strength
     */
    AuthResponse register(RegisterRequest request);
    
    /**
     * Login user with credentials.
     * Requirements: 8.2, 8.3 - Issue JWT token, opaque error messages
     */
    AuthResponse login(LoginRequest request);
    
    /**
     * Refresh JWT token.
     * Requirements: 8.4 - Handle token expiration
     */
    AuthResponse refreshToken(String token);
}
