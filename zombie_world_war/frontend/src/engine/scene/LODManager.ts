import * as THREE from 'three'
import type { EventCallback } from '../types'

/**
 * LOD level configuration
 */
export interface LODLevel {
  distance: number
  detail: 'high' | 'medium' | 'low' | 'billboard'
}

/**
 * Performance metrics
 */
export interface PerformanceMetrics {
  fps: number
  frameTime: number
  drawCalls: number
  triangles: number
  visibleObjects: number
  culledObjects: number
}

/**
 * LOD events
 */
export enum LODEvent {
  QUALITY_CHANGED = 'lod:qualityChanged',
  PERFORMANCE_WARNING = 'lod:performanceWarning',
}

/**
 * LODManager - Handles Level of Detail and performance optimization
 * Requirements: 5.3
 */
export class LODManager {
  private scene: THREE.Scene
  private camera: THREE.PerspectiveCamera
  private renderer: THREE.WebGLRenderer

  // LOD objects tracking
  private lodObjects: Map<string, THREE.LOD> = new Map()

  // Frustum culling
  private frustum: THREE.Frustum = new THREE.Frustum()
  private projScreenMatrix: THREE.Matrix4 = new THREE.Matrix4()

  // Performance monitoring
  private frameCount: number = 0
  private lastFPSUpdate: number = 0
  private currentFPS: number = 60
  private targetFPS: number = 60
  private frameTimes: number[] = []

  // Adaptive quality
  private adaptiveQualityEnabled: boolean = true
  private currentQualityLevel: number = 1 // 0-2 (low, medium, high)
  private qualityAdjustCooldown: number = 0

  // Object pools for reuse
  private geometryPool: Map<string, THREE.BufferGeometry[]> = new Map()

  // Event system
  private eventListeners: Map<string, Set<EventCallback>> = new Map()

  // Culling stats
  private visibleCount: number = 0
  private culledCount: number = 0


  constructor(scene: THREE.Scene, camera: THREE.PerspectiveCamera, renderer: THREE.WebGLRenderer) {
    this.scene = scene
    this.camera = camera
    this.renderer = renderer
  }

  /**
   * Update LOD system - call every frame
   */
  update(deltaTime: number): void {
    // Update performance metrics
    this.updatePerformanceMetrics(deltaTime)

    // Update frustum for culling
    this.updateFrustum()

    // Perform frustum culling
    this.performFrustumCulling()

    // Update LOD levels based on camera distance
    this.updateLODLevels()

    // Adaptive quality adjustment
    if (this.adaptiveQualityEnabled) {
      this.adjustQuality(deltaTime)
    }
  }

  /**
   * Update performance metrics
   */
  private updatePerformanceMetrics(deltaTime: number): void {
    this.frameCount++
    this.frameTimes.push(deltaTime * 1000)

    // Keep only last 60 frame times
    if (this.frameTimes.length > 60) {
      this.frameTimes.shift()
    }

    // Update FPS every second
    const now = performance.now()
    if (now - this.lastFPSUpdate >= 1000) {
      this.currentFPS = this.frameCount
      this.frameCount = 0
      this.lastFPSUpdate = now
    }
  }

  /**
   * Update frustum matrix for culling
   */
  private updateFrustum(): void {
    this.projScreenMatrix.multiplyMatrices(
      this.camera.projectionMatrix,
      this.camera.matrixWorldInverse
    )
    this.frustum.setFromProjectionMatrix(this.projScreenMatrix)
  }

  /**
   * Perform frustum culling on scene objects
   */
  private performFrustumCulling(): void {
    this.visibleCount = 0
    this.culledCount = 0

    this.scene.traverse((object) => {
      // Skip non-mesh objects and always-visible objects
      if (!(object instanceof THREE.Mesh) || object.userData.noCull) {
        return
      }

      // Skip objects without geometry bounds
      if (!object.geometry.boundingSphere) {
        object.geometry.computeBoundingSphere()
      }

      // Get world position for culling check
      const worldPosition = new THREE.Vector3()
      object.getWorldPosition(worldPosition)

      // Create bounding sphere in world space
      const boundingSphere = object.geometry.boundingSphere!.clone()
      boundingSphere.center.copy(worldPosition)

      // Apply scale to radius
      const scale = object.scale
      const maxScale = Math.max(scale.x, scale.y, scale.z)
      boundingSphere.radius *= maxScale

      // Check if in frustum
      const isVisible = this.frustum.intersectsSphere(boundingSphere)
      object.visible = isVisible

      if (isVisible) {
        this.visibleCount++
      } else {
        this.culledCount++
      }
    })
  }

  /**
   * Update LOD levels for all LOD objects
   */
  private updateLODLevels(): void {
    this.lodObjects.forEach((lod) => {
      lod.update(this.camera)
    })
  }

  /**
   * Adjust quality based on performance
   */
  private adjustQuality(deltaTime: number): void {
    // Cooldown to prevent rapid quality changes
    if (this.qualityAdjustCooldown > 0) {
      this.qualityAdjustCooldown -= deltaTime
      return
    }

    const avgFrameTime = this.frameTimes.reduce((a, b) => a + b, 0) / this.frameTimes.length

    // Target frame time for 60 FPS is ~16.67ms
    const targetFrameTime = 1000 / this.targetFPS

    if (avgFrameTime > targetFrameTime * 1.5 && this.currentQualityLevel > 0) {
      // Performance is poor, reduce quality
      this.currentQualityLevel--
      this.applyQualityLevel()
      this.qualityAdjustCooldown = 3 // Wait 3 seconds before next adjustment
      this.emit(LODEvent.PERFORMANCE_WARNING, { fps: this.currentFPS, quality: this.currentQualityLevel })
    } else if (avgFrameTime < targetFrameTime * 0.7 && this.currentQualityLevel < 2) {
      // Performance is good, increase quality
      this.currentQualityLevel++
      this.applyQualityLevel()
      this.qualityAdjustCooldown = 5 // Wait 5 seconds before next adjustment
    }
  }

  /**
   * Apply current quality level settings
   */
  private applyQualityLevel(): void {
    switch (this.currentQualityLevel) {
      case 0: // Low
        this.renderer.setPixelRatio(1)
        this.setLODDistances(20, 40, 80)
        break
      case 1: // Medium
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5))
        this.setLODDistances(30, 60, 120)
        break
      case 2: // High
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
        this.setLODDistances(50, 100, 200)
        break
    }

    this.emit(LODEvent.QUALITY_CHANGED, { level: this.currentQualityLevel })
  }

  /**
   * Set LOD distances for all LOD objects
   */
  private setLODDistances(near: number, mid: number, far: number): void {
    this.lodObjects.forEach((lod) => {
      const levels = lod.levels
      if (levels.length >= 3) {
        levels[0].distance = 0
        levels[1].distance = near
        levels[2].distance = mid
        if (levels.length >= 4) {
          levels[3].distance = far
        }
      }
    })
  }


  // ==================== LOD Object Creation ====================

  /**
   * Create a LOD object with multiple detail levels
   */
  createLODObject(
    id: string,
    highDetail: THREE.Object3D,
    mediumDetail?: THREE.Object3D,
    lowDetail?: THREE.Object3D,
    billboard?: THREE.Object3D
  ): THREE.LOD {
    const lod = new THREE.LOD()

    // Add high detail (closest)
    lod.addLevel(highDetail, 0)

    // Add medium detail
    if (mediumDetail) {
      lod.addLevel(mediumDetail, 30)
    }

    // Add low detail
    if (lowDetail) {
      lod.addLevel(lowDetail, 60)
    }

    // Add billboard (furthest)
    if (billboard) {
      lod.addLevel(billboard, 120)
    }

    this.lodObjects.set(id, lod)
    return lod
  }

  /**
   * Create simplified geometry for LOD
   */
  createSimplifiedGeometry(
    geometry: THREE.BufferGeometry,
    targetRatio: number
  ): THREE.BufferGeometry {
    // Simple vertex reduction by sampling
    const positions = geometry.getAttribute('position')
    if (!positions) return geometry.clone()

    const vertexCount = positions.count
    const targetCount = Math.floor(vertexCount * targetRatio)

    if (targetCount >= vertexCount) return geometry.clone()

    // Create simplified geometry
    const simplified = new THREE.BufferGeometry()
    const newPositions: number[] = []
    const step = Math.ceil(vertexCount / targetCount)

    for (let i = 0; i < vertexCount; i += step) {
      newPositions.push(
        positions.getX(i),
        positions.getY(i),
        positions.getZ(i)
      )
    }

    simplified.setAttribute(
      'position',
      new THREE.Float32BufferAttribute(newPositions, 3)
    )

    // Copy normals if present
    const normals = geometry.getAttribute('normal')
    if (normals) {
      const newNormals: number[] = []
      for (let i = 0; i < vertexCount; i += step) {
        newNormals.push(
          normals.getX(i),
          normals.getY(i),
          normals.getZ(i)
        )
      }
      simplified.setAttribute(
        'normal',
        new THREE.Float32BufferAttribute(newNormals, 3)
      )
    }

    simplified.computeBoundingSphere()
    return simplified
  }

  /**
   * Create a billboard sprite for distant objects
   */
  createBillboard(
    texture: THREE.Texture | null,
    color: number = 0x888888,
    size: number = 10
  ): THREE.Sprite {
    const material = new THREE.SpriteMaterial({
      map: texture,
      color: color,
      transparent: true,
      opacity: 0.8,
    })
    const sprite = new THREE.Sprite(material)
    sprite.scale.set(size, size, 1)
    return sprite
  }

  /**
   * Remove a LOD object
   */
  removeLODObject(id: string): void {
    const lod = this.lodObjects.get(id)
    if (lod) {
      this.scene.remove(lod)
      this.lodObjects.delete(id)
    }
  }

  // ==================== Object Pooling ====================

  /**
   * Get geometry from pool or create new
   */
  getPooledGeometry(type: string, createFn: () => THREE.BufferGeometry): THREE.BufferGeometry {
    const pool = this.geometryPool.get(type)
    if (pool && pool.length > 0) {
      return pool.pop()!
    }
    return createFn()
  }

  /**
   * Return geometry to pool
   */
  returnToPool(type: string, geometry: THREE.BufferGeometry): void {
    if (!this.geometryPool.has(type)) {
      this.geometryPool.set(type, [])
    }
    const pool = this.geometryPool.get(type)!
    if (pool.length < 50) { // Max pool size
      pool.push(geometry)
    } else {
      geometry.dispose()
    }
  }

  // ==================== Performance Getters ====================

  /**
   * Get current performance metrics
   */
  getPerformanceMetrics(): PerformanceMetrics {
    const info = this.renderer.info
    const avgFrameTime = this.frameTimes.length > 0
      ? this.frameTimes.reduce((a, b) => a + b, 0) / this.frameTimes.length
      : 16.67

    return {
      fps: this.currentFPS,
      frameTime: avgFrameTime,
      drawCalls: info.render.calls,
      triangles: info.render.triangles,
      visibleObjects: this.visibleCount,
      culledObjects: this.culledCount,
    }
  }

  /**
   * Get current FPS
   */
  getFPS(): number {
    return this.currentFPS
  }

  /**
   * Get current quality level (0-2)
   */
  getQualityLevel(): number {
    return this.currentQualityLevel
  }

  /**
   * Set quality level manually
   */
  setQualityLevel(level: number): void {
    this.currentQualityLevel = Math.max(0, Math.min(2, level))
    this.applyQualityLevel()
  }

  /**
   * Enable/disable adaptive quality
   */
  setAdaptiveQuality(enabled: boolean): void {
    this.adaptiveQualityEnabled = enabled
  }

  /**
   * Set target FPS
   */
  setTargetFPS(fps: number): void {
    this.targetFPS = Math.max(30, Math.min(144, fps))
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
    // Clear LOD objects
    this.lodObjects.forEach((lod) => {
      lod.traverse((object) => {
        if (object instanceof THREE.Mesh) {
          object.geometry.dispose()
          if (Array.isArray(object.material)) {
            object.material.forEach(m => m.dispose())
          } else {
            object.material.dispose()
          }
        }
      })
    })
    this.lodObjects.clear()

    // Clear geometry pools
    this.geometryPool.forEach((pool) => {
      pool.forEach(geometry => geometry.dispose())
    })
    this.geometryPool.clear()

    // Clear event listeners
    this.eventListeners.clear()
  }
}
