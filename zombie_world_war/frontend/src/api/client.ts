import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios'

/**
 * API base URL - can be configured via environment variable
 */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api'

/**
 * Token storage keys
 */
const TOKEN_KEY = 'zww_token'
const REFRESH_TOKEN_KEY = 'zww_refresh_token'
const TOKEN_EXPIRY_KEY = 'zww_token_expiry'

/**
 * Flag to prevent multiple refresh requests
 */
let isRefreshing = false
let refreshSubscribers: ((token: string) => void)[] = []

/**
 * Subscribe to token refresh
 */
const subscribeTokenRefresh = (callback: (token: string) => void) => {
  refreshSubscribers.push(callback)
}

/**
 * Notify all subscribers with new token
 */
const onTokenRefreshed = (token: string) => {
  refreshSubscribers.forEach(callback => callback(token))
  refreshSubscribers = []
}

/**
 * Create axios instance with base configuration
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * Request interceptor - automatically attach JWT token
 * Requirement 8.4: JWT token auto-attachment
 */
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem(TOKEN_KEY)
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

/**
 * Response interceptor - handle token expiration and auto-refresh
 * Requirement 8.4: Token expiration handling and auto-refresh
 */
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }
    
    // Check if error is 401 Unauthorized and we haven't retried yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)
      
      // If no refresh token, reject immediately
      if (!refreshToken) {
        clearAuthData()
        return Promise.reject(error)
      }
      
      // If already refreshing, queue this request
      if (isRefreshing) {
        return new Promise((resolve) => {
          subscribeTokenRefresh((token: string) => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            resolve(apiClient(originalRequest))
          })
        })
      }
      
      originalRequest._retry = true
      isRefreshing = true
      
      try {
        // Attempt to refresh the token
        const response = await axios.post(`${API_BASE_URL}/auth/refresh`, null, {
          headers: {
            Authorization: `Bearer ${refreshToken}`,
          },
        })
        
        const { token, expiresIn } = response.data
        const expiryTime = Date.now() + expiresIn * 1000
        
        // Update stored tokens
        localStorage.setItem(TOKEN_KEY, token)
        localStorage.setItem(TOKEN_EXPIRY_KEY, expiryTime.toString())
        
        // Notify all queued requests
        onTokenRefreshed(token)
        
        // Retry original request with new token
        originalRequest.headers.Authorization = `Bearer ${token}`
        return apiClient(originalRequest)
      } catch (refreshError) {
        // Refresh failed, clear auth data
        clearAuthData()
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }
    
    return Promise.reject(error)
  }
)

/**
 * Clear all authentication data from localStorage
 */
function clearAuthData() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
  localStorage.removeItem(TOKEN_EXPIRY_KEY)
  localStorage.removeItem('zww_user')
}

export { apiClient, API_BASE_URL }
export default apiClient
