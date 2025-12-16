package com.zombieworldwar.security;

import lombok.AllArgsConstructor;
import lombok.Getter;

import java.security.Principal;

/**
 * Principal object representing an authenticated user from JWT token.
 * Requirements: 8.5 - Associate operations with user account
 */
@Getter
@AllArgsConstructor
public class JwtUserPrincipal implements Principal {
    
    private final Long userId;
    private final String username;

    @Override
    public String getName() {
        return username;
    }
}
