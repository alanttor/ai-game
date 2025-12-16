import * as THREE from 'three'
import type { Vector3, EventCallback } from '../types'
import { ZombieVariant, ZombieStateType } from '../types'

/**
 * Zombie configuration constants per variant
 * Requirements: 3.1, 3.6
 */
export const ZombieConfig = {
  // Detection and attack ranges
  DETECTION_RANGE: 30,      // Units - player detection range
  ATTACK_RANGE: 2,          // Units - melee attack range
  
  // Timing
  ATTACK_COOLDOWN: 1.5,     // Seconds between attacks
  DEATH_REMOVE_DELAY: 5,    // Seconds before removing dead zombie
  WANDER_CHANGE_INTERVAL: 3, // Seconds between wander direction changes
  
  // Variant-specific stats
  variants: {
    [ZombieVariant.WALKER]: {
      health: 100,
      damage: 10,
      speed: 2.0,
      name: 'Walker',
    },
    [ZombieVariant.RUNNER]: {
      health: 75,
      damage: 8,
      speed: 5.0,
      name: 'Runner',
    },
    [ZombieVariant.BRUTE]: {
      health: 250,
      damage: 25,
      speed: 1.5,
      name: 'Brute',
    },
    [ZombieVariant.CRAWLER]: {
      health: 50,
      damage: 15,
      speed: 3.0,
      name: 'Crawler',
    },
  },
}

/**
 * Zombie events
 */
export enum ZombieEvent {
  STATE_CHANGED = 'zombie:stateChanged',
  DAMAGE_TAKEN = 'zombie:damageTaken',
  ATTACK = 'zombie:attack',
  DEATH = 'zombie:death',
}


/**
 * Zombie class - AI-controlled enemy entity
 * Implements state machine for behavior (IDLE, WANDERING, CHASING, ATTACKING, DYING)
 * Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6
 */
export class Zombie {
  // Unique identifier
  private _id: string
  
  // Position and movement
  private _position: THREE.Vector3
  private _rotation: THREE.Euler
  
  // Stats based on variant
  private _health: number
  private _maxHealth: number
  private _damage: number
  private _speed: number
  private _variant: ZombieVariant
  
  // State machine
  private _state: ZombieStateType = ZombieStateType.IDLE
  private previousState: ZombieStateType = ZombieStateType.IDLE
  
  // Timers
  private attackCooldown: number = 0
  private deathTimer: number = 0
  private wanderTimer: number = 0
  private wanderDirection: THREE.Vector3 = new THREE.Vector3()
  
  // Spawn area for wandering
  private spawnPosition: THREE.Vector3
  private wanderRadius: number = 10
  
  // 3D model reference
  private mesh: THREE.Object3D | null = null
  
  // Event listeners
  private eventListeners: Map<string, Set<EventCallback>> = new Map()

  constructor(
    id: string,
    position: Vector3,
    variant: ZombieVariant = ZombieVariant.WALKER
  ) {
    this._id = id
    this._position = new THREE.Vector3(position.x, position.y, position.z)
    this._rotation = new THREE.Euler(0, 0, 0, 'YXZ')
    this.spawnPosition = this._position.clone()
    this._variant = variant
    
    // Initialize stats from variant config
    const variantConfig = ZombieConfig.variants[variant]
    this._health = variantConfig.health
    this._maxHealth = variantConfig.health
    this._damage = variantConfig.damage
    this._speed = variantConfig.speed
    
    // Start in idle state
    this._state = ZombieStateType.IDLE
  }

  // ==================== State Machine ====================

  /**
   * Transition to a new state
   */
  private setState(newState: ZombieStateType): void {
    if (this._state === newState) return
    if (this._state === ZombieStateType.DYING) return // Can't leave dying state
    
    this.previousState = this._state
    this._state = newState
    
    this.emit(ZombieEvent.STATE_CHANGED, {
      previous: this.previousState,
      current: this._state,
    })
    
    // State entry actions
    this.onStateEnter(newState)
  }

  /**
   * Handle state entry actions
   */
  private onStateEnter(state: ZombieStateType): void {
    switch (state) {
      case ZombieStateType.WANDERING:
        this.pickNewWanderDirection()
        this.wanderTimer = ZombieConfig.WANDER_CHANGE_INTERVAL
        break
      case ZombieStateType.DYING:
        this.deathTimer = ZombieConfig.DEATH_REMOVE_DELAY
        this.emit(ZombieEvent.DEATH, { id: this._id })
        break
      case ZombieStateType.ATTACKING:
        this.attackCooldown = 0 // Ready to attack immediately
        break
    }
  }

  /**
   * Pick a random direction for wandering
   */
  private pickNewWanderDirection(): void {
    const angle = Math.random() * Math.PI * 2
    this.wanderDirection.set(Math.cos(angle), 0, Math.sin(angle))
  }


  // ==================== Update Logic ====================

  /**
   * Main update method - call each frame
   * Requirements: 3.2, 3.3, 3.6
   * 
   * @param deltaTime - Time elapsed since last frame
   * @param playerPosition - Current player position for AI decisions
   */
  update(deltaTime: number, playerPosition: THREE.Vector3): void {
    // Update timers
    if (this.attackCooldown > 0) {
      this.attackCooldown -= deltaTime
    }
    
    // Handle dying state separately
    if (this._state === ZombieStateType.DYING) {
      this.updateDying(deltaTime)
      return
    }
    
    // Calculate distance to player
    const distanceToPlayer = this._position.distanceTo(playerPosition)
    
    // State transitions based on player distance
    this.updateStateTransitions(distanceToPlayer, playerPosition)
    
    // Execute current state behavior
    this.executeStateBehavior(deltaTime, playerPosition, distanceToPlayer)
    
    // Update mesh position if attached
    this.updateMeshPosition()
  }

  /**
   * Update state transitions based on player distance
   * Requirements: 3.2, 3.3, 3.6
   */
  private updateStateTransitions(distanceToPlayer: number, _playerPosition: THREE.Vector3): void {
    switch (this._state) {
      case ZombieStateType.IDLE:
      case ZombieStateType.WANDERING:
        // Transition to chasing if player is within detection range
        if (distanceToPlayer < ZombieConfig.DETECTION_RANGE) {
          this.setState(ZombieStateType.CHASING)
        } else if (this._state === ZombieStateType.IDLE) {
          // Start wandering after being idle
          this.setState(ZombieStateType.WANDERING)
        }
        break
        
      case ZombieStateType.CHASING:
        // Transition to attacking if within attack range
        if (distanceToPlayer < ZombieConfig.ATTACK_RANGE) {
          this.setState(ZombieStateType.ATTACKING)
        }
        // Return to wandering if player escapes detection range
        else if (distanceToPlayer > ZombieConfig.DETECTION_RANGE * 1.5) {
          this.setState(ZombieStateType.WANDERING)
        }
        break
        
      case ZombieStateType.ATTACKING:
        // Return to chasing if player moves out of attack range
        if (distanceToPlayer >= ZombieConfig.ATTACK_RANGE) {
          this.setState(ZombieStateType.CHASING)
        }
        break
    }
  }

  /**
   * Execute behavior for current state
   */
  private executeStateBehavior(
    deltaTime: number,
    playerPosition: THREE.Vector3,
    _distanceToPlayer: number
  ): void {
    switch (this._state) {
      case ZombieStateType.IDLE:
        // Do nothing, just wait
        break
        
      case ZombieStateType.WANDERING:
        this.updateWandering(deltaTime)
        break
        
      case ZombieStateType.CHASING:
        this.updateChasing(deltaTime, playerPosition)
        break
        
      case ZombieStateType.ATTACKING:
        this.updateAttacking(deltaTime, playerPosition)
        break
    }
  }

  /**
   * Update wandering behavior
   * Requirements: 3.6
   */
  private updateWandering(deltaTime: number): void {
    // Update wander timer
    this.wanderTimer -= deltaTime
    if (this.wanderTimer <= 0) {
      this.pickNewWanderDirection()
      this.wanderTimer = ZombieConfig.WANDER_CHANGE_INTERVAL
    }
    
    // Move in wander direction
    const movement = this.wanderDirection.clone().multiplyScalar(this._speed * 0.5 * deltaTime)
    const newPosition = this._position.clone().add(movement)
    
    // Keep within spawn area
    const distanceFromSpawn = newPosition.distanceTo(this.spawnPosition)
    if (distanceFromSpawn <= this.wanderRadius) {
      this._position.copy(newPosition)
    } else {
      // Turn back towards spawn
      this.wanderDirection.copy(this.spawnPosition).sub(this._position).normalize()
    }
    
    // Face movement direction
    this.faceDirection(this.wanderDirection)
  }

  /**
   * Update chasing behavior
   * Requirements: 3.2
   */
  private updateChasing(deltaTime: number, playerPosition: THREE.Vector3): void {
    // Calculate direction to player
    const direction = new THREE.Vector3()
      .subVectors(playerPosition, this._position)
      .setY(0) // Keep on ground plane
      .normalize()
    
    // Move towards player
    const movement = direction.multiplyScalar(this._speed * deltaTime)
    this._position.add(movement)
    
    // Face player
    this.faceDirection(direction)
  }

  /**
   * Update attacking behavior
   * Requirements: 3.3
   */
  private updateAttacking(_deltaTime: number, playerPosition: THREE.Vector3): void {
    // Face player
    const direction = new THREE.Vector3()
      .subVectors(playerPosition, this._position)
      .setY(0)
      .normalize()
    this.faceDirection(direction)
    
    // Attack if cooldown is ready
    if (this.attackCooldown <= 0) {
      this.performAttack()
      this.attackCooldown = ZombieConfig.ATTACK_COOLDOWN
    }
  }

  /**
   * Update dying state
   * Requirements: 3.5
   */
  private updateDying(deltaTime: number): void {
    this.deathTimer -= deltaTime
  }

  /**
   * Face a direction
   */
  private faceDirection(direction: THREE.Vector3): void {
    if (direction.lengthSq() > 0) {
      this._rotation.y = Math.atan2(direction.x, direction.z)
    }
  }

  /**
   * Update mesh position to match zombie position
   */
  private updateMeshPosition(): void {
    if (this.mesh) {
      this.mesh.position.copy(this._position)
      this.mesh.rotation.copy(this._rotation)
    }
  }


  // ==================== Combat ====================

  /**
   * Perform an attack
   * Requirements: 3.3
   */
  private performAttack(): void {
    this.emit(ZombieEvent.ATTACK, {
      id: this._id,
      damage: this._damage,
      position: this.position,
    })
  }

  /**
   * Apply damage to the zombie
   * Requirements: 3.4, 3.5
   * 
   * @param amount - Damage amount
   * @param hitPoint - Optional hit location for effects
   */
  takeDamage(amount: number, hitPoint?: Vector3): void {
    if (this._state === ZombieStateType.DYING) return
    if (amount <= 0) return
    
    const previousHealth = this._health
    this._health = Math.max(0, this._health - amount)
    
    this.emit(ZombieEvent.DAMAGE_TAKEN, {
      id: this._id,
      damage: amount,
      previousHealth,
      currentHealth: this._health,
      hitPoint,
    })
    
    // Check for death
    if (this._health <= 0) {
      this.die()
    }
  }

  /**
   * Trigger death state
   * Requirements: 3.5
   */
  die(): void {
    this.setState(ZombieStateType.DYING)
  }

  // ==================== State Queries ====================

  /**
   * Check if zombie should be removed (death animation complete)
   */
  shouldRemove(): boolean {
    return this._state === ZombieStateType.DYING && this.deathTimer <= 0
  }

  /**
   * Check if zombie is dead
   */
  isDead(): boolean {
    return this._state === ZombieStateType.DYING || this._health <= 0
  }

  /**
   * Check if zombie is aware of player (chasing or attacking)
   */
  isAwareOfPlayer(): boolean {
    return this._state === ZombieStateType.CHASING || this._state === ZombieStateType.ATTACKING
  }

  /**
   * Check if zombie can attack (cooldown ready and in attacking state)
   */
  canAttack(): boolean {
    return this._state === ZombieStateType.ATTACKING && this.attackCooldown <= 0
  }

  /**
   * Get the damage this zombie deals
   */
  getDamage(): number {
    return this._damage
  }

  /**
   * Get distance to a position
   */
  distanceTo(position: Vector3): number {
    return this._position.distanceTo(new THREE.Vector3(position.x, position.y, position.z))
  }

  // ==================== Getters & Setters ====================

  get id(): string {
    return this._id
  }

  get position(): Vector3 {
    return { x: this._position.x, y: this._position.y, z: this._position.z }
  }

  set position(pos: Vector3) {
    this._position.set(pos.x, pos.y, pos.z)
    this.updateMeshPosition()
  }

  get rotation(): { x: number; y: number; z: number } {
    return { x: this._rotation.x, y: this._rotation.y, z: this._rotation.z }
  }

  get health(): number {
    return this._health
  }

  get maxHealth(): number {
    return this._maxHealth
  }

  get damage(): number {
    return this._damage
  }

  get speed(): number {
    return this._speed
  }

  get variant(): ZombieVariant {
    return this._variant
  }

  get state(): ZombieStateType {
    return this._state
  }

  /**
   * Get position as THREE.Vector3
   */
  getPosition3(): THREE.Vector3 {
    return this._position.clone()
  }

  /**
   * Set the 3D mesh for this zombie
   */
  setMesh(mesh: THREE.Object3D): void {
    this.mesh = mesh
    this.updateMeshPosition()
  }

  /**
   * Get the 3D mesh
   */
  getMesh(): THREE.Object3D | null {
    return this.mesh
  }

  // ==================== Serialization ====================

  /**
   * Export zombie state for saving
   */
  toState(): { id: string; position: Vector3; health: number; variant: ZombieVariant; state: ZombieStateType } {
    return {
      id: this._id,
      position: this.position,
      health: this._health,
      variant: this._variant,
      state: this._state,
    }
  }

  /**
   * Create zombie from saved state
   */
  static fromState(state: { id: string; position: Vector3; health: number; variant: ZombieVariant; state: ZombieStateType }): Zombie {
    const zombie = new Zombie(state.id, state.position, state.variant)
    zombie._health = state.health
    zombie._state = state.state
    return zombie
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
    if (this.mesh) {
      // Remove from parent if attached
      if (this.mesh.parent) {
        this.mesh.parent.remove(this.mesh)
      }
      this.mesh = null
    }
  }
}
