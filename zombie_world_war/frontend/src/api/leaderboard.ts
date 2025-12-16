import { apiClient } from './client'

/**
 * Leaderboard entry from the API
 * Requirements: 7.2
 */
export interface LeaderboardEntry {
  id: number
  userId: number
  playerName: string
  score: number
  waveReached: number
  zombiesKilled: number
  playTimeSeconds: number
  achievedAt: string
  rank: number
}

/**
 * Paginated response from the API
 */
export interface PageResponse<T> {
  content: T[]
  totalElements: number
  totalPages: number
  size: number
  number: number
  first: boolean
  last: boolean
}

/**
 * User rank information
 */
export interface UserRank {
  userId: number
  playerName: string
  highestScore: number
  rank: number
  waveReached: number
}

/**
 * Score submission request
 */
export interface ScoreSubmitRequest {
  score: number
  waveReached: number
  zombiesKilled: number
  playTimeSeconds: number
}

/**
 * Score submission response
 */
export interface ScoreResponse {
  success: boolean
  message: string
  entryId: number
  isTopTen: boolean
}

/**
 * Leaderboard API functions
 * Requirements: 7.1, 7.2, 7.3, 11.3
 */
export const leaderboardApi = {
  /**
   * Get top scores with pagination
   * Requirements: 7.2, 11.3
   */
  async getTopScores(page: number = 0, size: number = 20): Promise<PageResponse<LeaderboardEntry>> {
    const response = await apiClient.get<PageResponse<LeaderboardEntry>>('/leaderboard/top', {
      params: { page, size }
    })
    return response.data
  },

  /**
   * Submit a score to the leaderboard
   * Requirements: 7.1
   */
  async submitScore(scoreData: ScoreSubmitRequest): Promise<ScoreResponse> {
    const response = await apiClient.post<ScoreResponse>('/leaderboard/submit', scoreData)
    return response.data
  },

  /**
   * Get a user's rank
   * Requirements: 7.2
   */
  async getUserRank(userId: number): Promise<UserRank> {
    const response = await apiClient.get<UserRank>(`/leaderboard/rank/${userId}`)
    return response.data
  }
}
