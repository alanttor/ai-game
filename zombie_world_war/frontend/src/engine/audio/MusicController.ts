import type { EventCallback } from '../types'
import { AudioManager, MusicTrack, SoundEffect } from './AudioManager'

/**
 * Music state for dynamic music system
 */
export enum MusicState {
  MENU = 'menu',
  PREPARATION = 'preparation',
  COMBAT = 'combat',
  TENSE = 'tense',
  GAME_OVER = 'gameOver',
}

/**
 * Music controller events
 */
export enum MusicControllerEvent {
  STATE_CHANGED = 'music:stateChanged',
  ALERT_PLAYED = 'music:alertPlayed',
}

/**
 * Configuration for music transitions
 */
export const MusicControllerConfig = {
  // Health threshold for tense music (25% as per Requirements 9.5)
  TENSE_HEALTH_THRESHOLD: 0.25,
  
  // Minimum time between state changes to prevent rapid switching
  MIN_STATE_CHANGE_INTERVAL: 2.0, // seconds
  
  // Preparation countdown alert thresholds (seconds remaining)
  COUNTDOWN_ALERT_TIMES: [10, 5, 4, 3, 2, 1],
}

/**
 * MusicController - Handles dynamic music transitions based on game state
 * Implements music intensity changes based on combat, danger, and wave events
 * Requirements: 10.3, 10.4, 10.5
 */
export class MusicController {
  private audioManager: AudioManager
  
  // Current music state
  private _currentState: MusicState = MusicState.MENU
  private lastStateChangeTime: number = 0
  
  // Game state tracking
  private playerHealthPercent: number = 1.0
  private isInCombat: boolean = false
  private isPreparationPhase: boolean = false
  private preparationTimeLeft: number = 0
  private lastAlertTime: number = -1
  
  // Pause state
  private _isPaused: boolean = false
  
  // Event listeners
  private eventListeners: Map<string, Set<EventCallback>> = new Map()

  constructor(audioManager: AudioManager) {
    this.audioManager = audioManager
  }

  /**
   * Initialize the music controller
   */
  init(): void {
    this._currentState = MusicState.MENU
    this.lastStateChangeTime = performance.now() / 1000
  }

  // ==================== State Management ====================

  /**
   * Set the music state directly
   * @param state - Target music state
   * @param force - Force state change even if within minimum interval
   */
  setState(state: MusicState, force: boolean = false): void {
    const currentTime = performance.now() / 1000
    const timeSinceLastChange = currentTime - this.lastStateChangeTime
    
    // Prevent rapid state changes unless forced
    if (!force && timeSinceLastChange < MusicControllerConfig.MIN_STATE_CHANGE_INTERVAL) {
      return
    }
    
    if (this._currentState === state) return
    
    const previousState = this._currentState
    this._currentState = state
    this.lastStateChangeTime = currentTime
    
    // Play appropriate music track
    this.playMusicForState(state)
    
    this.emit(MusicControllerEvent.STATE_CHANGED, {
      previous: previousState,
      current: state,
    })
  }

  /**
   * Play the appropriate music track for a state
   */
  private playMusicForState(state: MusicState): void {
    switch (state) {
      case MusicState.MENU:
        this.audioManager.playMusic(MusicTrack.MENU, true)
        break
      case MusicState.PREPARATION:
        this.audioManager.playMusic(MusicTrack.AMBIENT, true)
        break
      case MusicState.COMBAT:
        this.audioManager.playMusic(MusicTrack.COMBAT, true)
        break
      case MusicState.TENSE:
        this.audioManager.playMusic(MusicTrack.TENSE, true)
        break
      case MusicState.GAME_OVER:
        this.audioManager.playMusic(MusicTrack.GAME_OVER, true)
        break
    }
  }

  /**
   * Get current music state
   */
  get currentState(): MusicState {
    return this._currentState
  }

  /**
   * Get preparation time remaining
   */
  get prepTimeLeft(): number {
    return this.preparationTimeLeft
  }

  // ==================== Game State Updates ====================

  /**
   * Update player health for tense music triggering
   * Requirements: 10.4
   * @param healthPercent - Player health as percentage (0-1)
   */
  updatePlayerHealth(healthPercent: number): void {
    this.playerHealthPercent = Math.max(0, Math.min(1, healthPercent))
    this.evaluateMusicState()
  }

  /**
   * Set combat state
   * @param inCombat - Whether player is in active combat
   */
  setInCombat(inCombat: boolean): void {
    this.isInCombat = inCombat
    this.evaluateMusicState()
  }

  /**
   * Update preparation phase state
   * @param isPreparation - Whether in preparation phase
   * @param timeLeft - Time remaining in preparation (seconds)
   */
  updatePreparationPhase(isPreparation: boolean, timeLeft: number = 0): void {
    const wasPreparation = this.isPreparationPhase
    this.isPreparationPhase = isPreparation
    this.preparationTimeLeft = timeLeft
    
    // If entering preparation phase, switch to ambient music
    if (isPreparation && !wasPreparation) {
      this.setState(MusicState.PREPARATION, true)
      this.lastAlertTime = -1 // Reset alert tracking
    }
    
    // Check for countdown alerts
    if (isPreparation) {
      this.checkCountdownAlerts(timeLeft)
    }
    
    this.evaluateMusicState()
  }

  /**
   * Handle wave start
   * Requirements: 10.3
   */
  onWaveStart(): void {
    this.isPreparationPhase = false
    this.isInCombat = true
    
    // Play wave start alert
    this.playWaveAlert()
    
    // Switch to combat music
    this.setState(MusicState.COMBAT, true)
  }

  /**
   * Handle wave end
   */
  onWaveEnd(): void {
    this.isInCombat = false
    this.evaluateMusicState()
  }

  /**
   * Handle game over
   */
  onGameOver(): void {
    this.setState(MusicState.GAME_OVER, true)
  }

  /**
   * Handle return to menu
   */
  onReturnToMenu(): void {
    this.setState(MusicState.MENU, true)
    this.resetState()
  }

  /**
   * Reset internal state
   */
  private resetState(): void {
    this.playerHealthPercent = 1.0
    this.isInCombat = false
    this.isPreparationPhase = false
    this.preparationTimeLeft = 0
    this.lastAlertTime = -1
  }

  // ==================== Music State Evaluation ====================

  /**
   * Evaluate and update music state based on current game conditions
   * Requirements: 10.3, 10.4
   */
  private evaluateMusicState(): void {
    // Don't change music during menu or game over
    if (this._currentState === MusicState.MENU || 
        this._currentState === MusicState.GAME_OVER) {
      return
    }
    
    // Check for tense music (low health)
    if (this.playerHealthPercent <= MusicControllerConfig.TENSE_HEALTH_THRESHOLD) {
      this.setState(MusicState.TENSE)
      return
    }
    
    // Check for combat music
    if (this.isInCombat && !this.isPreparationPhase) {
      this.setState(MusicState.COMBAT)
      return
    }
    
    // Default to preparation/ambient music
    if (this.isPreparationPhase) {
      this.setState(MusicState.PREPARATION)
    }
  }

  // ==================== Wave Alerts ====================

  /**
   * Play wave start alert sound
   * Requirements: 10.3
   */
  private playWaveAlert(): void {
    // Play the wave start sound effect
    this.audioManager.play(SoundEffect.WAVE_START, { volume: 1.0 })
    this.emit(MusicControllerEvent.ALERT_PLAYED, { type: 'waveStart' })
  }

  /**
   * Check and play countdown alerts during preparation phase
   * @param timeLeft - Time remaining in seconds
   */
  private checkCountdownAlerts(timeLeft: number): void {
    const roundedTime = Math.ceil(timeLeft)
    
    // Check if we should play an alert for this time
    if (MusicControllerConfig.COUNTDOWN_ALERT_TIMES.includes(roundedTime)) {
      // Only play if we haven't already played for this second
      if (this.lastAlertTime !== roundedTime) {
        this.lastAlertTime = roundedTime
        this.playCountdownAlert(roundedTime)
      }
    }
  }

  /**
   * Play countdown alert sound
   * @param secondsRemaining - Seconds remaining in countdown
   */
  private playCountdownAlert(secondsRemaining: number): void {
    // Increase urgency as time decreases
    const volume = secondsRemaining <= 3 ? 0.8 : 0.5
    const playbackRate = secondsRemaining <= 3 ? 1.2 : 1.0
    
    this.audioManager.play(SoundEffect.PREPARATION_TICK, {
      volume,
      playbackRate,
    })
    
    this.emit(MusicControllerEvent.ALERT_PLAYED, {
      type: 'countdown',
      secondsRemaining,
    })
  }


  // ==================== Pause Handling ====================

  /**
   * Handle game pause - reduces audio volume
   * Requirements: 10.5
   */
  onPause(): void {
    if (this._isPaused) return
    this._isPaused = true
    this.audioManager.pause()
  }

  /**
   * Handle game resume - restores audio volume
   * Requirements: 10.5
   */
  onResume(): void {
    if (!this._isPaused) return
    this._isPaused = false
    this.audioManager.resume()
  }

  /**
   * Check if music is paused
   */
  get isPaused(): boolean {
    return this._isPaused
  }

  // ==================== Update ====================

  /**
   * Update music controller each frame
   * @param _deltaTime - Time since last frame (unused, reserved for future use)
   */
  update(_deltaTime: number): void {
    // Currently no per-frame updates needed
    // Reserved for future features like beat-synced effects
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

  // ==================== Cleanup ====================

  /**
   * Stop all music
   */
  stopMusic(): void {
    this.audioManager.stopMusic()
  }

  /**
   * Dispose of resources
   */
  dispose(): void {
    this.stopMusic()
    this.eventListeners.clear()
    this.resetState()
  }
}
