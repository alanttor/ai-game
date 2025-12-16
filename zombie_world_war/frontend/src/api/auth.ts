import apiClient from './client'
import type { AuthResponse } from '@/stores/authStore'

/**
 * Login request payload
 */
export interface LoginRequest {
  username: string
  password: string
}

/**
 * Register request payload
 */
export interface RegisterRequest {
  username: string
  email: string
  password: string
}

/**
 * Authentication API endpoints
 * Requirements: 8.1, 8.2, 8.4
 */
export const authApi = {
  /**
   * Login with username and password
   * Requirement 8.2: Issue JWT token valid for 24 hours
   */
  async login(data: LoginRequest): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/login', data)
    return response.data
  },

  /**
   * Register new user account
   * Requirement 8.1: Validate email format and password strength
   */
  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/register', data)
    return response.data
  },

  /**
   * Refresh JWT token
   * Requirement 8.4: Token refresh before expiration
   */
  async refreshToken(refreshToken: string): Promise<{ token: string; expiresIn: number }> {
    const response = await apiClient.post('/auth/refresh', null, {
      headers: {
        Authorization: `Bearer ${refreshToken}`,
      },
    })
    return response.data
  },

  /**
   * Logout - clear tokens on client side
   * Note: Backend may also invalidate the token
   */
  async logout(): Promise<void> {
    try {
      await apiClient.post('/auth/logout')
    } catch {
      // Ignore errors on logout - we'll clear local data anyway
    }
  },
}

export default authApi
