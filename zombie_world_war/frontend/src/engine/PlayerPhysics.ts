import * as THREE from 'three'
import { Player } from './Player'
import type { EventCallback } from './types'

/**
 * Physics configuration
 */
export const PhysicsConfig = {
  // Collision
  PLAYER_RADIUS: 0.4,        // Player collision radius
  PLAYER_HEIGHT: 1.8,        // Player collision height
  
  // Ground detection
  GROUND_CHECK_DISTANCE: 0.1, // Distance to check below player for ground
  STEP_HEIGHT: 0.3,          // Maximum step height player can climb
  
  // Wall collision
  WALL_SLIDE_FACTOR: 0.8,    // How much velocity is preserved when sliding along walls
  COLLISION_ITERATIONS: 3,   // Number of collision resolution iterations
}

/**
 * Physics events
 */
export enum PhysicsEvent {
  COLLISION = 'physics:collision',
  GROUND_STATE_CHANGED = 'physics:groundStateChanged',
}

/**
 * Collision result
 */
export interface CollisionResult {
  collided: boolean
  normal: THREE.Vector3
  penetration: number
  object?: THREE.Object3D
}

/**
 * PlayerPhysics - Handles player physics and collision detection
 * Requirements: 1.3 - Ground detection, jump physics (fixed height 2 units), wall collision
 */
export class PlayerPhysics {
  private player: Player
  private scene: THREE.Scene
  
  // Raycasters for collision detection
  private groundRaycaster: THREE.Raycaster
  private wallRaycasters: THREE.Raycaster[]
  
  // Collision objects (exclude from collision)
  private excludeFromCollision: Set<THREE.Object3D> = new Set()
  
  // Event listeners
  private eventListeners: Map<string, Set<EventCallback>> = new Map()

  constructor(player: Player, scene: THREE.Scene) {
    this.player = player
    this.scene = scene
    
    // Initialize ground raycaster
    this.groundRaycaster = new THREE.Raycaster()
    this.groundRaycaster.far = PhysicsConfig.PLAYER_HEIGHT + PhysicsConfig.GROUND_CHECK_DISTANCE
    
    // Initialize wall raycasters (8 directions for better coverage)
    this.wallRaycasters = []
    for (let i = 0; i < 8; i++) {
      const raycaster = new THREE.Raycaster()
      raycaster.far = PhysicsConfig.PLAYER_RADIUS * 1.5
      this.wallRaycasters.push(raycaster)
    }
  }


  /**
   * Update physics for the player
   * 
   * @param deltaTime - Time elapsed since last frame
   */
  update(deltaTime: number): void {
    // Check ground state
    const groundY = this.checkGround()
    
    // Update player physics with ground position
    this.player.updatePhysics(deltaTime, groundY)
  }

  /**
   * Check for ground below player
   * Requirements: 1.3 - Ground detection
   * 
   * @returns Y position of ground, or 0 if no ground found
   */
  checkGround(): number {
    const position = this.player.getPosition3()
    
    // Cast ray downward from player position
    const rayOrigin = new THREE.Vector3(
      position.x,
      position.y + PhysicsConfig.PLAYER_HEIGHT / 2,
      position.z
    )
    
    this.groundRaycaster.set(rayOrigin, new THREE.Vector3(0, -1, 0))
    
    const intersects = this.groundRaycaster.intersectObjects(
      this.getCollidableObjects(),
      true
    )
    
    if (intersects.length > 0) {
      const hit = intersects[0]
      const groundY = hit.point.y
      
      // Check if player is close enough to be considered on ground
      const distanceToGround = position.y - groundY
      
      if (distanceToGround <= PhysicsConfig.GROUND_CHECK_DISTANCE) {
        if (!this.player.isOnGround()) {
          this.player.setOnGround(true)
          this.emit(PhysicsEvent.GROUND_STATE_CHANGED, { onGround: true })
        }
        return groundY
      }
    }
    
    // No ground found or too far
    if (this.player.isOnGround()) {
      this.player.setOnGround(false)
      this.emit(PhysicsEvent.GROUND_STATE_CHANGED, { onGround: false })
    }
    
    return 0 // Default ground level
  }

  /**
   * Check and resolve wall collisions
   * Requirements: 1.3 - Wall collision
   * 
   * @param movement - Intended movement vector
   * @returns Adjusted movement vector after collision resolution
   */
  resolveWallCollision(movement: THREE.Vector3): THREE.Vector3 {
    if (movement.length() === 0) return movement
    
    const position = this.player.getPosition3()
    const adjustedMovement = movement.clone()
    
    // Check collision in movement direction
    const collision = this.checkWallCollision(position, movement.clone().normalize())
    
    if (collision.collided && collision.penetration > 0) {
      // Slide along wall
      const slideDirection = this.calculateSlideDirection(movement, collision.normal)
      adjustedMovement.copy(slideDirection.multiplyScalar(movement.length() * PhysicsConfig.WALL_SLIDE_FACTOR))
      
      this.emit(PhysicsEvent.COLLISION, {
        type: 'wall',
        normal: collision.normal,
        object: collision.object,
      })
    }
    
    return adjustedMovement
  }

  /**
   * Check for wall collision in a direction
   */
  private checkWallCollision(position: THREE.Vector3, direction: THREE.Vector3): CollisionResult {
    const rayOrigin = new THREE.Vector3(
      position.x,
      position.y + PhysicsConfig.PLAYER_HEIGHT / 2,
      position.z
    )
    
    const raycaster = this.wallRaycasters[0]
    raycaster.set(rayOrigin, direction)
    raycaster.far = PhysicsConfig.PLAYER_RADIUS * 2
    
    const intersects = raycaster.intersectObjects(this.getCollidableObjects(), true)
    
    if (intersects.length > 0) {
      const hit = intersects[0]
      
      if (hit.distance < PhysicsConfig.PLAYER_RADIUS) {
        return {
          collided: true,
          normal: hit.face?.normal.clone() || new THREE.Vector3(0, 0, 1),
          penetration: PhysicsConfig.PLAYER_RADIUS - hit.distance,
          object: hit.object,
        }
      }
    }
    
    return {
      collided: false,
      normal: new THREE.Vector3(),
      penetration: 0,
    }
  }

  /**
   * Calculate slide direction along a wall
   */
  private calculateSlideDirection(movement: THREE.Vector3, wallNormal: THREE.Vector3): THREE.Vector3 {
    // Project movement onto the wall plane
    const dot = movement.dot(wallNormal)
    const slide = movement.clone().sub(wallNormal.clone().multiplyScalar(dot))
    
    // Keep only horizontal component
    slide.y = 0
    
    if (slide.length() > 0) {
      slide.normalize()
    }
    
    return slide
  }

  /**
   * Check if a position is valid (no collisions)
   */
  isPositionValid(position: THREE.Vector3): boolean {
    // Check for wall collisions in all directions
    const directions = [
      new THREE.Vector3(1, 0, 0),
      new THREE.Vector3(-1, 0, 0),
      new THREE.Vector3(0, 0, 1),
      new THREE.Vector3(0, 0, -1),
    ]
    
    for (const direction of directions) {
      const collision = this.checkWallCollision(position, direction)
      if (collision.collided && collision.penetration > 0) {
        return false
      }
    }
    
    return true
  }

  /**
   * Get all objects that should be checked for collision
   */
  private getCollidableObjects(): THREE.Object3D[] {
    const collidable: THREE.Object3D[] = []
    
    this.scene.traverse((object) => {
      // Skip excluded objects
      if (this.excludeFromCollision.has(object)) return
      
      // Skip non-mesh objects
      if (!(object instanceof THREE.Mesh)) return
      
      // Skip objects marked as non-collidable
      if (object.userData.noCollision) return
      
      collidable.push(object)
    })
    
    return collidable
  }

  /**
   * Add object to exclusion list (won't collide with player)
   */
  excludeObject(object: THREE.Object3D): void {
    this.excludeFromCollision.add(object)
  }

  /**
   * Remove object from exclusion list
   */
  includeObject(object: THREE.Object3D): void {
    this.excludeFromCollision.delete(object)
  }

  /**
   * Perform a step-up check (for climbing small obstacles)
   */
  canStepUp(position: THREE.Vector3, direction: THREE.Vector3): boolean {
    // Check if there's an obstacle at foot level
    const footCheck = this.checkWallCollision(position, direction)
    
    if (!footCheck.collided) return false
    
    // Check if there's clearance at step height
    const stepPosition = position.clone()
    stepPosition.y += PhysicsConfig.STEP_HEIGHT
    
    const stepCheck = this.checkWallCollision(stepPosition, direction)
    
    return !stepCheck.collided
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
