import * as THREE from 'three'
import { Weapon, WeaponConfig, FireResult } from './Weapon'
import { WeaponType } from '../types'

/**
 * Default shotgun configuration
 */
const DEFAULT_SHOTGUN_CONFIG: WeaponConfig = {
  id: 'shotgun',
  name: 'Shotgun',
  type: WeaponType.SHOTGUN,
  damage: 15,            // Per pellet
  fireRate: 1,           // 1 round per second
  magazineSize: 8,
  maxReserveAmmo: 48,
  reloadTime: 3.0,       // 3 seconds
  range: 25,             // 25 units (short range)
  spread: 0.1,           // Spread in radians
  pelletCount: 8,        // 8 pellets per shot
}

/**
 * Shotgun weapon class
 * High damage at close range with multiple pellets
 * Requirements: 2.1, 2.2
 */
export class Shotgun extends Weapon {
  constructor(config: Partial<WeaponConfig> = {}) {
    super({ ...DEFAULT_SHOTGUN_CONFIG, ...config })
  }

  /**
   * Fire the shotgun
   * Fires multiple pellets with spread
   * Requirements: 2.1
   */
  fire(origin: THREE.Vector3, direction: THREE.Vector3, scene?: THREE.Scene): FireResult {
    if (!this.performFire()) {
      return { success: false, damage: 0 }
    }

    let totalDamage = 0
    let closestHit: { point: THREE.Vector3; normal?: THREE.Vector3; object?: THREE.Object3D } | null = null
    let closestDistance = Infinity

    // Fire multiple pellets
    for (let i = 0; i < this.pelletCount; i++) {
      // Apply random spread to direction
      const spreadDirection = this.applySpread(direction.clone())

      if (scene) {
        const raycaster = new THREE.Raycaster(origin, spreadDirection.normalize(), 0, this.range)
        const intersects = raycaster.intersectObjects(scene.children, true)

        if (intersects.length > 0) {
          const hit = intersects[0]
          totalDamage += this.damage

          // Track closest hit for return value
          if (hit.distance < closestDistance) {
            closestDistance = hit.distance
            closestHit = {
              point: hit.point,
              normal: hit.face?.normal,
              object: hit.object,
            }
          }
        }
      } else {
        // No scene, assume all pellets hit
        totalDamage += this.damage
      }
    }

    if (closestHit) {
      return {
        success: true,
        damage: totalDamage,
        hitPoint: closestHit.point,
        hitNormal: closestHit.normal,
        hitObject: closestHit.object,
      }
    }

    return { success: true, damage: totalDamage }
  }

  /**
   * Apply random spread to a direction vector
   */
  private applySpread(direction: THREE.Vector3): THREE.Vector3 {
    // Random angle within spread cone
    const spreadAngle = (Math.random() - 0.5) * this.spread * 2
    const spreadAngle2 = (Math.random() - 0.5) * this.spread * 2

    // Create rotation quaternion for spread
    const spreadQuat = new THREE.Quaternion()
    spreadQuat.setFromEuler(new THREE.Euler(spreadAngle, spreadAngle2, 0))

    // Apply spread rotation
    direction.applyQuaternion(spreadQuat)

    return direction
  }
}
