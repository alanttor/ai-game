import * as THREE from 'three'
import { Weapon, WeaponConfig, FireResult } from './Weapon'
import { WeaponType } from '../types'

/**
 * Default pistol configuration
 */
const DEFAULT_PISTOL_CONFIG: WeaponConfig = {
  id: 'pistol',
  name: 'Pistol',
  type: WeaponType.PISTOL,
  damage: 25,
  fireRate: 3,           // 3 rounds per second
  magazineSize: 15,
  maxReserveAmmo: 90,
  reloadTime: 1.5,       // 1.5 seconds
  range: 50,             // 50 units
}

/**
 * Pistol weapon class
 * A reliable sidearm with moderate damage and fire rate
 * Requirements: 2.1, 2.2
 */
export class Pistol extends Weapon {
  constructor(config: Partial<WeaponConfig> = {}) {
    super({ ...DEFAULT_PISTOL_CONFIG, ...config })
  }

  /**
   * Fire the pistol
   * Performs raycast hit detection
   * Requirements: 2.1
   */
  fire(origin: THREE.Vector3, direction: THREE.Vector3, scene?: THREE.Scene): FireResult {
    if (!this.performFire()) {
      return { success: false, damage: 0 }
    }

    // Perform raycast if scene is provided
    if (scene) {
      const raycaster = new THREE.Raycaster(origin, direction.normalize(), 0, this.range)
      const intersects = raycaster.intersectObjects(scene.children, true)

      if (intersects.length > 0) {
        const hit = intersects[0]
        return {
          success: true,
          damage: this.damage,
          hitPoint: hit.point,
          hitNormal: hit.face?.normal,
          hitObject: hit.object,
        }
      }
    }

    return { success: true, damage: this.damage }
  }
}
