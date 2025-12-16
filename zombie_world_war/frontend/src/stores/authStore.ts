import { defineStore } from 'pinia'

/**
 * Authentication response from backend
 */
export interface AuthResponse {
  token: string
  refreshToken?: string
  expiresIn: number
  username: string
  userId: number
}

/**
 * User information stored in auth state
 */
export interface UserInfo {
  id: number
  username: string
  email?: string
}

/**
 * Auth store state interface
 */
interface AuthState {
  token: string | null
  refreshToken: string | null
  tokenExpiry: number | null
  user: UserInfo | null
  isLoading: boolean
  error: string | null
}

const TOKEN_KEY = 'zww_token'
const REFRESH_TOKEN_KEY = 'zww_refresh_token'
const TOKEN_EXPIRY_KEY = 'zww_token_expiry'
const USER_KEY = 'zww_user'

/**
 * Authentication Pinia Store
 * Manages JWT token storage, refresh, and user authentication state
 * Requirements: 8.2, 8.4
 */
export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    token: localStorage.getItem(TOKEN_KEY),
    refreshToken: localStorage.getItem(REFRESH_TOKEN_KEY),
    tokenExpiry: localStorage.getItem(TOKEN_EXPIRY_KEY) 
      ? parseInt(localStorage.getItem(TOKEN_EXPIRY_KEY)!, 10) 
      : null,
    user: localStorage.getItem(USER_KEY) 
      ? JSON.parse(localStorage.getItem(USER_KEY)!) 
      : null,
    isLoading: false,
    error: null,
  }),

  getters: {
    /**
     * Check if user is authenticated with valid token
     */
    isAuthenticated: (state): boolean => {
      if (!state.token || !state.tokenExpiry) return false
      return Date.now() < state.tokenExpiry
    },

    /**
     * Check if token is expired
     */
    isTokenExpired: (state): boolean => {
      if (!state.tokenExpiry) return true
      return Date.now() >= state.tokenExpiry
    },

    /**
     * Check if token needs refresh (within 5 minutes of expiry)
     */
    needsRefresh: (state): boolean => {
      if (!state.tokenExpiry) return false
      const fiveMinutes = 5 * 60 * 1000
      return Date.now() >= state.tokenExpiry - fiveMinutes
    },

    /**
     * Get current user info
     */
    currentUser: (state): UserInfo | null => state.user,

    /**
     * Get current JWT token
     */
    getToken: (state): string | null => state.token,
  },

  actions: {
    /**
     * Set authentication data after successful login/register
     */
    setAuth(response: AuthResponse) {
      const expiryTime = Date.now() + response.expiresIn * 1000
      
      this.token = response.token
      this.refreshToken = response.refreshToken || null
      this.tokenExpiry = expiryTime
      this.user = {
        id: response.userId,
        username: response.username,
      }
      this.error = null

      // Persist to localStorage
      localStorage.setItem(TOKEN_KEY, response.token)
      if (response.refreshToken) {
        localStorage.setItem(REFRESH_TOKEN_KEY, response.refreshToken)
      }
      localStorage.setItem(TOKEN_EXPIRY_KEY, expiryTime.toString())
      localStorage.setItem(USER_KEY, JSON.stringify(this.user))
    },

    /**
     * Update token after refresh
     */
    updateToken(token: string, expiresIn: number) {
      const expiryTime = Date.now() + expiresIn * 1000
      
      this.token = token
      this.tokenExpiry = expiryTime

      localStorage.setItem(TOKEN_KEY, token)
      localStorage.setItem(TOKEN_EXPIRY_KEY, expiryTime.toString())
    },

    /**
     * Clear all authentication data (logout)
     */
    clearAuth() {
      this.token = null
      this.refreshToken = null
      this.tokenExpiry = null
      this.user = null
      this.error = null

      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(REFRESH_TOKEN_KEY)
      localStorage.removeItem(TOKEN_EXPIRY_KEY)
      localStorage.removeItem(USER_KEY)
    },

    /**
     * Set loading state
     */
    setLoading(loading: boolean) {
      this.isLoading = loading
    },

    /**
     * Set error message
     */
    setError(error: string | null) {
      this.error = error
    },

    /**
     * Initialize auth state from localStorage
     * Called on app startup
     */
    initializeAuth() {
      const token = localStorage.getItem(TOKEN_KEY)
      const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)
      const tokenExpiry = localStorage.getItem(TOKEN_EXPIRY_KEY)
      const user = localStorage.getItem(USER_KEY)

      if (token && tokenExpiry) {
        this.token = token
        this.refreshToken = refreshToken
        this.tokenExpiry = parseInt(tokenExpiry, 10)
        this.user = user ? JSON.parse(user) : null

        // Check if token is expired
        if (this.isTokenExpired) {
          this.clearAuth()
        }
      }
    },
  },
})
