import * as THREE from 'three'
import { WeaponType } from '../types'

/**
 * Muzzle flash configuration
 */
interface MuzzleFlashConfig {
  color: number
  intensity: number
  size: number
  duration: number  // milliseconds
}

/**
 * Default muzzle flash configs by weapon type
 */
const MUZZLE_FLASH_CONFIGS: Record<string, MuzzleFlashConfig> = {
  [WeaponType.PISTOL]: {
    color: 0xffaa00,
    intensity: 2,
    size: 0.3,
    duration: 50,
  },
  [WeaponType.RIFLE]: {
    color: 0xffcc00,
    intensity: 3,
    size: 0.4,
    duration: 40,
  },
  [WeaponType.SHOTGUN]: {
    color: 0xff8800,
    intensity: 4,
    size: 0.6,
    duration: 80,
  },
}

/**
 * WeaponVisuals - Handles weapon visual effects
 * Requirements: 2.5
 */
export class WeaponVisuals {
  private scene: THREE.Scene
  private camera: THREE.PerspectiveCamera

  // Muzzle flash components
  private muzzleFlashLight: THREE.PointLight | null = null
  private muzzleFlashMesh: THREE.Mesh | null = null
  private muzzleFlashTimeout: ReturnType<typeof setTimeout> | null = null

  // Weapon model (placeholder for future 3D models)
  private weaponModel: THREE.Group | null = null
  private weaponOffset: THREE.Vector3 = new THREE.Vector3(0.3, -0.3, -0.5)

  // Animation state
  private recoilAmount: number = 0
  private recoilRecoverySpeed: number = 10

  constructor(scene: THREE.Scene, camera: THREE.PerspectiveCamera) {
    this.scene = scene
    this.camera = camera
    this.initMuzzleFlash()
  }

  /**
   * Initialize muzzle flash components
   */
  private initMuzzleFlash(): void {
    // Create point light for muzzle flash
    this.muzzleFlashLight = new THREE.PointLight(0xffaa00, 0, 10)
    this.muzzleFlashLight.visible = false
    this.scene.add(this.muzzleFlashLight)

    // Create muzzle flash sprite/mesh
    const flashGeometry = new THREE.PlaneGeometry(0.3, 0.3)
    const flashMaterial = new THREE.MeshBasicMaterial({
      color: 0xffaa00,
      transparent: true,
      opacity: 0,
      side: THREE.DoubleSide,
      blending: THREE.AdditiveBlending,
    })
    this.muzzleFlashMesh = new THREE.Mesh(flashGeometry, flashMaterial)
    this.muzzleFlashMesh.visible = false
    this.scene.add(this.muzzleFlashMesh)
  }

  /**
   * Show muzzle flash effect
   * Requirements: 2.5
   */
  showMuzzleFlash(weaponType: WeaponType): void {
    if (weaponType === WeaponType.MELEE) return

    const config = MUZZLE_FLASH_CONFIGS[weaponType] || MUZZLE_FLASH_CONFIGS[WeaponType.PISTOL]

    // Position muzzle flash in front of camera
    const flashPosition = this.getMuzzlePosition()

    // Update light
    if (this.muzzleFlashLight) {
      this.muzzleFlashLight.position.copy(flashPosition)
      this.muzzleFlashLight.color.setHex(config.color)
      this.muzzleFlashLight.intensity = config.intensity
      this.muzzleFlashLight.visible = true
    }

    // Update mesh
    if (this.muzzleFlashMesh) {
      this.muzzleFlashMesh.position.copy(flashPosition)
      this.muzzleFlashMesh.lookAt(this.camera.position)
      this.muzzleFlashMesh.scale.setScalar(config.size)
      ;(this.muzzleFlashMesh.material as THREE.MeshBasicMaterial).color.setHex(config.color)
      ;(this.muzzleFlashMesh.material as THREE.MeshBasicMaterial).opacity = 1
      this.muzzleFlashMesh.visible = true
    }

    // Apply recoil
    this.applyRecoil(weaponType)

    // Clear previous timeout
    if (this.muzzleFlashTimeout) {
      clearTimeout(this.muzzleFlashTimeout)
    }

    // Hide after duration
    this.muzzleFlashTimeout = setTimeout(() => {
      this.hideMuzzleFlash()
    }, config.duration)
  }

  /**
   * Hide muzzle flash effect
   */
  private hideMuzzleFlash(): void {
    if (this.muzzleFlashLight) {
      this.muzzleFlashLight.visible = false
      this.muzzleFlashLight.intensity = 0
    }

    if (this.muzzleFlashMesh) {
      this.muzzleFlashMesh.visible = false
      ;(this.muzzleFlashMesh.material as THREE.MeshBasicMaterial).opacity = 0
    }
  }

  /**
   * Get muzzle position based on camera
   */
  private getMuzzlePosition(): THREE.Vector3 {
    const position = new THREE.Vector3()
    
    // Get camera direction
    const direction = new THREE.Vector3(0, 0, -1)
    direction.applyQuaternion(this.camera.quaternion)

    // Position in front of camera
    position.copy(this.camera.position)
    position.addScaledVector(direction, 1.5)

    // Offset slightly down and right for weapon position
    const right = new THREE.Vector3(1, 0, 0)
    right.applyQuaternion(this.camera.quaternion)
    position.addScaledVector(right, 0.2)

    const down = new THREE.Vector3(0, -1, 0)
    position.addScaledVector(down, 0.1)

    return position
  }

  /**
   * Apply recoil effect
   */
  private applyRecoil(weaponType: WeaponType): void {
    switch (weaponType) {
      case WeaponType.PISTOL:
        this.recoilAmount = 0.02
        break
      case WeaponType.RIFLE:
        this.recoilAmount = 0.015
        break
      case WeaponType.SHOTGUN:
        this.recoilAmount = 0.05
        break
      default:
        this.recoilAmount = 0
    }
  }

  /**
   * Update weapon visuals (call each frame)
   */
  update(deltaTime: number): void {
    // Recover from recoil
    if (this.recoilAmount > 0) {
      this.recoilAmount -= this.recoilRecoverySpeed * deltaTime
      if (this.recoilAmount < 0) {
        this.recoilAmount = 0
      }
    }

    // Update weapon model position if exists
    if (this.weaponModel) {
      this.updateWeaponModelPosition()
    }
  }

  /**
   * Update weapon model position to follow camera
   */
  private updateWeaponModelPosition(): void {
    if (!this.weaponModel) return

    // Base position relative to camera
    const position = new THREE.Vector3()
    position.copy(this.weaponOffset)

    // Apply recoil offset
    position.z += this.recoilAmount

    // Transform to world space
    position.applyQuaternion(this.camera.quaternion)
    position.add(this.camera.position)

    this.weaponModel.position.copy(position)
    this.weaponModel.quaternion.copy(this.camera.quaternion)
  }

  /**
   * Set weapon model (for future 3D model loading)
   */
  setWeaponModel(model: THREE.Group | null): void {
    // Remove old model
    if (this.weaponModel) {
      this.scene.remove(this.weaponModel)
    }

    this.weaponModel = model

    if (model) {
      this.scene.add(model)
      this.updateWeaponModelPosition()
    }
  }

  /**
   * Get current recoil amount (for camera shake)
   */
  getRecoilAmount(): number {
    return this.recoilAmount
  }

  /**
   * Cleanup resources
   */
  dispose(): void {
    if (this.muzzleFlashTimeout) {
      clearTimeout(this.muzzleFlashTimeout)
    }

    if (this.muzzleFlashLight) {
      this.scene.remove(this.muzzleFlashLight)
      this.muzzleFlashLight.dispose()
    }

    if (this.muzzleFlashMesh) {
      this.scene.remove(this.muzzleFlashMesh)
      ;(this.muzzleFlashMesh.geometry as THREE.BufferGeometry).dispose()
      ;(this.muzzleFlashMesh.material as THREE.Material).dispose()
    }

    if (this.weaponModel) {
      this.scene.remove(this.weaponModel)
    }
  }
}
