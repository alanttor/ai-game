import * as THREE from 'three'
import { Weapon, WeaponConfig, FireResult } from './Weapon'
import { WeaponType } from '../types'

/**
 * Default rifle configuration
 */
const DEFAULT_RIFLE_CONFIG: WeaponConfig = {
  id: 'rifle',
  name: 'Assault Rifle',
  type: WeaponType.RIFLE,
  damage: 30,
  fireRate: 10,          // 10 rounds per second (automatic)
  magazineSize: 30,
  maxReserveAmmo: 180,
  reloadTime: 2.5,       // 2.5 seconds
  range: 100,            // 100 units
}

/**
 * Rifle weapon class
 * High fire rate automatic weapon with good range
 * Requirements: 2.1, 2.2
 */
export class Rifle extends Weapon {
  constructor(config: Partial<WeaponConfig> = {}) {
    super({ ...DEFAULT_RIFLE_CONFIG, ...config })
  }

  /**
   * Fire the rifle
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
