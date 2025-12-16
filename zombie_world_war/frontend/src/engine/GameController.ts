import * as THREE from 'three'
import type { GameState, EventCallback, Vector3 } from './types'
import { GameEvent, ZombieStateType } from './types'
import { Player, PlayerEvent } from './Player'
import { WeaponManager, WeaponManagerEvent } from './weapons/WeaponManager'
import { ZombieManager } from './zombies/ZombieManager'
import { WaveManager, WaveEvent } from './waves/WaveManager'
import { GameOverReason } from './waves/GameOverManager'
import { AudioManager } from './audio/AudioManager'
import { GameAudioController } from './audio/GameAudioController'
import { FirstPersonCamera } from './FirstPersonCamera'
import { SceneManager } from './SceneManager'
import { InputManager } from './InputManager'
import { LODManager } from './scene/LODManager'
import { PerformanceMonitor, PerformanceEvent } from './performance/PerformanceMonitor'
import type { PerformanceMetrics } from './performance/PerformanceMonitor'

/**
 * GameController events
 */
export enum GameControllerEvent {
  STATE_CHANGED = 'gameController:stateChanged',
  SCORE_UPDATED = 'gameController:scoreUpdated',
  WAVE_STARTED = 'gameController:waveStarted',
  WAVE_ENDED = 'gameController:waveEnded',
  GAME_OVER = 'gameController:gameOver',
  PLAYER_DAMAGED = 'gameController:playerDamaged',
}

/**
 * Game configuration interface
 */
export interface GameConfig {
  mouseSensitivity: number
  masterVolume: number
  musicVolume: number
  sfxVolume: number
}

/**
 * Default game configuration
 */
export const DEFAULT_GAME_CONFIG: GameConfig = {
  mouseSensitivity: 50,
  masterVolume: 80,
  musicVolume: 70,
  sfxVolume: 90,
}


/**
 * GameController - Orchestrates all game systems
 * Integrates Player, Weapons, Zombies, Waves, and Audio
 * Requirements: All - System Integration
 */
export class GameController {
  // Core managers
  private sceneManager: SceneManager
  private inputManager: InputManager
  private player: Player
  private weaponManager: WeaponManager
  private zombieManager: ZombieManager
  private waveManager: WaveManager
  private audioManager: AudioManager
  private audioController: GameAudioController
  private firstPersonCamera: FirstPersonCamera

  // Performance managers
  private lodManager: LODManager
  private performanceMonitor: PerformanceMonitor

  // Game state
  private _isInitialized: boolean = false
  private _isRunning: boolean = false
  private _isPaused: boolean = false
  private _score: number = 0
  private _playTime: number = 0

  // Configuration
  private config: GameConfig = { ...DEFAULT_GAME_CONFIG }

  // Event listeners
  private eventListeners: Map<string, Set<EventCallback>> = new Map()

  // Cached objects for performance (avoid allocations in update loop)
  private _cachedPlayerPos: THREE.Vector3 = new THREE.Vector3()
  private _cachedDirection: THREE.Vector3 = new THREE.Vector3()

  constructor(sceneManager: SceneManager, inputManager: InputManager) {
    this.sceneManager = sceneManager
    this.inputManager = inputManager

    // Initialize player at spawn position
    this.player = new Player({ x: 0, y: 0, z: 0 })

    // Initialize weapon manager
    this.weaponManager = new WeaponManager()

    // Initialize zombie manager with scene
    this.zombieManager = new ZombieManager(this.sceneManager.getScene())

    // Initialize wave manager
    this.waveManager = new WaveManager()

    // Initialize audio system
    this.audioManager = new AudioManager()
    this.audioController = new GameAudioController(this.audioManager)

    // Initialize first person camera
    const camera = this.sceneManager.getCamera()
    this.firstPersonCamera = new FirstPersonCamera(camera.aspect)
    this.firstPersonCamera.setSensitivity(this.config.mouseSensitivity / 50 * 0.002)

    // Initialize performance systems
    this.lodManager = new LODManager(
      this.sceneManager.getScene(),
      this.sceneManager.getCamera(),
      this.sceneManager.getRenderer()
    )
    this.performanceMonitor = new PerformanceMonitor()
    this.performanceMonitor.setRenderer(this.sceneManager.getRenderer())
  }


  /**
   * Initialize all game systems
   */
  async init(): Promise<void> {
    if (this._isInitialized) return

    // Attach camera to player
    this.player.attachCamera(this.sceneManager.getCamera())

    // Initialize wave manager with dependencies
    this.waveManager.init(this.zombieManager, this.player)

    // Initialize audio
    await this.audioController.init()

    // Setup event listeners between systems
    this.setupEventListeners()

    // Setup performance event listeners
    this.setupPerformanceListeners()

    // Load configuration from localStorage
    this.loadConfig()

    this._isInitialized = true
  }

  /**
   * Setup performance monitoring event listeners
   */
  private setupPerformanceListeners(): void {
    this.performanceMonitor.on(PerformanceEvent.FPS_DROP, (data) => {
      const fpsData = data as { fps: number; isCritical: boolean }
      console.warn(`Performance warning: FPS dropped to ${fpsData.fps}`)
      
      // Auto-reduce quality if critical
      if (fpsData.isCritical) {
        const currentQuality = this.lodManager.getQualityLevel()
        if (currentQuality > 0) {
          this.lodManager.setQualityLevel(currentQuality - 1)
        }
      }
    })

    this.performanceMonitor.on(PerformanceEvent.FPS_RECOVER, () => {
      // Performance recovered, could increase quality
    })
  }

  /**
   * Setup event listeners between game systems
   */
  private setupEventListeners(): void {
    // Player events
    this.player.on(PlayerEvent.HEALTH_CHANGED, (data) => {
      const healthData = data as { current: number; damage?: number }
      if (healthData.damage && healthData.damage > 0) {
        this.audioController.playPlayerHurt()
        this.emit(GameControllerEvent.PLAYER_DAMAGED, healthData)
      }
      this.emitStateChanged()
    })

    this.player.on(PlayerEvent.DEATH, () => {
      this.audioController.playPlayerDeath()
      this.waveManager.triggerGameOver(GameOverReason.PLAYER_DEATH)
    })

    this.player.on(PlayerEvent.JUMP, () => {
      this.audioController.playJump()
    })

    this.player.on(PlayerEvent.LAND, () => {
      this.audioController.playLand()
    })


    // Weapon events
    this.weaponManager.on(WeaponManagerEvent.WEAPON_FIRED, (data) => {
      const weaponData = data as { weapon: { type: string } }
      this.audioController.playWeaponFire(
        weaponData.weapon.type,
        this.player.position
      )
    })

    this.weaponManager.on(WeaponManagerEvent.WEAPON_RELOAD_START, () => {
      this.audioController.playReload(this.player.position)
    })

    this.weaponManager.on(WeaponManagerEvent.WEAPON_EMPTY, () => {
      this.audioController.playEmptyClick(this.player.position)
    })

    this.weaponManager.on(WeaponManagerEvent.WEAPON_SWITCHED, () => {
      this.emitStateChanged()
    })

    this.weaponManager.on(WeaponManagerEvent.AMMO_CHANGED, () => {
      this.emitStateChanged()
    })

    // Wave events
    this.waveManager.on(WaveEvent.WAVE_START, () => {
      this.audioController.playWaveStart()
      this.audioController.playCombatMusic()
      this.emit(GameControllerEvent.WAVE_STARTED, {
        wave: this.waveManager.currentWave,
        totalZombies: this.waveManager.totalZombiesInWave,
      })
    })

    this.waveManager.on(WaveEvent.WAVE_END, () => {
      this.audioController.playWaveComplete()
      this.audioController.playAmbientMusic()
      this.emit(GameControllerEvent.WAVE_ENDED, {
        wave: this.waveManager.currentWave,
        score: this.waveManager.score,
      })
    })


    this.waveManager.on(WaveEvent.PREPARATION_START, () => {
      this.audioController.playAmbientMusic()
    })

    this.waveManager.on(WaveEvent.SCORE_CHANGED, (data) => {
      const scoreData = data as { score: number }
      this._score = scoreData.score
      this.emit(GameControllerEvent.SCORE_UPDATED, { score: this._score })
    })

    this.waveManager.on(WaveEvent.GAME_OVER, (data) => {
      this.audioController.playGameOverMusic()
      this.emit(GameControllerEvent.GAME_OVER, data)
    })

    // Zombie events
    this.zombieManager.on(GameEvent.ZOMBIE_DEATH, (data) => {
      const zombieData = data as { position?: Vector3 }
      if (zombieData.position) {
        this.audioController.playZombieDeath(zombieData.position)
      }
    })
  }

  /**
   * Start a new game
   */
  startNewGame(): void {
    // Reset all systems
    this.player = new Player({ x: 0, y: 0, z: 0 })
    this.player.attachCamera(this.sceneManager.getCamera())
    this.setupEventListeners()

    this.zombieManager.clear()
    this.waveManager.reset()
    this.waveManager.init(this.zombieManager, this.player)

    this._score = 0
    this._playTime = 0
    this._isRunning = true
    this._isPaused = false

    // Start the game
    this.waveManager.startGame()
    this.audioController.playAmbientMusic()

    this.emit(GameEvent.GAME_START)
  }


  /**
   * Load game from saved state
   */
  loadGame(state: GameState): void {
    // Restore player state
    this.player.fromState({
      position: state.player.position,
      rotation: state.player.rotation,
      health: state.player.health,
      stamina: state.player.stamina,
    })

    // Restore weapon state
    this.weaponManager.fromState({
      weapons: state.player.weapons,
      currentWeaponIndex: state.player.currentWeaponIndex,
    })

    // Restore wave state
    this.waveManager.fromState(state.wave, state.score)

    // Restore zombies
    this.zombieManager.fromState(state.zombies)

    this._score = state.score
    this._playTime = state.playTime
    this._isRunning = true
    this._isPaused = false

    this.emit(GameEvent.GAME_START)
  }

  /**
   * Get current game state for saving
   */
  getGameState(): GameState {
    const weaponState = this.weaponManager.toState()

    return {
      player: {
        position: this.player.position,
        rotation: this.player.rotation,
        health: this.player.health,
        stamina: this.player.stamina,
        weapons: weaponState.weapons,
        currentWeaponIndex: weaponState.currentWeaponIndex,
      },
      wave: this.waveManager.toState(),
      zombies: this.zombieManager.toState(),
      score: this._score,
      playTime: this._playTime,
      timestamp: Date.now(),
    }
  }


  /**
   * Update game logic each frame
   */
  update(deltaTime: number): void {
    if (!this._isRunning || this._isPaused) return

    this._playTime += deltaTime

    // Update performance monitoring
    this.performanceMonitor.update(deltaTime)
    this.performanceMonitor.setZombieCount(this.zombieManager.getActiveCount())

    // Update player
    this.player.update(deltaTime)

    // Update zombies with player position
    this.zombieManager.update(deltaTime, this.player.position)

    // Update wave manager
    this.waveManager.update(deltaTime)

    // Update audio
    this.audioController.setPlayerPosition(this.player.position)
    this.audioController.update(deltaTime)

    // Update zombie ambient sounds (throttled for performance)
    this.updateZombieAmbientSoundsThrottled(deltaTime)

    // Check for zombie attacks on player
    this.checkZombieAttacks()

    // Update lighting based on player position (use cached vector)
    this._cachedPlayerPos.set(
      this.player.position.x,
      this.player.position.y,
      this.player.position.z
    )
    this.sceneManager.updateLighting(this._cachedPlayerPos)

    // Update LOD system
    this.lodManager.update(deltaTime)
  }

  // Throttle zombie ambient sound updates
  private _lastZombieAudioUpdate: number = 0
  private _zombieAudioUpdateInterval: number = 0.1 // 100ms

  /**
   * Update zombie ambient sounds with throttling for performance
   */
  private updateZombieAmbientSoundsThrottled(deltaTime: number): void {
    this._lastZombieAudioUpdate += deltaTime
    if (this._lastZombieAudioUpdate >= this._zombieAudioUpdateInterval) {
      this._lastZombieAudioUpdate = 0
      
      const zombies = this.zombieManager.getAllZombies().map((z) => ({
        id: z.id,
        position: z.position,
        state: z.state as ZombieStateType,
      }))
      this.audioController.updateZombieAmbientSounds(deltaTime, zombies)
    }
  }

  /**
   * Check for zombie attacks on player
   */
  private checkZombieAttacks(): void {
    const zombiesInRange = this.zombieManager.getZombiesInRange(
      this.player.position,
      2.0 // Attack range
    )

    for (const zombie of zombiesInRange) {
      if (zombie.canAttack()) {
        const damage = zombie.getDamage()
        this.player.takeDamage(damage)
        this.audioController.playZombieAttack(zombie.position)
      }
    }
  }


  /**
   * Process player input
   */
  processInput(deltaTime: number): void {
    if (!this._isRunning || this._isPaused) return

    // Get movement input
    const movement = this.inputManager.getMovementInput()
    const mouseMovement = this.inputManager.getMouseMovement()

    // Apply movement
    this.player.move(movement.x, movement.z, deltaTime)

    // Apply camera rotation
    const sensitivity = this.config.mouseSensitivity / 50
    this.player.rotate(
      mouseMovement.x * sensitivity * 0.002,
      mouseMovement.y * sensitivity * 0.002
    )

    // Handle sprint
    this.player.sprint(this.inputManager.wantsToSprint())

    // Handle jump
    if (this.inputManager.wantsToJump()) {
      this.player.jump()
    }

    // Handle weapon actions
    if (this.inputManager.wantsToFire()) {
      this.fireWeapon()
    }

    if (this.inputManager.wantsToReload()) {
      this.weaponManager.reload()
    }

    // Handle weapon switching
    const wheelDirection = this.inputManager.getMouseWheelDirection()
    if (wheelDirection > 0) {
      this.weaponManager.cycleNext()
    } else if (wheelDirection < 0) {
      this.weaponManager.cyclePrevious()
    }

    const weaponSlot = this.inputManager.getWeaponSlotPressed()
    if (weaponSlot >= 0) {
      this.weaponManager.switchToSlot(weaponSlot)
    }
  }


  /**
   * Fire the current weapon
   */
  private fireWeapon(): void {
    const camera = this.sceneManager.getCamera()
    const origin = camera.position.clone()
    const direction = new THREE.Vector3()
    camera.getWorldDirection(direction)

    const result = this.weaponManager.fire(
      origin,
      direction,
      this.sceneManager.getScene()
    )

    if (result.success && result.hits) {
      // Process hits on zombies
      for (const hit of result.hits) {
        if (hit.zombieId) {
          this.zombieManager.damageZombie(
            hit.zombieId,
            result.damage,
            hit.point
          )
          this.audioController.playZombieHit(hit.point)
        }
      }
    }
  }

  /**
   * Pause the game
   */
  pause(): void {
    if (!this._isRunning || this._isPaused) return
    this._isPaused = true
    this.audioController.onGamePause()
    this.emit(GameEvent.GAME_PAUSE)
  }

  /**
   * Resume the game
   */
  resume(): void {
    if (!this._isRunning || !this._isPaused) return
    this._isPaused = false
    this.audioController.onGameResume()
    this.emit(GameEvent.GAME_RESUME)
  }

  /**
   * Stop the game
   */
  stop(): void {
    this._isRunning = false
    this._isPaused = false
    this.audioController.stopMusic()
    this.emit(GameEvent.GAME_STOP)
  }


  // ==================== Configuration ====================

  /**
   * Apply game configuration
   */
  applyConfig(config: Partial<GameConfig>): void {
    this.config = { ...this.config, ...config }

    // Apply mouse sensitivity
    if (config.mouseSensitivity !== undefined) {
      this.firstPersonCamera.setSensitivity(config.mouseSensitivity / 50)
    }

    // Apply audio settings
    if (config.masterVolume !== undefined) {
      this.audioManager.setMasterVolume(config.masterVolume / 100)
    }
    if (config.musicVolume !== undefined) {
      this.audioManager.setMusicVolume(config.musicVolume / 100)
    }
    if (config.sfxVolume !== undefined) {
      this.audioManager.setSfxVolume(config.sfxVolume / 100)
    }

    // Save to localStorage
    this.saveConfig()
  }

  /**
   * Save configuration to localStorage
   */
  private saveConfig(): void {
    localStorage.setItem('gameSettings', JSON.stringify(this.config))
  }

  /**
   * Load configuration from localStorage
   */
  private loadConfig(): void {
    const stored = localStorage.getItem('zww_settings')
    if (stored) {
      try {
        const parsed = JSON.parse(stored)
        this.config = { 
          ...DEFAULT_GAME_CONFIG, 
          mouseSensitivity: parsed.mouseSensitivity ?? DEFAULT_GAME_CONFIG.mouseSensitivity,
          masterVolume: parsed.masterVolume ?? DEFAULT_GAME_CONFIG.masterVolume,
          musicVolume: parsed.musicVolume ?? DEFAULT_GAME_CONFIG.musicVolume,
          sfxVolume: parsed.sfxVolume ?? DEFAULT_GAME_CONFIG.sfxVolume,
        }
        this.applyConfig(this.config)
      } catch {
        // Use defaults
      }
    }
  }

  /**
   * Get current configuration
   */
  getConfig(): GameConfig {
    return { ...this.config }
  }


  // ==================== Getters ====================

  get isInitialized(): boolean {
    return this._isInitialized
  }

  get isRunning(): boolean {
    return this._isRunning
  }

  get isPaused(): boolean {
    return this._isPaused
  }

  get score(): number {
    return this._score
  }

  get playTime(): number {
    return this._playTime
  }

  getPlayer(): Player {
    return this.player
  }

  getWeaponManager(): WeaponManager {
    return this.weaponManager
  }

  getZombieManager(): ZombieManager {
    return this.zombieManager
  }

  getWaveManager(): WaveManager {
    return this.waveManager
  }

  getAudioController(): GameAudioController {
    return this.audioController
  }

  getLODManager(): LODManager {
    return this.lodManager
  }

  getPerformanceMonitor(): PerformanceMonitor {
    return this.performanceMonitor
  }

  /**
   * Get current performance metrics
   */
  getPerformanceMetrics(): PerformanceMetrics {
    return this.performanceMonitor.getMetrics()
  }

  /**
   * Get HUD state for UI display
   */
  getHUDState() {
    const weapon = this.weaponManager.getCurrentWeapon()
    return {
      health: this.player.health,
      maxHealth: this.player.maxHealth,
      stamina: this.player.stamina,
      maxStamina: this.player.maxStamina,
      currentWeaponName: weapon?.name ?? 'None',
      currentWeaponSlot: this.weaponManager.getCurrentWeaponIndex(),
      currentAmmo: weapon?.currentAmmo ?? 0,
      reserveAmmo: weapon?.reserveAmmo ?? 0,
      magazineSize: weapon?.magazineSize ?? 0,
      isReloading: this.weaponManager.isReloading(),
      currentWave: this.waveManager.currentWave,
      zombiesKilled: this.waveManager.zombiesKilled,
      totalZombiesInWave: this.waveManager.totalZombiesInWave,
      isPreparationPhase: this.waveManager.isPreparationPhase,
      preparationTimeLeft: this.waveManager.preparationTimeLeft,
      score: this._score,
    }
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

  private emitStateChanged(): void {
    this.emit(GameControllerEvent.STATE_CHANGED, this.getHUDState())
  }

  // ==================== Cleanup ====================

  /**
   * Dispose all resources
   */
  dispose(): void {
    this.stop()
    this.zombieManager.dispose()
    this.waveManager.dispose()
    this.audioController.dispose()
    this.audioManager.dispose()
    this.lodManager.dispose()
    this.performanceMonitor.dispose()
    this.eventListeners.clear()
  }
}
