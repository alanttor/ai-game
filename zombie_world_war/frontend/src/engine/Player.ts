import * as THREE from 'three'
import type { Vector3, Euler, EventCallback } from './types'

/**
 * Player configuration constants
 */
export const PlayerConfig = {
  // Movement
  WALK_SPEED: 5.0,           // Units per second
  SPRINT_MULTIPLIER: 1.5,    // Sprint speed = walk speed * 1.5
  
  // Jump
  JUMP_HEIGHT: 2.0,          // Fixed jump height in units
  GRAVITY: 20.0,             // Gravity acceleration
  
  // Stamina
  MAX_STAMINA: 100,
  STAMINA_DRAIN_RATE: 20,    // Per second while sprinting
  STAMINA_REGEN_RATE: 15,    // Per second while not sprinting
  STAMINA_THRESHOLD: 20,     // Minimum stamina to start sprinting (20%)
  
  // Health
  MAX_HEALTH: 100,
  
  // Camera
  EYE_HEIGHT: 1.7,           // Camera height from ground
  MIN_PITCH: -Math.PI / 2 + 0.1,  // Look down limit
  MAX_PITCH: Math.PI / 2 - 0.1,   // Look up limit
}

/**
 * Player events
 */
export enum PlayerEvent {
  HEALTH_CHANGED = 'player:healthChanged',
  STAMINA_CHANGED = 'player:staminaChanged',
  DEATH = 'player:death',
  JUMP = 'player:jumped',
  LAND = 'player:landed',
}

/**
 * Player class - Handles player movement, health, stamina, and camera control
 * Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
 */
export class Player {
  // Position and rotation
  private _position: THREE.Vector3
  private _rotation: THREE.Euler
  
  // Velocity for physics
  private velocity: THREE.Vector3
  
  // Health and stamina
  private _health: number
  private _maxHealth: number
  private _stamina: number
  private _maxStamina: number

  
  // Sprint state
  private _isSprinting: boolean = false
  private _canSprint: boolean = true  // Blocked when stamina < threshold
  
  // Jump/ground state
  private _isOnGround: boolean = true
  private _isJumping: boolean = false
  
  // Camera reference (for first-person view)
  private camera: THREE.PerspectiveCamera | null = null
  
  // Event listeners
  private eventListeners: Map<string, Set<EventCallback>> = new Map()

  constructor(
    position: Vector3 = { x: 0, y: 0, z: 0 },
    rotation: Euler = { x: 0, y: 0, z: 0 }
  ) {
    this._position = new THREE.Vector3(position.x, position.y, position.z)
    this._rotation = new THREE.Euler(rotation.x, rotation.y, rotation.z, 'YXZ')
    this.velocity = new THREE.Vector3(0, 0, 0)
    
    this._health = PlayerConfig.MAX_HEALTH
    this._maxHealth = PlayerConfig.MAX_HEALTH
    this._stamina = PlayerConfig.MAX_STAMINA
    this._maxStamina = PlayerConfig.MAX_STAMINA
  }

  /**
   * Attach camera for first-person view
   */
  attachCamera(camera: THREE.PerspectiveCamera): void {
    this.camera = camera
    this.updateCameraPosition()
  }

  /**
   * Update camera position to follow player
   */
  private updateCameraPosition(): void {
    if (this.camera) {
      this.camera.position.set(
        this._position.x,
        this._position.y + PlayerConfig.EYE_HEIGHT,
        this._position.z
      )
      this.camera.rotation.copy(this._rotation)
    }
  }

  // ==================== Movement ====================

  /**
   * Move the player based on input direction
   * Direction is relative to camera facing (WASD movement)
   * Requirements: 1.1
   * 
   * @param inputX - Left/right input (-1 to 1)
   * @param inputZ - Forward/backward input (-1 to 1)
   * @param deltaTime - Time elapsed since last frame
   */
  move(inputX: number, inputZ: number, deltaTime: number): void {
    if (inputX === 0 && inputZ === 0) return
    
    // Calculate movement speed
    let speed = PlayerConfig.WALK_SPEED
    if (this._isSprinting && this._canSprint) {
      speed *= PlayerConfig.SPRINT_MULTIPLIER
    }
    
    // Get forward and right vectors from camera rotation (Y-axis only)
    const forward = new THREE.Vector3(0, 0, -1)
    const right = new THREE.Vector3(1, 0, 0)
    
    // Apply Y rotation only (horizontal movement)
    const yRotation = new THREE.Euler(0, this._rotation.y, 0)
    forward.applyEuler(yRotation)
    right.applyEuler(yRotation)
    
    // Calculate movement direction
    const moveDirection = new THREE.Vector3()
    moveDirection.addScaledVector(forward, -inputZ)  // Forward is -Z
    moveDirection.addScaledVector(right, inputX)
    
    // Normalize to prevent faster diagonal movement
    if (moveDirection.length() > 0) {
      moveDirection.normalize()
    }
    
    // Apply movement
    this._position.addScaledVector(moveDirection, speed * deltaTime)
    
    this.updateCameraPosition()
  }

  /**
   * Rotate camera based on mouse movement
   * Requirements: 1.2
   * 
   * @param deltaX - Mouse X movement (already scaled by sensitivity)
   * @param deltaY - Mouse Y movement (already scaled by sensitivity)
   */
  rotate(deltaX: number, deltaY: number): void {
    // Yaw (horizontal rotation)
    this._rotation.y -= deltaX
    
    // Pitch (vertical rotation) with clamping
    this._rotation.x -= deltaY
    this._rotation.x = Math.max(
      PlayerConfig.MIN_PITCH,
      Math.min(PlayerConfig.MAX_PITCH, this._rotation.x)
    )
    
    this.updateCameraPosition()
  }

  /**
   * Attempt to jump
   * Requirements: 1.3 - Jump only when on ground, fixed height of 2 units
   * 
   * @returns true if jump was initiated
   */
  jump(): boolean {
    if (!this._isOnGround) return false
    
    // Calculate initial velocity needed for fixed jump height
    // Using v² = 2gh, so v = sqrt(2 * g * h)
    const jumpVelocity = Math.sqrt(2 * PlayerConfig.GRAVITY * PlayerConfig.JUMP_HEIGHT)
    
    this.velocity.y = jumpVelocity
    this._isOnGround = false
    this._isJumping = true
    
    this.emit(PlayerEvent.JUMP)
    return true
  }

  /**
   * Set sprint state
   * Requirements: 1.4, 1.5
   * 
   * @param active - Whether sprint key is held
   */
  sprint(active: boolean): void {
    // Can only start sprinting if stamina is above threshold
    if (active && !this._isSprinting) {
      if (this._stamina >= PlayerConfig.STAMINA_THRESHOLD) {
        this._isSprinting = true
        this._canSprint = true
      }
    } else if (!active) {
      this._isSprinting = false
    }
  }

  // ==================== Health & Stamina ====================

  /**
   * Apply damage to player
   * 
   * @param amount - Damage amount
   */
  takeDamage(amount: number): void {
    if (amount <= 0) return
    
    const previousHealth = this._health
    this._health = Math.max(0, this._health - amount)
    
    this.emit(PlayerEvent.HEALTH_CHANGED, {
      previous: previousHealth,
      current: this._health,
      damage: amount,
    })
    
    if (this._health <= 0) {
      this.emit(PlayerEvent.DEATH)
    }
  }

  /**
   * Heal the player
   * 
   * @param amount - Heal amount
   */
  heal(amount: number): void {
    if (amount <= 0) return
    
    const previousHealth = this._health
    this._health = Math.min(this._maxHealth, this._health + amount)
    
    this.emit(PlayerEvent.HEALTH_CHANGED, {
      previous: previousHealth,
      current: this._health,
      healed: amount,
    })
  }

  /**
   * Update stamina based on sprint state
   * Requirements: 1.4, 1.5
   * 
   * @param deltaTime - Time elapsed since last frame
   */
  updateStamina(deltaTime: number): void {
    const previousStamina = this._stamina
    
    if (this._isSprinting && this._canSprint) {
      // Drain stamina while sprinting
      this._stamina = Math.max(0, this._stamina - PlayerConfig.STAMINA_DRAIN_RATE * deltaTime)
      
      // Check if stamina depleted
      if (this._stamina <= 0) {
        this._canSprint = false
        this._isSprinting = false
      }
    } else {
      // Regenerate stamina when not sprinting
      this._stamina = Math.min(this._maxStamina, this._stamina + PlayerConfig.STAMINA_REGEN_RATE * deltaTime)
      
      // Re-enable sprinting when stamina reaches threshold (20%)
      if (!this._canSprint && this._stamina >= PlayerConfig.STAMINA_THRESHOLD) {
        this._canSprint = true
      }
    }
    
    if (previousStamina !== this._stamina) {
      this.emit(PlayerEvent.STAMINA_CHANGED, {
        previous: previousStamina,
        current: this._stamina,
      })
    }
  }


  // ==================== Physics Update ====================

  /**
   * Update physics (gravity, ground detection)
   * Requirements: 1.3
   * 
   * @param deltaTime - Time elapsed since last frame
   * @param groundY - Y position of ground at player's location
   */
  updatePhysics(deltaTime: number, groundY: number = 0): void {
    if (!this._isOnGround) {
      // Apply gravity
      this.velocity.y -= PlayerConfig.GRAVITY * deltaTime
      
      // Update position
      this._position.y += this.velocity.y * deltaTime
      
      // Ground collision
      if (this._position.y <= groundY) {
        this._position.y = groundY
        this.velocity.y = 0
        this._isOnGround = true
        
        if (this._isJumping) {
          this._isJumping = false
          this.emit(PlayerEvent.LAND)
        }
      }
    }
    
    this.updateCameraPosition()
  }

  /**
   * Full update method - call each frame
   * 
   * @param deltaTime - Time elapsed since last frame
   * @param groundY - Y position of ground at player's location
   */
  update(deltaTime: number, groundY: number = 0): void {
    this.updateStamina(deltaTime)
    this.updatePhysics(deltaTime, groundY)
  }

  // ==================== State Queries ====================

  /**
   * Check if player is dead
   */
  isDead(): boolean {
    return this._health <= 0
  }

  /**
   * Check if player is currently sprinting
   */
  isSprinting(): boolean {
    return this._isSprinting && this._canSprint
  }

  /**
   * Check if player can start sprinting
   */
  canSprint(): boolean {
    return this._canSprint
  }

  /**
   * Check if player is on ground
   */
  isOnGround(): boolean {
    return this._isOnGround
  }

  /**
   * Check if player is jumping
   */
  isJumping(): boolean {
    return this._isJumping
  }

  /**
   * Get current movement speed
   */
  getCurrentSpeed(): number {
    if (this._isSprinting && this._canSprint) {
      return PlayerConfig.WALK_SPEED * PlayerConfig.SPRINT_MULTIPLIER
    }
    return PlayerConfig.WALK_SPEED
  }

  // ==================== Getters & Setters ====================

  get position(): Vector3 {
    return { x: this._position.x, y: this._position.y, z: this._position.z }
  }

  set position(pos: Vector3) {
    this._position.set(pos.x, pos.y, pos.z)
    this.updateCameraPosition()
  }

  get rotation(): Euler {
    return { x: this._rotation.x, y: this._rotation.y, z: this._rotation.z }
  }

  set rotation(rot: Euler) {
    this._rotation.set(rot.x, rot.y, rot.z, 'YXZ')
    this.updateCameraPosition()
  }

  get health(): number {
    return this._health
  }

  get maxHealth(): number {
    return this._maxHealth
  }

  get stamina(): number {
    return this._stamina
  }

  get maxStamina(): number {
    return this._maxStamina
  }

  /**
   * Get position as THREE.Vector3
   */
  getPosition3(): THREE.Vector3 {
    return this._position.clone()
  }

  /**
   * Get rotation as THREE.Euler
   */
  getRotation3(): THREE.Euler {
    return this._rotation.clone()
  }

  /**
   * Set ground state (for external collision detection)
   */
  setOnGround(onGround: boolean): void {
    const wasOnGround = this._isOnGround
    this._isOnGround = onGround
    
    if (!wasOnGround && onGround && this._isJumping) {
      this._isJumping = false
      this.velocity.y = 0
      this.emit(PlayerEvent.LAND)
    }
  }

  // ==================== Serialization ====================

  /**
   * Export player state for saving
   */
  toState(): { position: Vector3; rotation: Euler; health: number; stamina: number } {
    return {
      position: this.position,
      rotation: this.rotation,
      health: this._health,
      stamina: this._stamina,
    }
  }

  /**
   * Restore player state from save
   */
  fromState(state: { position: Vector3; rotation: Euler; health: number; stamina: number }): void {
    this.position = state.position
    this.rotation = state.rotation
    this._health = state.health
    this._stamina = state.stamina
    this._isOnGround = true
    this._isJumping = false
    this.velocity.set(0, 0, 0)
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
