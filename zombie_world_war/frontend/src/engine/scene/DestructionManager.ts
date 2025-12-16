import * as THREE from 'three'
import type { EventCallback } from '../types'

/**
 * Destructible object configuration
 */
export interface DestructibleConfig {
  health: number
  debrisCount: number
  debrisScale: number
  explosionForce: number
  soundEffect?: string
}

/**
 * Particle configuration
 */
export interface ParticleConfig {
  count: number
  size: number
  color: number
  lifetime: number
  velocity: THREE.Vector3
  spread: number
  gravity: number
}

/**
 * Destruction events
 */
export enum DestructionEvent {
  OBJECT_DAMAGED = 'destruction:damaged',
  OBJECT_DESTROYED = 'destruction:destroyed',
  DEBRIS_SPAWNED = 'destruction:debrisSpawned',
}

/**
 * Particle system for effects
 */
interface ParticleSystem {
  points: THREE.Points
  velocities: THREE.Vector3[]
  lifetimes: number[]
  maxLifetime: number
  gravity: number
  startTime: number
}

/**
 * Destructible object wrapper
 */
interface DestructibleObject {
  mesh: THREE.Mesh
  config: DestructibleConfig
  currentHealth: number
}

/**
 * DestructionManager - Handles destructible objects and particle effects
 * Requirements: 5.5
 */
export class DestructionManager {
  private scene: THREE.Scene

  // Destructible objects
  private destructibles: Map<string, DestructibleObject> = new Map()

  // Active particle systems
  private particleSystems: ParticleSystem[] = []

  // Debris objects
  private debrisObjects: THREE.Mesh[] = []
  private debrisVelocities: THREE.Vector3[] = []
  private debrisLifetimes: number[] = []

  // Materials cache
  private materials: Map<string, THREE.Material> = new Map()

  // Event system
  private eventListeners: Map<string, Set<EventCallback>> = new Map()

  // Physics constants
  private gravity: number = -9.8
  private debrisLifetime: number = 5 // seconds


  constructor(scene: THREE.Scene) {
    this.scene = scene
    this.initMaterials()
  }

  /**
   * Initialize reusable materials
   */
  private initMaterials(): void {
    // Debris materials
    this.materials.set('debris_concrete', new THREE.MeshStandardMaterial({
      color: 0x555555,
      roughness: 0.9,
    }))

    this.materials.set('debris_wood', new THREE.MeshStandardMaterial({
      color: 0x654321,
      roughness: 0.85,
    }))

    this.materials.set('debris_metal', new THREE.MeshStandardMaterial({
      color: 0x666677,
      roughness: 0.4,
      metalness: 0.8,
    }))

    this.materials.set('debris_glass', new THREE.MeshStandardMaterial({
      color: 0x88ccff,
      roughness: 0.1,
      metalness: 0.9,
      transparent: true,
      opacity: 0.6,
    }))
  }

  /**
   * Update all destruction effects
   */
  update(deltaTime: number): void {
    this.updateParticleSystems(deltaTime)
    this.updateDebris(deltaTime)
  }

  // ==================== Destructible Objects ====================

  /**
   * Register a mesh as destructible
   */
  registerDestructible(
    id: string,
    mesh: THREE.Mesh,
    config: Partial<DestructibleConfig> = {}
  ): void {
    const fullConfig: DestructibleConfig = {
      health: config.health ?? 100,
      debrisCount: config.debrisCount ?? 8,
      debrisScale: config.debrisScale ?? 0.3,
      explosionForce: config.explosionForce ?? 5,
      soundEffect: config.soundEffect,
    }

    this.destructibles.set(id, {
      mesh,
      config: fullConfig,
      currentHealth: fullConfig.health,
    })

    mesh.userData.destructibleId = id
  }

  /**
   * Damage a destructible object
   */
  damageObject(id: string, damage: number, hitPoint?: THREE.Vector3): boolean {
    const destructible = this.destructibles.get(id)
    if (!destructible) return false

    destructible.currentHealth -= damage

    this.emit(DestructionEvent.OBJECT_DAMAGED, {
      id,
      damage,
      remainingHealth: destructible.currentHealth,
    })

    // Spawn hit particles at impact point
    if (hitPoint) {
      this.spawnHitParticles(hitPoint, destructible.mesh)
    }

    // Check if destroyed
    if (destructible.currentHealth <= 0) {
      this.destroyObject(id)
      return true
    }

    return false
  }

  /**
   * Destroy a destructible object
   */
  destroyObject(id: string): void {
    const destructible = this.destructibles.get(id)
    if (!destructible) return

    const { mesh, config } = destructible
    const position = mesh.position.clone()

    // Spawn debris
    this.spawnDebris(position, config)

    // Spawn explosion particles
    this.spawnExplosionParticles(position)

    // Remove original mesh
    this.scene.remove(mesh)

    // Dispose geometry and material
    mesh.geometry.dispose()
    if (Array.isArray(mesh.material)) {
      mesh.material.forEach(m => m.dispose())
    } else {
      mesh.material.dispose()
    }

    // Remove from tracking
    this.destructibles.delete(id)

    this.emit(DestructionEvent.OBJECT_DESTROYED, { id, position })
  }

  /**
   * Get destructible health
   */
  getHealth(id: string): number {
    const destructible = this.destructibles.get(id)
    return destructible?.currentHealth ?? 0
  }

  /**
   * Check if object is destructible
   */
  isDestructible(id: string): boolean {
    return this.destructibles.has(id)
  }

  // ==================== Debris System ====================

  /**
   * Spawn debris from destroyed object
   */
  private spawnDebris(position: THREE.Vector3, config: DestructibleConfig): void {
    const materials = ['debris_concrete', 'debris_wood', 'debris_metal']

    for (let i = 0; i < config.debrisCount; i++) {
      // Random debris shape
      const size = config.debrisScale * (0.5 + Math.random() * 0.5)
      const geometry = this.createDebrisGeometry(size)

      // Random material
      const materialKey = materials[Math.floor(Math.random() * materials.length)]
      const material = this.materials.get(materialKey)!

      const debris = new THREE.Mesh(geometry, material)
      debris.position.copy(position)
      debris.position.add(new THREE.Vector3(
        (Math.random() - 0.5) * 2,
        Math.random() * 1,
        (Math.random() - 0.5) * 2
      ))
      debris.rotation.set(
        Math.random() * Math.PI,
        Math.random() * Math.PI,
        Math.random() * Math.PI
      )
      debris.castShadow = true
      debris.receiveShadow = true

      this.scene.add(debris)
      this.debrisObjects.push(debris)

      // Random velocity
      const velocity = new THREE.Vector3(
        (Math.random() - 0.5) * config.explosionForce * 2,
        Math.random() * config.explosionForce,
        (Math.random() - 0.5) * config.explosionForce * 2
      )
      this.debrisVelocities.push(velocity)
      this.debrisLifetimes.push(this.debrisLifetime)
    }

    this.emit(DestructionEvent.DEBRIS_SPAWNED, {
      position,
      count: config.debrisCount,
    })
  }

  /**
   * Create random debris geometry
   */
  private createDebrisGeometry(size: number): THREE.BufferGeometry {
    const type = Math.floor(Math.random() * 3)
    switch (type) {
      case 0:
        return new THREE.BoxGeometry(size, size * 0.5, size * 0.8)
      case 1:
        return new THREE.TetrahedronGeometry(size)
      default:
        return new THREE.DodecahedronGeometry(size * 0.5)
    }
  }

  /**
   * Update debris physics
   */
  private updateDebris(deltaTime: number): void {
    const toRemove: number[] = []

    for (let i = 0; i < this.debrisObjects.length; i++) {
      const debris = this.debrisObjects[i]
      const velocity = this.debrisVelocities[i]

      // Apply gravity
      velocity.y += this.gravity * deltaTime

      // Update position
      debris.position.add(velocity.clone().multiplyScalar(deltaTime))

      // Rotate debris
      debris.rotation.x += deltaTime * 2
      debris.rotation.z += deltaTime * 1.5

      // Ground collision
      if (debris.position.y < 0.1) {
        debris.position.y = 0.1
        velocity.y *= -0.3 // Bounce with energy loss
        velocity.x *= 0.8
        velocity.z *= 0.8
      }

      // Update lifetime
      this.debrisLifetimes[i] -= deltaTime
      if (this.debrisLifetimes[i] <= 0) {
        toRemove.push(i)
      }

      // Fade out near end of life
      if (this.debrisLifetimes[i] < 1) {
        const opacity = this.debrisLifetimes[i]
        if (debris.material instanceof THREE.MeshStandardMaterial) {
          debris.material.transparent = true
          debris.material.opacity = opacity
        }
      }
    }

    // Remove expired debris (reverse order to maintain indices)
    for (let i = toRemove.length - 1; i >= 0; i--) {
      const index = toRemove[i]
      const debris = this.debrisObjects[index]

      this.scene.remove(debris)
      debris.geometry.dispose()

      this.debrisObjects.splice(index, 1)
      this.debrisVelocities.splice(index, 1)
      this.debrisLifetimes.splice(index, 1)
    }
  }


  // ==================== Particle System ====================

  /**
   * Spawn hit particles at impact point
   */
  private spawnHitParticles(position: THREE.Vector3, _mesh: THREE.Mesh): void {
    this.createParticleSystem({
      count: 20,
      size: 0.1,
      color: 0x888888,
      lifetime: 0.5,
      velocity: new THREE.Vector3(0, 2, 0),
      spread: 2,
      gravity: 5,
    }, position)
  }

  /**
   * Spawn explosion particles
   */
  private spawnExplosionParticles(position: THREE.Vector3): void {
    // Dust cloud
    this.createParticleSystem({
      count: 50,
      size: 0.3,
      color: 0x666666,
      lifetime: 1.5,
      velocity: new THREE.Vector3(0, 3, 0),
      spread: 5,
      gravity: 2,
    }, position)

    // Sparks
    this.createParticleSystem({
      count: 30,
      size: 0.1,
      color: 0xffaa00,
      lifetime: 0.8,
      velocity: new THREE.Vector3(0, 5, 0),
      spread: 8,
      gravity: 10,
    }, position)
  }

  /**
   * Create a particle system
   */
  createParticleSystem(config: ParticleConfig, position: THREE.Vector3): void {
    const geometry = new THREE.BufferGeometry()
    const positions: number[] = []
    const velocities: THREE.Vector3[] = []
    const lifetimes: number[] = []

    for (let i = 0; i < config.count; i++) {
      // Initial position with spread
      positions.push(
        position.x + (Math.random() - 0.5) * config.spread * 0.2,
        position.y + (Math.random() - 0.5) * config.spread * 0.2,
        position.z + (Math.random() - 0.5) * config.spread * 0.2
      )

      // Random velocity
      const velocity = config.velocity.clone()
      velocity.x += (Math.random() - 0.5) * config.spread
      velocity.y += (Math.random() - 0.5) * config.spread
      velocity.z += (Math.random() - 0.5) * config.spread
      velocities.push(velocity)

      // Random lifetime variation
      lifetimes.push(config.lifetime * (0.5 + Math.random() * 0.5))
    }

    geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3))

    const material = new THREE.PointsMaterial({
      color: config.color,
      size: config.size,
      transparent: true,
      opacity: 1,
      sizeAttenuation: true,
    })

    const points = new THREE.Points(geometry, material)
    this.scene.add(points)

    this.particleSystems.push({
      points,
      velocities,
      lifetimes,
      maxLifetime: config.lifetime,
      gravity: config.gravity,
      startTime: performance.now(),
    })
  }

  /**
   * Spawn muzzle flash particles
   */
  spawnMuzzleFlash(position: THREE.Vector3, direction: THREE.Vector3): void {
    this.createParticleSystem({
      count: 15,
      size: 0.15,
      color: 0xffff00,
      lifetime: 0.1,
      velocity: direction.clone().multiplyScalar(10),
      spread: 1,
      gravity: 0,
    }, position)
  }

  /**
   * Spawn blood splatter particles
   */
  spawnBloodSplatter(position: THREE.Vector3): void {
    this.createParticleSystem({
      count: 25,
      size: 0.15,
      color: 0x880000,
      lifetime: 0.6,
      velocity: new THREE.Vector3(0, 2, 0),
      spread: 3,
      gravity: 8,
    }, position)
  }

  /**
   * Spawn spark particles
   */
  spawnSparks(position: THREE.Vector3): void {
    this.createParticleSystem({
      count: 20,
      size: 0.08,
      color: 0xffcc00,
      lifetime: 0.4,
      velocity: new THREE.Vector3(0, 3, 0),
      spread: 4,
      gravity: 15,
    }, position)
  }

  /**
   * Update particle systems
   */
  private updateParticleSystems(deltaTime: number): void {
    const toRemove: number[] = []

    for (let i = 0; i < this.particleSystems.length; i++) {
      const system = this.particleSystems[i]
      const positions = system.points.geometry.getAttribute('position') as THREE.BufferAttribute
      let allDead = true

      for (let j = 0; j < system.velocities.length; j++) {
        // Update lifetime
        system.lifetimes[j] -= deltaTime
        if (system.lifetimes[j] <= 0) continue

        allDead = false

        // Apply gravity
        system.velocities[j].y -= system.gravity * deltaTime

        // Update position
        const idx = j * 3
        positions.setX(idx / 3, positions.getX(idx / 3) + system.velocities[j].x * deltaTime)
        positions.setY(idx / 3, positions.getY(idx / 3) + system.velocities[j].y * deltaTime)
        positions.setZ(idx / 3, positions.getZ(idx / 3) + system.velocities[j].z * deltaTime)
      }

      positions.needsUpdate = true

      // Update opacity based on average lifetime
      const avgLifetime = system.lifetimes.reduce((a, b) => Math.max(a, b), 0)
      const opacity = avgLifetime / system.maxLifetime
      if (system.points.material instanceof THREE.PointsMaterial) {
        system.points.material.opacity = opacity
      }

      if (allDead) {
        toRemove.push(i)
      }
    }

    // Remove dead particle systems
    for (let i = toRemove.length - 1; i >= 0; i--) {
      const index = toRemove[i]
      const system = this.particleSystems[index]

      this.scene.remove(system.points)
      system.points.geometry.dispose()
      if (system.points.material instanceof THREE.Material) {
        system.points.material.dispose()
      }

      this.particleSystems.splice(index, 1)
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
      listeners.forEach(callback => callback(data))
    }
  }

  // ==================== Cleanup ====================

  dispose(): void {
    // Dispose destructibles
    this.destructibles.forEach((destructible) => {
      destructible.mesh.geometry.dispose()
      if (Array.isArray(destructible.mesh.material)) {
        destructible.mesh.material.forEach(m => m.dispose())
      } else {
        destructible.mesh.material.dispose()
      }
    })
    this.destructibles.clear()

    // Dispose debris
    this.debrisObjects.forEach((debris) => {
      this.scene.remove(debris)
      debris.geometry.dispose()
    })
    this.debrisObjects = []
    this.debrisVelocities = []
    this.debrisLifetimes = []

    // Dispose particle systems
    this.particleSystems.forEach((system) => {
      this.scene.remove(system.points)
      system.points.geometry.dispose()
      if (system.points.material instanceof THREE.Material) {
        system.points.material.dispose()
      }
    })
    this.particleSystems = []

    // Dispose materials
    this.materials.forEach(material => material.dispose())
    this.materials.clear()

    // Clear event listeners
    this.eventListeners.clear()
  }
}
