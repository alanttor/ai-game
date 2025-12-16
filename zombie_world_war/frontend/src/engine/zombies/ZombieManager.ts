import * as THREE from 'three'
import type { Vector3, EventCallback, ZombieState } from '../types'
import { ZombieVariant, GameEvent } from '../types'
import { Zombie, ZombieEvent } from './Zombie'
import { ZombieVisuals } from './ZombieVisuals'

/**
 * ZombieManager - Manages all zombie entities in the game
 * Handles spawning, updating, and removing zombies
 * Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6
 */
export class ZombieManager {
  // Active zombies
  private zombies: Map<string, Zombie> = new Map()
  
  // Zombie visuals for animations
  private zombieVisuals: Map<string, ZombieVisuals> = new Map()
  
  // Scene reference for adding/removing meshes
  private scene: THREE.Scene
  
  // Zombie ID counter
  private nextZombieId: number = 0
  
  // Event listeners
  private eventListeners: Map<string, Set<EventCallback>> = new Map()
  
  // Statistics
  private totalKilled: number = 0

  constructor(scene: THREE.Scene) {
    this.scene = scene
  }

  /**
   * Spawn a new zombie at the given position
   * Requirements: 3.1
   * 
   * @param position - Spawn position
   * @param variant - Zombie variant (random if not specified)
   * @returns The spawned zombie
   */
  spawnZombie(position: Vector3, variant?: ZombieVariant): Zombie {
    const id = `zombie_${this.nextZombieId++}`
    const zombieVariant = variant ?? this.getRandomVariant()
    
    const zombie = new Zombie(id, position, zombieVariant)
    
    // Setup event listeners
    this.setupZombieEvents(zombie)
    
    // Create visuals and attach mesh
    const visuals = new ZombieVisuals(zombieVariant)
    const mesh = visuals.getMesh()
    zombie.setMesh(mesh)
    this.scene.add(mesh)
    
    // Store visuals for animation updates
    this.zombieVisuals.set(id, visuals)
    
    // Add to collection
    this.zombies.set(id, zombie)
    
    // Emit spawn event
    this.emit(GameEvent.ZOMBIE_SPAWN, { zombie: zombie.toState() })
    
    return zombie
  }


  /**
   * Spawn multiple zombies at random positions around spawn points
   * 
   * @param count - Number of zombies to spawn
   * @param spawnPoints - Array of spawn point positions
   * @param radius - Spawn radius around each point
   */
  spawnWave(count: number, spawnPoints: Vector3[], radius: number = 5): Zombie[] {
    const spawned: Zombie[] = []
    
    for (let i = 0; i < count; i++) {
      // Pick random spawn point
      const spawnPoint = spawnPoints[Math.floor(Math.random() * spawnPoints.length)]
      
      // Add random offset within radius
      const angle = Math.random() * Math.PI * 2
      const distance = Math.random() * radius
      const position: Vector3 = {
        x: spawnPoint.x + Math.cos(angle) * distance,
        y: spawnPoint.y,
        z: spawnPoint.z + Math.sin(angle) * distance,
      }
      
      const zombie = this.spawnZombie(position)
      spawned.push(zombie)
    }
    
    return spawned
  }

  /**
   * Get a random zombie variant with weighted distribution
   * Requirements: 3.1
   */
  private getRandomVariant(): ZombieVariant {
    const roll = Math.random()
    
    // Weighted distribution: Walker 50%, Runner 25%, Crawler 15%, Brute 10%
    if (roll < 0.5) return ZombieVariant.WALKER
    if (roll < 0.75) return ZombieVariant.RUNNER
    if (roll < 0.9) return ZombieVariant.CRAWLER
    return ZombieVariant.BRUTE
  }

  /**
   * Create zombie visuals with animated mesh
   * Requirements: 3.1
   */
  private createZombieVisuals(variant: ZombieVariant): ZombieVisuals {
    return new ZombieVisuals(variant)
  }

  /**
   * Setup event listeners for a zombie
   */
  private setupZombieEvents(zombie: Zombie): void {
    zombie.on(ZombieEvent.DEATH, (data) => {
      this.totalKilled++
      this.emit(GameEvent.ZOMBIE_DEATH, data)
    })
    
    zombie.on(ZombieEvent.ATTACK, (data) => {
      this.emit(ZombieEvent.ATTACK, data)
    })
  }


  // Cached vector for performance
  private _cachedPlayerPos: THREE.Vector3 = new THREE.Vector3()

  /**
   * Update all zombies
   * 
   * @param deltaTime - Time elapsed since last frame
   * @param playerPosition - Current player position
   */
  update(deltaTime: number, playerPosition: Vector3): void {
    // Reuse cached vector to avoid allocations
    this._cachedPlayerPos.set(playerPosition.x, playerPosition.y, playerPosition.z)
    const toRemove: string[] = []
    
    for (const [id, zombie] of this.zombies) {
      try {
        zombie.update(deltaTime, this._cachedPlayerPos)
        
        // Update visuals/animations
        const visuals = this.zombieVisuals.get(id)
        if (visuals) {
          visuals.update(deltaTime, zombie.state, zombie.speed)
        }
        
        // Mark for removal if death animation complete
        if (zombie.shouldRemove()) {
          toRemove.push(id)
        }
      } catch (error) {
        console.error(`Error updating zombie ${id}:`, error)
        toRemove.push(id) // Remove problematic zombie
      }
    }
    
    // Remove dead zombies
    for (const id of toRemove) {
      this.removeZombie(id)
    }
  }

  /**
   * Remove a zombie by ID
   */
  removeZombie(id: string): void {
    const zombie = this.zombies.get(id)
    if (zombie) {
      // Remove mesh from scene
      const mesh = zombie.getMesh()
      if (mesh) {
        this.scene.remove(mesh)
      }
      
      // Cleanup visuals
      const visuals = this.zombieVisuals.get(id)
      if (visuals) {
        visuals.dispose()
        this.zombieVisuals.delete(id)
      }
      
      // Cleanup and remove
      zombie.dispose()
      this.zombies.delete(id)
    }
  }

  /**
   * Apply damage to a zombie
   * 
   * @param id - Zombie ID
   * @param damage - Damage amount
   * @param hitPoint - Optional hit location
   */
  damageZombie(id: string, damage: number, hitPoint?: Vector3): void {
    const zombie = this.zombies.get(id)
    if (zombie) {
      zombie.takeDamage(damage, hitPoint)
    }
  }

  /**
   * Get zombie by ID
   */
  getZombie(id: string): Zombie | undefined {
    return this.zombies.get(id)
  }

  /**
   * Get all active zombies
   */
  getAllZombies(): Zombie[] {
    return Array.from(this.zombies.values())
  }

  /**
   * Get zombies within range of a position
   */
  getZombiesInRange(position: Vector3, range: number): Zombie[] {
    return this.getAllZombies().filter((zombie) => {
      return zombie.distanceTo(position) <= range && !zombie.isDead()
    })
  }

  /**
   * Get the closest zombie to a position
   */
  getClosestZombie(position: Vector3): Zombie | null {
    let closest: Zombie | null = null
    let closestDistance = Infinity
    
    for (const zombie of this.zombies.values()) {
      if (zombie.isDead()) continue
      
      const distance = zombie.distanceTo(position)
      if (distance < closestDistance) {
        closestDistance = distance
        closest = zombie
      }
    }
    
    return closest
  }

  /**
   * Perform raycast hit detection against zombies
   * 
   * @param raycaster - Three.js raycaster
   * @returns Hit zombie and intersection point, or null
   */
  raycastZombies(raycaster: THREE.Raycaster): { zombie: Zombie; point: Vector3 } | null {
    const meshes: THREE.Object3D[] = []
    const meshToZombie: Map<THREE.Object3D, Zombie> = new Map()
    
    for (const zombie of this.zombies.values()) {
      if (zombie.isDead()) continue
      
      const mesh = zombie.getMesh()
      if (mesh) {
        meshes.push(mesh)
        meshToZombie.set(mesh, zombie)
      }
    }
    
    const intersects = raycaster.intersectObjects(meshes, true)
    
    if (intersects.length > 0) {
      // Find the root mesh (zombie group)
      let hitObject = intersects[0].object
      while (hitObject.parent && !meshToZombie.has(hitObject)) {
        hitObject = hitObject.parent
      }
      
      const zombie = meshToZombie.get(hitObject)
      if (zombie) {
        const point = intersects[0].point
        return {
          zombie,
          point: { x: point.x, y: point.y, z: point.z },
        }
      }
    }
    
    return null
  }

  // ==================== Statistics ====================

  /**
   * Get count of active (alive) zombies
   */
  getActiveCount(): number {
    let count = 0
    for (const zombie of this.zombies.values()) {
      if (!zombie.isDead()) count++
    }
    return count
  }

  /**
   * Get total zombie count (including dying)
   */
  getTotalCount(): number {
    return this.zombies.size
  }

  /**
   * Get total zombies killed
   */
  getTotalKilled(): number {
    return this.totalKilled
  }

  /**
   * Reset kill counter
   */
  resetKillCount(): void {
    this.totalKilled = 0
  }

  // ==================== Serialization ====================

  /**
   * Export all zombie states for saving
   */
  toState(): ZombieState[] {
    return this.getAllZombies().map((zombie) => zombie.toState())
  }

  /**
   * Restore zombies from saved state
   */
  fromState(states: ZombieState[]): void {
    // Clear existing zombies
    this.clear()
    
    // Recreate zombies from state
    for (const state of states) {
      const zombie = Zombie.fromState(state)
      
      // Setup events
      this.setupZombieEvents(zombie)
      
      // Create visuals and mesh
      const visuals = this.createZombieVisuals(zombie.variant)
      const mesh = visuals.getMesh()
      zombie.setMesh(mesh)
      this.scene.add(mesh)
      
      // Store visuals
      this.zombieVisuals.set(zombie.id, visuals)
      
      // Add to collection
      this.zombies.set(zombie.id, zombie)
      
      // Update next ID counter
      const idNum = parseInt(zombie.id.replace('zombie_', ''), 10)
      if (!isNaN(idNum) && idNum >= this.nextZombieId) {
        this.nextZombieId = idNum + 1
      }
    }
  }

  /**
   * Clear all zombies
   */
  clear(): void {
    for (const [id, zombie] of this.zombies) {
      const mesh = zombie.getMesh()
      if (mesh) {
        this.scene.remove(mesh)
      }
      
      // Cleanup visuals
      const visuals = this.zombieVisuals.get(id)
      if (visuals) {
        visuals.dispose()
      }
      
      zombie.dispose()
    }
    this.zombies.clear()
    this.zombieVisuals.clear()
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
   * Cleanup all resources
   */
  dispose(): void {
    this.clear()
    this.eventListeners.clear()
  }
}
