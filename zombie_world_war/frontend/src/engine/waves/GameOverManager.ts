import type { EventCallback } from '../types'

/**
 * Game over reason enumeration
 */
export enum GameOverReason {
  PLAYER_DEATH = 'playerDeath',
  QUIT = 'quit',
  TIMEOUT = 'timeout',
}

/**
 * Game over statistics
 */
export interface GameOverStats {
  finalScore: number
  waveReached: number
  totalZombiesKilled: number
  playTime: number
  reason: GameOverReason
}

/**
 * Final score display data for UI rendering
 * Requirements: 4.5
 */
export interface FinalScoreDisplay {
  score: string
  waveReached: number
  zombiesKilled: number
  playTime: string
  message: string
  isHighScore: boolean
}

/**
 * Game over events
 */
export enum GameOverEvent {
  GAME_OVER = 'gameOver:triggered',
  STATS_READY = 'gameOver:statsReady',
  RESTART = 'gameOver:restart',
  SCORE_DISPLAY_READY = 'gameOver:scoreDisplayReady',
}

/**
 * GameOverManager - Handles game over state and final score display
 * Requirements: 4.5
 */
export class GameOverManager {
  private _isGameOver: boolean = false
  private _stats: GameOverStats | null = null
  private _highScore: number = 0
  private eventListeners: Map<string, Set<EventCallback>> = new Map()

  /**
   * Check if game is over
   */
  get isGameOver(): boolean {
    return this._isGameOver
  }

  /**
   * Get game over statistics
   */
  get stats(): GameOverStats | null {
    return this._stats
  }

  /**
   * Get the final score
   * Requirements: 4.5
   */
  get finalScore(): number {
    return this._stats?.finalScore ?? 0
  }

  /**
   * Get the wave reached
   */
  get waveReached(): number {
    return this._stats?.waveReached ?? 0
  }

  /**
   * Get total zombies killed
   */
  get totalZombiesKilled(): number {
    return this._stats?.totalZombiesKilled ?? 0
  }

  /**
   * Set high score for comparison
   */
  setHighScore(score: number): void {
    this._highScore = score
  }

  /**
   * Check if current score is a high score
   */
  isNewHighScore(): boolean {
    if (!this._stats) return false
    return this._stats.finalScore > this._highScore
  }

  /**
   * Trigger game over
   * Requirements: 4.5
   * 
   * @param reason - Why the game ended
   * @param finalScore - Final score achieved
   * @param waveReached - Highest wave reached
   * @param totalZombiesKilled - Total zombies killed
   * @param playTime - Total play time in seconds
   */
  triggerGameOver(
    reason: GameOverReason,
    finalScore: number,
    waveReached: number,
    totalZombiesKilled: number,
    playTime: number
  ): void {
    if (this._isGameOver) return

    this._isGameOver = true
    this._stats = {
      finalScore,
      waveReached,
      totalZombiesKilled,
      playTime,
      reason,
    }

    this.emit(GameOverEvent.GAME_OVER, this._stats)
    this.emit(GameOverEvent.STATS_READY, this._stats)
    
    // Emit score display ready event with formatted data
    const displayData = this.getFinalScoreDisplay()
    this.emit(GameOverEvent.SCORE_DISPLAY_READY, displayData)
  }

  /**
   * Check if player should trigger game over
   * Requirements: 4.5
   * 
   * @param playerHealth - Current player health
   * @returns true if game should end
   */
  shouldTriggerGameOver(playerHealth: number): boolean {
    return playerHealth <= 0 && !this._isGameOver
  }

  /**
   * Get formatted final score string
   * Requirements: 4.5
   */
  getFormattedScore(): string {
    if (!this._stats) return '0'
    return this._stats.finalScore.toLocaleString()
  }

  /**
   * Get formatted play time string (MM:SS)
   */
  getFormattedPlayTime(): string {
    if (!this._stats) return '00:00'
    
    const totalSeconds = Math.floor(this._stats.playTime)
    const minutes = Math.floor(totalSeconds / 60)
    const seconds = totalSeconds % 60
    
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
  }

  /**
   * Get formatted play time string with hours (HH:MM:SS)
   */
  getFormattedPlayTimeLong(): string {
    if (!this._stats) return '00:00:00'
    
    const totalSeconds = Math.floor(this._stats.playTime)
    const hours = Math.floor(totalSeconds / 3600)
    const minutes = Math.floor((totalSeconds % 3600) / 60)
    const seconds = totalSeconds % 60
    
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
  }

  /**
   * Get game over message based on reason
   * Requirements: 4.5
   */
  getGameOverMessage(): string {
    if (!this._stats) return 'Game Over'
    
    switch (this._stats.reason) {
      case GameOverReason.PLAYER_DEATH:
        return 'You have been overwhelmed by the zombie horde!'
      case GameOverReason.QUIT:
        return 'You abandoned the fight...'
      case GameOverReason.TIMEOUT:
        return 'Time has run out!'
      default:
        return 'Game Over'
    }
  }

  /**
   * Get complete final score display data for UI
   * Requirements: 4.5
   */
  getFinalScoreDisplay(): FinalScoreDisplay {
    return {
      score: this.getFormattedScore(),
      waveReached: this._stats?.waveReached ?? 0,
      zombiesKilled: this._stats?.totalZombiesKilled ?? 0,
      playTime: this.getFormattedPlayTime(),
      message: this.getGameOverMessage(),
      isHighScore: this.isNewHighScore(),
    }
  }

  /**
   * Get summary text for the game over screen
   * Requirements: 4.5
   */
  getSummaryText(): string {
    if (!this._stats) return 'No game data available'
    
    const lines = [
      `Final Score: ${this.getFormattedScore()}`,
      `Wave Reached: ${this._stats.waveReached}`,
      `Zombies Killed: ${this._stats.totalZombiesKilled}`,
      `Time Survived: ${this.getFormattedPlayTime()}`,
    ]
    
    if (this.isNewHighScore()) {
      lines.unshift('🏆 NEW HIGH SCORE! 🏆')
    }
    
    return lines.join('\n')
  }

  /**
   * Request restart
   */
  requestRestart(): void {
    this.emit(GameOverEvent.RESTART, {})
  }

  /**
   * Reset the game over state
   */
  reset(): void {
    this._isGameOver = false
    this._stats = null
  }

  // ==================== Event System ====================

  on(event: string, callback: EventCallback): void {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, new Set())
    }
    this.eventListeners.get(event)!.add(callback)
  }

  off(event: string, callback: EventCallback): void {
    const listeners = this.eventListeners.get(event)
    if (listeners) {
      listeners.delete(callback)
    }
  }

  private emit(event: string, data?: unknown): void {
    const listeners = this.eventListeners.get(event)
    if (listeners) {
      listeners.forEach((callback) => callback(data))
    }
  }

  /**
   * Cleanup resources
   */
  dispose(): void {
    this.eventListeners.clear()
    this._stats = null
  }
}
