import * as THREE from 'three'
import type { GameState, EventCallback } from './types'
import { GameEvent } from './types'
import { InputManager, InputKey, InputEvent } from './InputManager'
import { SceneManager } from './SceneManager'

/**
 * GameEngine - Core game engine class
 * Manages the game loop, rendering, and coordinates all game systems
 * Requirements: 5.1, 5.2
 */
export class GameEngine {
  // Managers
  private sceneManager: SceneManager
  private inputManager: InputManager

  // Game loop state
  private isRunning: boolean = false
  private isPaused: boolean = false
  private lastTime: number = 0
  private animationFrameId: number | null = null

  // Frame timing
  private targetFPS: number = 60
  private frameTime: number = 1000 / 60
  private accumulator: number = 0

  // Event system
  private eventListeners: Map<string, Set<EventCallback>> = new Map()

  // Game state
  private gameState: GameState | null = null

  constructor(container: HTMLElement) {
    this.sceneManager = new SceneManager(container)
    this.inputManager = new InputManager()
  }

  /**
   * Initialize the game engine
   * Sets up Three.js renderer, scene, and initial game state
   */
  async init(): Promise<void> {
    // Initialize scene manager
    await this.sceneManager.init()

    // Initialize input manager
    this.inputManager.init(this.sceneManager.getRenderer().domElement)

    // Setup input event handlers
    this.setupInputHandlers()

    // Initialize game state
    this.initializeGameState()

    // Emit initialization complete event
    this.emit(GameEvent.GAME_START, { initialized: true })
  }

  /**
   * Setup input event handlers
   */
  private setupInputHandlers(): void {
    // Handle pause key
    this.inputManager.on(InputEvent.KEY_DOWN, (data: unknown) => {
      const keyData = data as { code: string }
      if (keyData.code === InputKey.PAUSE) {
        if (this.isPaused) {
          this.resume()
        } else {
          this.pause()
        }
      }
    })

    // Handle pointer lock change
    this.inputManager.on(InputEvent.POINTER_LOCK_CHANGE, (data: unknown) => {
      const lockData = data as { locked: boolean }
      if (!lockData.locked && this.isRunning && !this.isPaused) {
        // Pause game when pointer lock is lost
        this.pause()
      }
    })
  }

  /**
   * Initialize default game state
   */
  private initializeGameState(): void {
    this.gameState = {
      player: {
        position: { x: 0, y: 0, z: 0 },
        rotation: { x: 0, y: 0, z: 0 },
        health: 100,
        stamina: 100,
        weapons: [],
        currentWeaponIndex: 0,
      },
      wave: {
        currentWave: 1,
        zombiesKilled: 0,
        totalZombiesInWave: 0,
        isPreparationPhase: true,
      },
      zombies: [],
      score: 0,
      playTime: 0,
      timestamp: Date.now(),
    }
  }

  /**
   * Start the game loop
   */
  start(): void {
    if (this.isRunning) return

    this.isRunning = true
    this.isPaused = false
    this.lastTime = performance.now()
    this.emit(GameEvent.GAME_START)
    this.gameLoop()
  }

  /**
   * Pause the game
   */
  pause(): void {
    if (!this.isRunning || this.isPaused) return

    this.isPaused = true
    this.emit(GameEvent.GAME_PAUSE)
  }

  /**
   * Resume the game from pause
   */
  resume(): void {
    if (!this.isRunning || !this.isPaused) return

    this.isPaused = false
    this.lastTime = performance.now()
    this.emit(GameEvent.GAME_RESUME)
    this.gameLoop()
  }

  /**
   * Stop the game completely
   */
  stop(): void {
    this.isRunning = false
    this.isPaused = false

    if (this.animationFrameId !== null) {
      cancelAnimationFrame(this.animationFrameId)
      this.animationFrameId = null
    }

    this.emit(GameEvent.GAME_STOP)
    this.cleanup()
  }

  /**
   * Main game loop using requestAnimationFrame
   */
  private gameLoop(): void {
    if (!this.isRunning || this.isPaused) return

    const currentTime = performance.now()
    const frameTime = currentTime - this.lastTime
    this.lastTime = currentTime

    // Fixed timestep with accumulator for physics stability
    this.accumulator += frameTime

    // Prevent spiral of death - cap accumulator to prevent freeze
    if (this.accumulator > 200) {
      this.accumulator = 200
    }

    // Fixed update at target FPS with max iterations to prevent freeze
    let iterations = 0
    const maxIterations = 5
    while (this.accumulator >= this.frameTime && iterations < maxIterations) {
      this.fixedUpdate(this.frameTime / 1000)
      this.accumulator -= this.frameTime
      iterations++
    }
    
    // If we hit max iterations, discard remaining time
    if (iterations >= maxIterations) {
      this.accumulator = 0
    }

    // Variable update for rendering interpolation
    const alpha = this.accumulator / this.frameTime
    this.update(frameTime / 1000, alpha)

    // Render
    this.render()

    // Clear per-frame input state
    this.inputManager.update()

    this.animationFrameId = requestAnimationFrame(() => this.gameLoop())
  }

  /**
   * Fixed timestep update for physics and game logic
   * @param deltaTime Fixed time step in seconds
   */
  fixedUpdate(deltaTime: number): void {
    if (this.gameState) {
      this.gameState.playTime += deltaTime
    }

    // Process input
    this.processInput(deltaTime)

    // TODO: Update physics, AI, etc.
  }

  /**
   * Variable update for rendering and interpolation
   * @param _deltaTime Time elapsed since last frame in seconds (unused, reserved for future interpolation)
   * @param _alpha Interpolation factor (0-1) (unused, reserved for future interpolation)
   */
  update(_deltaTime: number, _alpha: number): void {
    // Update lighting based on player position
    if (this.gameState) {
      const playerPos = new THREE.Vector3(
        this.gameState.player.position.x,
        this.gameState.player.position.y,
        this.gameState.player.position.z
      )
      this.sceneManager.updateLighting(playerPos)
    }

    // TODO: Interpolate visual positions, update animations, etc.
  }

  /**
   * Process player input
   */
  private processInput(deltaTime: number): void {
    if (!this.gameState) return

    // Get movement input
    const movement = this.inputManager.getMovementInput()
    
    // Get mouse look
    const mouseMovement = this.inputManager.getMouseMovement()

    // Check for weapon switching via scroll wheel
    const wheelDirection = this.inputManager.getMouseWheelDirection()
    if (wheelDirection !== 0) {
      this.emit('weapon:cycle', { direction: wheelDirection })
    }

    // Check for weapon slot selection
    const weaponSlot = this.inputManager.getWeaponSlotPressed()
    if (weaponSlot >= 0) {
      this.emit('weapon:select', { slot: weaponSlot })
    }

    // Check for reload
    if (this.inputManager.wantsToReload()) {
      this.emit('weapon:reload', {})
    }

    // Check for fire
    if (this.inputManager.wantsToFire()) {
      this.emit('weapon:fire', {})
    }

    // Check for jump
    if (this.inputManager.wantsToJump()) {
      this.emit('player:jump', {})
    }

    // Emit movement update
    this.emit('player:move', {
      movement,
      mouseMovement,
      sprint: this.inputManager.wantsToSprint(),
      deltaTime,
    })
  }

  /**
   * Render the scene
   */
  render(): void {
    this.sceneManager.render()
  }

  /**
   * Get current game state
   */
  getState(): GameState | null {
    return this.gameState
  }

  /**
   * Set game state (for loading saves)
   */
  setState(state: GameState): void {
    this.gameState = state
  }

  /**
   * Subscribe to game events
   */
  on(event: string, callback: EventCallback): void {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, new Set())
    }
    this.eventListeners.get(event)!.add(callback)
  }

  /**
   * Unsubscribe from game events
   */
  off(event: string, callback: EventCallback): void {
    const listeners = this.eventListeners.get(event)
    if (listeners) {
      listeners.delete(callback)
    }
  }

  /**
   * Emit a game event
   */
  emit(event: string, data?: unknown): void {
    const listeners = this.eventListeners.get(event)
    if (listeners) {
      listeners.forEach((callback) => callback(data))
    }
  }

  /**
   * Cleanup resources
   */
  private cleanup(): void {
    // Dispose input manager
    this.inputManager.dispose()

    // Dispose scene manager
    this.sceneManager.dispose()

    // Clear event listeners
    this.eventListeners.clear()
  }

  // ==================== Getters ====================

  /**
   * Get the scene manager
   */
  getSceneManager(): SceneManager {
    return this.sceneManager
  }

  /**
   * Get the input manager
   */
  getInputManager(): InputManager {
    return this.inputManager
  }

  /**
   * Get Three.js scene (convenience method)
   */
  getScene(): THREE.Scene {
    return this.sceneManager.getScene()
  }

  /**
   * Get Three.js camera (convenience method)
   */
  getCamera(): THREE.PerspectiveCamera {
    return this.sceneManager.getCamera()
  }

  /**
   * Get Three.js renderer (convenience method)
   */
  getRenderer(): THREE.WebGLRenderer {
    return this.sceneManager.getRenderer()
  }

  /**
   * Check if game is running
   */
  isGameRunning(): boolean {
    return this.isRunning
  }

  /**
   * Check if game is paused
   */
  isGamePaused(): boolean {
    return this.isPaused
  }

  /**
   * Get target FPS
   */
  getTargetFPS(): number {
    return this.targetFPS
  }

  /**
   * Set target FPS
   */
  setTargetFPS(fps: number): void {
    this.targetFPS = Math.max(30, Math.min(144, fps))
    this.frameTime = 1000 / this.targetFPS
  }

  /**
   * Set mouse sensitivity
   */
  setMouseSensitivity(sensitivity: number): void {
    this.inputManager.setMouseSensitivity(sensitivity)
  }

  /**
   * Get mouse sensitivity
   */
  getMouseSensitivity(): number {
    return this.inputManager.getMouseSensitivity()
  }
}
