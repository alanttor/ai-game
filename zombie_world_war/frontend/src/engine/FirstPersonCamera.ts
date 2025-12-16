import * as THREE from 'three'
import { Player, PlayerConfig } from './Player'
import type { EventCallback } from './types'

/**
 * Camera configuration
 */
export const CameraConfig = {
  DEFAULT_SENSITIVITY: 0.002,
  MIN_SENSITIVITY: 0.0001,
  MAX_SENSITIVITY: 0.01,
  FOV: 75,
  NEAR: 0.1,
  FAR: 1000,
}

/**
 * Camera events
 */
export enum CameraEvent {
  SENSITIVITY_CHANGED = 'camera:sensitivityChanged',
}

/**
 * FirstPersonCamera - Handles first-person camera control
 * Requirements: 1.2 - Mouse view control with configurable sensitivity
 */
export class FirstPersonCamera {
  private camera: THREE.PerspectiveCamera
  private player: Player | null = null
  private sensitivity: number = CameraConfig.DEFAULT_SENSITIVITY
  
  // Event listeners
  private eventListeners: Map<string, Set<EventCallback>> = new Map()

  constructor(aspect: number = 16 / 9) {
    this.camera = new THREE.PerspectiveCamera(
      CameraConfig.FOV,
      aspect,
      CameraConfig.NEAR,
      CameraConfig.FAR
    )
    
    // Set initial position at eye height
    this.camera.position.set(0, PlayerConfig.EYE_HEIGHT, 0)
    
    // Use YXZ order for FPS-style rotation (yaw then pitch)
    this.camera.rotation.order = 'YXZ'
  }

  /**
   * Attach camera to a player
   */
  attachToPlayer(player: Player): void {
    this.player = player
    player.attachCamera(this.camera)
  }

  /**
   * Detach camera from player
   */
  detachFromPlayer(): void {
    this.player = null
  }

  /**
   * Handle mouse movement for camera rotation
   * Requirements: 1.2 - Camera rotation proportional to (delta * sensitivity)
   * 
   * @param movementX - Raw mouse X movement
   * @param movementY - Raw mouse Y movement
   */
  handleMouseMove(movementX: number, movementY: number): void {
    if (!this.player) return
    
    // Apply sensitivity to mouse movement
    const deltaX = movementX * this.sensitivity
    const deltaY = movementY * this.sensitivity
    
    // Delegate rotation to player (which updates camera)
    this.player.rotate(deltaX, deltaY)
  }

  /**
   * Update camera aspect ratio (call on window resize)
   */
  updateAspect(aspect: number): void {
    this.camera.aspect = aspect
    this.camera.updateProjectionMatrix()
  }

  /**
   * Set mouse sensitivity
   * Requirements: 1.2 - Configurable sensitivity
   */
  setSensitivity(sensitivity: number): void {
    const oldSensitivity = this.sensitivity
    this.sensitivity = Math.max(
      CameraConfig.MIN_SENSITIVITY,
      Math.min(CameraConfig.MAX_SENSITIVITY, sensitivity)
    )
    
    if (oldSensitivity !== this.sensitivity) {
      this.emit(CameraEvent.SENSITIVITY_CHANGED, {
        previous: oldSensitivity,
        current: this.sensitivity,
      })
    }
  }

  /**
   * Get current mouse sensitivity
   */
  getSensitivity(): number {
    return this.sensitivity
  }

  /**
   * Get the Three.js camera
   */
  getCamera(): THREE.PerspectiveCamera {
    return this.camera
  }

  /**
   * Get camera position
   */
  getPosition(): THREE.Vector3 {
    return this.camera.position.clone()
  }

  /**
   * Get camera forward direction
   */
  getForwardDirection(): THREE.Vector3 {
    const direction = new THREE.Vector3(0, 0, -1)
    direction.applyQuaternion(this.camera.quaternion)
    return direction
  }

  /**
   * Get camera right direction
   */
  getRightDirection(): THREE.Vector3 {
    const direction = new THREE.Vector3(1, 0, 0)
    direction.applyQuaternion(this.camera.quaternion)
    return direction
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
