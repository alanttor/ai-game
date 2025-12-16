import * as THREE from 'three'
import { Player, PlayerEvent } from './Player'
import { FirstPersonCamera } from './FirstPersonCamera'
import { PlayerPhysics } from './PlayerPhysics'
import type { Vector3, Euler, EventCallback } from './types'

/**
 * PlayerController - Integrates Player, Camera, and Physics systems
 * Provides a unified interface for player control
 * Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
 */
export class PlayerController {
  private player: Player
  private camera: FirstPersonCamera
  private physics: PlayerPhysics
  
  // Event listeners
  private eventListeners: Map<string, Set<EventCallback>> = new Map()

  constructor(scene: THREE.Scene, aspect: number = 16 / 9) {
    // Create player
    this.player = new Player()
    
    // Create camera and attach to player
    this.camera = new FirstPersonCamera(aspect)
    this.camera.attachToPlayer(this.player)
    
    // Create physics system
    this.physics = new PlayerPhysics(this.player, scene)
    
    // Forward player events
    this.setupEventForwarding()
  }

  /**
   * Setup event forwarding from player to controller
   */
  private setupEventForwarding(): void {
    const events = [
      PlayerEvent.HEALTH_CHANGED,
      PlayerEvent.STAMINA_CHANGED,
      PlayerEvent.DEATH,
      PlayerEvent.JUMP,
      PlayerEvent.LAND,
    ]
    
    events.forEach((event) => {
      this.player.on(event, (data) => this.emit(event, data))
    })
  }

  /**
   * Process input and update player state
   * Call this each frame with input data
   * 
   * @param input - Input state for this frame
   * @param deltaTime - Time elapsed since last frame
   */
  processInput(input: PlayerInput, deltaTime: number): void {
    // Handle mouse look
    if (input.mouseMovement) {
      this.camera.handleMouseMove(
        input.mouseMovement.x,
        input.mouseMovement.y
      )
    }
    
    // Handle sprint
    this.player.sprint(input.sprint)
    
    // Handle jump
    if (input.jump) {
      this.player.jump()
    }
    
    // Handle movement
    if (input.movement.x !== 0 || input.movement.z !== 0) {
      this.player.move(input.movement.x, input.movement.z, deltaTime)
    }
  }

  /**
   * Update physics and player state
   * Call this each frame after processing input
   * 
   * @param deltaTime - Time elapsed since last frame
   */
  update(deltaTime: number): void {
    // Update physics (ground detection, gravity)
    this.physics.update(deltaTime)
    
    // Update stamina
    this.player.updateStamina(deltaTime)
  }

  /**
   * Apply damage to player
   */
  takeDamage(amount: number): void {
    this.player.takeDamage(amount)
  }

  /**
   * Heal the player
   */
  heal(amount: number): void {
    this.player.heal(amount)
  }

  /**
   * Set player position
   */
  setPosition(position: Vector3): void {
    this.player.position = position
  }

  /**
   * Set player rotation
   */
  setRotation(rotation: Euler): void {
    this.player.rotation = rotation
  }

  /**
   * Set camera sensitivity
   */
  setSensitivity(sensitivity: number): void {
    this.camera.setSensitivity(sensitivity)
  }

  /**
   * Get camera sensitivity
   */
  getSensitivity(): number {
    return this.camera.getSensitivity()
  }

  // ==================== Getters ====================

  getPlayer(): Player {
    return this.player
  }

  getCamera(): FirstPersonCamera {
    return this.camera
  }

  getThreeCamera(): THREE.PerspectiveCamera {
    return this.camera.getCamera()
  }

  getPhysics(): PlayerPhysics {
    return this.physics
  }

  getPosition(): Vector3 {
    return this.player.position
  }

  getRotation(): Euler {
    return this.player.rotation
  }

  getHealth(): number {
    return this.player.health
  }

  getMaxHealth(): number {
    return this.player.maxHealth
  }

  getStamina(): number {
    return this.player.stamina
  }

  getMaxStamina(): number {
    return this.player.maxStamina
  }

  isDead(): boolean {
    return this.player.isDead()
  }

  isSprinting(): boolean {
    return this.player.isSprinting()
  }

  isOnGround(): boolean {
    return this.player.isOnGround()
  }

  // ==================== Serialization ====================

  /**
   * Export player state for saving
   */
  toState(): { position: Vector3; rotation: Euler; health: number; stamina: number } {
    return this.player.toState()
  }

  /**
   * Restore player state from save
   */
  fromState(state: { position: Vector3; rotation: Euler; health: number; stamina: number }): void {
    this.player.fromState(state)
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
}

/**
 * Input state for player controller
 */
export interface PlayerInput {
  movement: { x: number; z: number }
  mouseMovement?: { x: number; y: number }
  jump: boolean
  sprint: boolean
}
