package com.zombieworldwar.service.impl;

import com.zombieworldwar.dto.AuthResponse;
import com.zombieworldwar.dto.LoginRequest;
import com.zombieworldwar.dto.RegisterRequest;
import com.zombieworldwar.entity.User;
import com.zombieworldwar.repository.UserRepository;
import com.zombieworldwar.security.JwtTokenProvider;
import com.zombieworldwar.service.AuthService;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.Optional;
import java.util.regex.Pattern;

/**
 * Implementation of AuthService for user authentication.
 * Requirements: 8.1, 8.2, 8.3, 8.4
 */
@Service
public class AuthServiceImpl implements AuthService {

    private static final Pattern EMAIL_PATTERN = Pattern.compile(
            "^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$"
    );
    private static final int MIN_PASSWORD_LENGTH = 8;

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtTokenProvider jwtTokenProvider;

    public AuthServiceImpl(
            UserRepository userRepository,
            PasswordEncoder passwordEncoder,
            JwtTokenProvider jwtTokenProvider) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.jwtTokenProvider = jwtTokenProvider;
    }

    /**
     * Register a new user with email and password validation.
     * Requirements: 8.1 - Validate email format and password strength (minimum 8 characters)
     */
    @Override
    @Transactional
    public AuthResponse register(RegisterRequest request) {
        // Validate email format
        if (!isValidEmail(request.getEmail())) {
            return AuthResponse.builder()
                    .success(false)
                    .message("Invalid email format")
                    .build();
        }

        // Validate password strength
        if (!isValidPassword(request.getPassword())) {
            return AuthResponse.builder()
                    .success(false)
                    .message("Password must be at least 8 characters")
                    .build();
        }

        // Check if username already exists
        if (userRepository.existsByUsername(request.getUsername())) {
            return AuthResponse.builder()
                    .success(false)
                    .message("Username already exists")
                    .build();
        }

        // Check if email already exists
        if (userRepository.existsByEmail(request.getEmail())) {
            return AuthResponse.builder()
                    .success(false)
                    .message("Email already exists")
                    .build();
        }

        // Create new user
        User user = User.builder()
                .username(request.getUsername())
                .email(request.getEmail())
                .passwordHash(passwordEncoder.encode(request.getPassword()))
                .build();

        User savedUser = userRepository.save(user);

        // Generate JWT token
        String token = jwtTokenProvider.generateToken(savedUser.getId(), savedUser.getUsername());

        return AuthResponse.builder()
                .userId(savedUser.getId())
                .username(savedUser.getUsername())
                .token(token)
                .expiresIn(jwtTokenProvider.getExpirationMs())
                .success(true)
                .message("Registration successful")
                .build();
    }

    /**
     * Login user with credentials.
     * Requirements: 8.2 - Issue JWT token valid for 24 hours
     * Requirements: 8.3 - Return opaque error without revealing which field is incorrect
     */
    @Override
    @Transactional
    public AuthResponse login(LoginRequest request) {
        // Find user by username or email
        Optional<User> userOpt = userRepository.findByUsernameOrEmail(request.getUsernameOrEmail());

        if (userOpt.isEmpty()) {
            // Requirements: 8.3 - Opaque error message
            return AuthResponse.builder()
                    .success(false)
                    .message("Invalid credentials")
                    .build();
        }

        User user = userOpt.get();

        // Verify password
        if (!passwordEncoder.matches(request.getPassword(), user.getPasswordHash())) {
            // Requirements: 8.3 - Same opaque error message for wrong password
            return AuthResponse.builder()
                    .success(false)
                    .message("Invalid credentials")
                    .build();
        }

        // Update last login time
        user.setLastLoginAt(LocalDateTime.now());
        userRepository.save(user);

        // Generate JWT token (Requirements: 8.2 - 24 hour validity)
        String token = jwtTokenProvider.generateToken(user.getId(), user.getUsername());

        return AuthResponse.builder()
                .userId(user.getId())
                .username(user.getUsername())
                .token(token)
                .expiresIn(jwtTokenProvider.getExpirationMs())
                .success(true)
                .message("Login successful")
                .build();
    }

    /**
     * Refresh JWT token.
     * Requirements: 8.4 - Handle token expiration and refresh
     */
    @Override
    public AuthResponse refreshToken(String token) {
        // Remove "Bearer " prefix if present
        if (token != null && token.startsWith("Bearer ")) {
            token = token.substring(7);
        }

        // Validate current token
        if (token == null || !jwtTokenProvider.validateToken(token)) {
            return AuthResponse.builder()
                    .success(false)
                    .message("Invalid or expired token")
                    .build();
        }

        // Get user info from token
        Long userId = jwtTokenProvider.getUserIdFromToken(token);
        String username = jwtTokenProvider.getUsernameFromToken(token);

        // Verify user still exists
        if (!userRepository.existsById(userId)) {
            return AuthResponse.builder()
                    .success(false)
                    .message("User not found")
                    .build();
        }

        // Generate new token
        String newToken = jwtTokenProvider.generateToken(userId, username);

        return AuthResponse.builder()
                .userId(userId)
                .username(username)
                .token(newToken)
                .expiresIn(jwtTokenProvider.getExpirationMs())
                .success(true)
                .message("Token refreshed successfully")
                .build();
    }

    /**
     * Validate email format.
     * Requirements: 8.1 - Validate email format
     */
    public boolean isValidEmail(String email) {
        if (email == null || email.isBlank()) {
            return false;
        }
        return EMAIL_PATTERN.matcher(email).matches();
    }

    /**
     * Validate password strength.
     * Requirements: 8.1 - Password must be at least 8 characters
     */
    public boolean isValidPassword(String password) {
        if (password == null) {
            return false;
        }
        return password.length() >= MIN_PASSWORD_LENGTH;
    }
}
