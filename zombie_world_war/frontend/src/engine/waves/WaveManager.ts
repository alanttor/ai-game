import type { Vector3, EventCallback, WaveState } from '../types'
import { GameEvent, ZombieVariant } from '../types'
import type { ZombieManager } from '../zombies/ZombieManager'
import type { Player } from '../Player'
import { GameOverManager, GameOverReason } from './GameOverManager'

/**
 * Wave configuration constants
 */
export const WaveConfig = {
  // Spawn formula: wave * 5 + 10
  BASE_ZOMBIES: 10,
  ZOMBIES_PER_WAVE: 5,
  
  // Preparation phase duration in seconds
  PREPARATION_TIME: 30,
  
  // Score formula: zombies * 100 * wave
  SCORE_PER_KILL: 100,
  
  // Wave completion bonus multiplier
  WAVE_COMPLETION_BONUS: 500,
  
  // Spawn settings
  SPAWN_INTERVAL: 0.5,  // Seconds between spawns
  MIN_SPAWN_DISTANCE: 20,  // Minimum distance from player
  MAX_SPAWN_DISTANCE: 40,  // Maximum distance from player
}

/**
 * Wave events
 */
export enum WaveEvent {
  WAVE_START = 'wave:start',
  WAVE_END = 'wave:end',
  PREPARATION_START = 'wave:preparationStart',
  PREPARATION_END = 'wave:preparationEnd',
  ZOMBIE_KILLED = 'wave:zombieKilled',
  SCORE_CHANGED = 'wave:scoreChanged',
  GAME_OVER = 'wave:gameOver',
}

/**
 * WaveManager - Manages wave-based survival gameplay
 * Handles zombie spawning, wave progression, scoring, and game over logic
 * Requirements: 4.1, 4.2, 4.3, 4.4, 4.5
 */
export class WaveManager {
  // Wave state
  private _currentWave: number = 0
  private _zombiesKilled: number = 0
  private _totalZombiesInWave: number = 0
  private _zombiesSpawned: number = 0
  private _isPreparationPhase: boolean = true
  private _preparationTimeLeft: number = WaveConfig.PREPARATION_TIME
  
  // Score
  private _score: number = 0
  private _waveScore: number = 0
  
  // Game state
  private _isGameOver: boolean = false
  private _gameOverReason: GameOverReason | null = null
  private _finalScore: number = 0
  
  // Spawning
  private spawnTimer: number = 0
  private spawnPoints: Vector3[] = []
  
  // References
  private zombieManager: ZombieManager | null = null
  private player: Player | null = null
  private gameOverManager: GameOverManager
  
  // Play time tracking
  private _playTime: number = 0
  
  // Event listeners
  private eventListeners: Map<string, Set<EventCallback>> = new Map()

  constructor() {
    // Initialize with default spawn points (can be overridden)
    this.spawnPoints = this.generateDefaultSpawnPoints()
    // Initialize game over manager
    this.gameOverManager = new GameOverManager()
  }

  /**
   * Initialize the wave manager with required references
   */
  init(zombieManager: ZombieManager, player: Player): void {
    this.zombieManager = zombieManager
    this.player = player
    
    // Listen for zombie deaths
    this.zombieManager.on(GameEvent.ZOMBIE_DEATH, () => {
      this.onZombieKilled()
    })
  }

  /**
   * Get the game over manager instance
   */
  getGameOverManager(): GameOverManager {
    return this.gameOverManager
  }


  /**
   * Generate default spawn points around the origin
   */
  private generateDefaultSpawnPoints(): Vector3[] {
    const points: Vector3[] = []
    const numPoints = 8
    const radius = 30
    
    for (let i = 0; i < numPoints; i++) {
      const angle = (i / numPoints) * Math.PI * 2
      points.push({
        x: Math.cos(angle) * radius,
        y: 0,
        z: Math.sin(angle) * radius,
      })
    }
    
    return points
  }

  /**
   * Set custom spawn points
   */
  setSpawnPoints(points: Vector3[]): void {
    this.spawnPoints = points
  }

  // ==================== Wave Control ====================

  /**
   * Start the game (begins with preparation phase for wave 1)
   */
  startGame(): void {
    this._currentWave = 0
    this._score = 0
    this._isGameOver = false
    this._gameOverReason = null
    this._playTime = 0
    
    // Reset game over manager
    this.gameOverManager.reset()
    
    // Start preparation for wave 1
    this.startPreparationPhase()
  }

  /**
   * Start preparation phase before a wave
   * Requirements: 4.2, 4.3
   */
  startPreparationPhase(): void {
    this._currentWave++
    this._isPreparationPhase = true
    this._preparationTimeLeft = WaveConfig.PREPARATION_TIME
    this._zombiesKilled = 0
    this._zombiesSpawned = 0
    this._waveScore = 0
    this._totalZombiesInWave = this.calculateZombieCount(this._currentWave)
    
    this.emit(WaveEvent.PREPARATION_START, {
      wave: this._currentWave,
      preparationTime: WaveConfig.PREPARATION_TIME,
      totalZombies: this._totalZombiesInWave,
    })
  }

  /**
   * Start the current wave (spawn zombies)
   * Requirements: 4.1
   */
  startWave(): void {
    this._isPreparationPhase = false
    this.spawnTimer = 0
    
    this.emit(WaveEvent.WAVE_START, {
      wave: this._currentWave,
      totalZombies: this._totalZombiesInWave,
    })
    this.emit(GameEvent.WAVE_START, {
      wave: this._currentWave,
      totalZombies: this._totalZombiesInWave,
    })
  }

  /**
   * End the current wave
   * Requirements: 4.2
   */
  endWave(): void {
    // Calculate wave completion bonus
    const waveBonus = this._currentWave * WaveConfig.WAVE_COMPLETION_BONUS
    this._score += waveBonus
    
    this.emit(WaveEvent.WAVE_END, {
      wave: this._currentWave,
      zombiesKilled: this._zombiesKilled,
      waveScore: this._waveScore,
      bonus: waveBonus,
      totalScore: this._score,
    })
    this.emit(GameEvent.WAVE_END, {
      wave: this._currentWave,
      score: this._score,
    })
    
    // Start preparation for next wave
    this.startPreparationPhase()
  }

  /**
   * Calculate number of zombies for a wave
   * Formula: wave * 5 + 10
   * Requirements: 4.1
   */
  calculateZombieCount(waveNumber: number): number {
    return waveNumber * WaveConfig.ZOMBIES_PER_WAVE + WaveConfig.BASE_ZOMBIES
  }

  /**
   * Calculate score for killing zombies
   * Formula: zombies * 100 * wave
   * Requirements: 4.4
   */
  calculateScore(zombiesKilled: number, waveNumber: number): number {
    return zombiesKilled * WaveConfig.SCORE_PER_KILL * waveNumber
  }

  // ==================== Update ====================

  /**
   * Update wave manager each frame
   * 
   * @param deltaTime - Time elapsed since last frame in seconds
   */
  update(deltaTime: number): void {
    if (this._isGameOver) return
    
    // Track play time
    this._playTime += deltaTime
    
    // Check for player death
    this.checkPlayerDeath()
    if (this._isGameOver) return
    
    if (this._isPreparationPhase) {
      this.updatePreparationPhase(deltaTime)
    } else {
      this.updateWavePhase(deltaTime)
    }
  }

  /**
   * Update during preparation phase
   */
  private updatePreparationPhase(deltaTime: number): void {
    this._preparationTimeLeft -= deltaTime
    
    if (this._preparationTimeLeft <= 0) {
      this._preparationTimeLeft = 0
      this.emit(WaveEvent.PREPARATION_END, { wave: this._currentWave })
      this.startWave()
    }
  }

  /**
   * Update during active wave
   */
  private updateWavePhase(deltaTime: number): void {
    // Spawn zombies gradually
    if (this._zombiesSpawned < this._totalZombiesInWave) {
      this.spawnTimer += deltaTime
      
      if (this.spawnTimer >= WaveConfig.SPAWN_INTERVAL) {
        this.spawnTimer = 0
        this.spawnZombie()
      }
    }
    
    // Check if wave is complete
    if (this._zombiesKilled >= this._totalZombiesInWave) {
      this.endWave()
    }
  }

  /**
   * Spawn a single zombie
   */
  private spawnZombie(): void {
    if (!this.zombieManager || this._zombiesSpawned >= this._totalZombiesInWave) return
    
    const spawnPoint = this.getSpawnPoint()
    const variant = this.getZombieVariantForWave()
    
    this.zombieManager.spawnZombie(spawnPoint, variant)
    this._zombiesSpawned++
  }

  /**
   * Get a spawn point (preferably away from player)
   */
  private getSpawnPoint(): Vector3 {
    if (this.spawnPoints.length === 0) {
      return { x: 0, y: 0, z: 30 }
    }
    
    // If we have player position, try to spawn away from them
    if (this.player) {
      const playerPos = this.player.position
      
      // Filter spawn points that are far enough from player
      const validPoints = this.spawnPoints.filter(point => {
        const dx = point.x - playerPos.x
        const dz = point.z - playerPos.z
        const distance = Math.sqrt(dx * dx + dz * dz)
        return distance >= WaveConfig.MIN_SPAWN_DISTANCE
      })
      
      if (validPoints.length > 0) {
        return validPoints[Math.floor(Math.random() * validPoints.length)]
      }
    }
    
    // Fallback to random spawn point
    return this.spawnPoints[Math.floor(Math.random() * this.spawnPoints.length)]
  }

  /**
   * Get zombie variant based on wave difficulty
   */
  private getZombieVariantForWave(): ZombieVariant {
    const wave = this._currentWave
    const roll = Math.random()
    
    // Higher waves have more dangerous variants
    if (wave >= 10) {
      // Wave 10+: 30% Walker, 30% Runner, 20% Crawler, 20% Brute
      if (roll < 0.3) return ZombieVariant.WALKER
      if (roll < 0.6) return ZombieVariant.RUNNER
      if (roll < 0.8) return ZombieVariant.CRAWLER
      return ZombieVariant.BRUTE
    } else if (wave >= 5) {
      // Wave 5-9: 40% Walker, 30% Runner, 20% Crawler, 10% Brute
      if (roll < 0.4) return ZombieVariant.WALKER
      if (roll < 0.7) return ZombieVariant.RUNNER
      if (roll < 0.9) return ZombieVariant.CRAWLER
      return ZombieVariant.BRUTE
    } else {
      // Wave 1-4: 60% Walker, 25% Runner, 10% Crawler, 5% Brute
      if (roll < 0.6) return ZombieVariant.WALKER
      if (roll < 0.85) return ZombieVariant.RUNNER
      if (roll < 0.95) return ZombieVariant.CRAWLER
      return ZombieVariant.BRUTE
    }
  }


  // ==================== Zombie Kill Handling ====================

  /**
   * Handle zombie death event
   * Requirements: 4.4
   */
  onZombieKilled(): void {
    if (this._isGameOver || this._isPreparationPhase) return
    
    this._zombiesKilled++
    
    // Calculate score for this kill
    const killScore = this.calculateScore(1, this._currentWave)
    this._waveScore += killScore
    this._score += killScore
    
    this.emit(WaveEvent.ZOMBIE_KILLED, {
      zombiesKilled: this._zombiesKilled,
      totalZombies: this._totalZombiesInWave,
      killScore,
      totalScore: this._score,
    })
    
    this.emit(WaveEvent.SCORE_CHANGED, {
      score: this._score,
      waveScore: this._waveScore,
    })
  }

  // ==================== Game Over ====================

  /**
   * Check if player has died
   * Requirements: 4.5
   */
  private checkPlayerDeath(): void {
    if (!this.player || this._isGameOver) return
    
    if (this.player.isDead()) {
      this.triggerGameOver(GameOverReason.PLAYER_DEATH)
    }
  }

  /**
   * Trigger game over
   * Requirements: 4.5
   */
  triggerGameOver(reason: GameOverReason): void {
    if (this._isGameOver) return
    
    this._isGameOver = true
    this._gameOverReason = reason
    this._finalScore = this._score
    
    const totalZombiesKilled = this.getTotalZombiesKilled()
    
    // Trigger game over in the GameOverManager for final score display
    this.gameOverManager.triggerGameOver(
      reason,
      this._finalScore,
      this._currentWave,
      totalZombiesKilled,
      this._playTime
    )
    
    this.emit(WaveEvent.GAME_OVER, {
      reason,
      finalScore: this._finalScore,
      waveReached: this._currentWave,
      totalZombiesKilled,
      playTime: this._playTime,
    })
    
    this.emit(GameEvent.GAME_OVER, {
      reason,
      score: this._finalScore,
      wave: this._currentWave,
    })
  }

  /**
   * Get total zombies killed across all waves
   */
  private getTotalZombiesKilled(): number {
    return this.zombieManager?.getTotalKilled() ?? 0
  }

  // ==================== State Queries ====================

  get currentWave(): number {
    return this._currentWave
  }

  get zombiesKilled(): number {
    return this._zombiesKilled
  }

  get totalZombiesInWave(): number {
    return this._totalZombiesInWave
  }

  get zombiesRemaining(): number {
    return this._totalZombiesInWave - this._zombiesKilled
  }

  get isPreparationPhase(): boolean {
    return this._isPreparationPhase
  }

  get preparationTimeLeft(): number {
    return this._preparationTimeLeft
  }

  get score(): number {
    return this._score
  }

  get waveScore(): number {
    return this._waveScore
  }

  get isGameOver(): boolean {
    return this._isGameOver
  }

  get gameOverReason(): GameOverReason | null {
    return this._gameOverReason
  }

  get finalScore(): number {
    return this._finalScore
  }

  get playTime(): number {
    return this._playTime
  }

  /**
   * Get final score display data from GameOverManager
   * Requirements: 4.5
   */
  getFinalScoreDisplay() {
    return this.gameOverManager.getFinalScoreDisplay()
  }

  /**
   * Get game over summary text
   * Requirements: 4.5
   */
  getGameOverSummary(): string {
    return this.gameOverManager.getSummaryText()
  }

  // ==================== Serialization ====================

  /**
   * Export wave state for saving
   */
  toState(): WaveState {
    return {
      currentWave: this._currentWave,
      zombiesKilled: this._zombiesKilled,
      totalZombiesInWave: this._totalZombiesInWave,
      isPreparationPhase: this._isPreparationPhase,
    }
  }

  /**
   * Get full game state for saving
   */
  getGameState(): {
    wave: WaveState
    score: number
    isGameOver: boolean
  } {
    return {
      wave: this.toState(),
      score: this._score,
      isGameOver: this._isGameOver,
    }
  }

  /**
   * Restore wave state from save
   */
  fromState(state: WaveState, score: number = 0): void {
    this._currentWave = state.currentWave
    this._zombiesKilled = state.zombiesKilled
    this._totalZombiesInWave = state.totalZombiesInWave
    this._isPreparationPhase = state.isPreparationPhase
    this._score = score
    this._zombiesSpawned = state.zombiesKilled // Assume killed zombies were spawned
    this._isGameOver = false
    this._gameOverReason = null
    
    if (this._isPreparationPhase) {
      this._preparationTimeLeft = WaveConfig.PREPARATION_TIME
    }
  }

  /**
   * Reset the wave manager
   */
  reset(): void {
    this._currentWave = 0
    this._zombiesKilled = 0
    this._totalZombiesInWave = 0
    this._zombiesSpawned = 0
    this._isPreparationPhase = true
    this._preparationTimeLeft = WaveConfig.PREPARATION_TIME
    this._score = 0
    this._waveScore = 0
    this._isGameOver = false
    this._gameOverReason = null
    this._finalScore = 0
    this._playTime = 0
    this.spawnTimer = 0
    
    // Reset game over manager
    this.gameOverManager.reset()
    
    // Reset zombie manager kill count
    this.zombieManager?.resetKillCount()
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
    this.gameOverManager.dispose()
    this.zombieManager = null
    this.player = null
  }
}
