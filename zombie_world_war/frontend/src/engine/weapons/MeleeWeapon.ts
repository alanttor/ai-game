import * as THREE from 'three'
import { Weapon, WeaponConfig, FireResult } from './Weapon'
import { WeaponType } from '../types'

/**
 * Default melee weapon configuration
 */
const DEFAULT_MELEE_CONFIG: WeaponConfig = {
  id: 'knife',
  name: 'Combat Knife',
  type: WeaponType.MELEE,
  damage: 50,
  fireRate: 2,           // 2 attacks per second
  magazineSize: 1,       // Melee doesn't use ammo
  maxReserveAmmo: 0,     // No reserve ammo
  reloadTime: 0,         // No reload
  range: 2,              // 2 units (melee range)
}

/**
 * MeleeWeapon class
 * Close range weapon with high damage, no ammo required
 * Requirements: 2.1, 2.6
 */
export class MeleeWeapon extends Weapon {
  constructor(config: Partial<WeaponConfig> = {}) {
    super({ ...DEFAULT_MELEE_CONFIG, ...config })
    // Melee weapons always have "ammo"
    this._currentAmmo = 1
    this._reserveAmmo = 0
  }

  /**
   * Override canFire - melee weapons always can fire (no ammo check)
   */
  canFire(): boolean {
    if (this._isReloading) return false

    // Check fire rate
    const now = performance.now()
    const timeSinceLastFire = (now - this._lastFireTime) / 1000
    const fireInterval = 1 / this.fireRate

    return timeSinceLastFire >= fireInterval
  }

  /**
   * Override canReload - melee weapons don't reload
   */
  canReload(): boolean {
    return false
  }

  /**
   * Perform melee attack
   * Checks for objects within melee range
   * Requirements: 2.1
   */
  fire(origin: THREE.Vector3, direction: THREE.Vector3, scene?: THREE.Scene): FireResult {
    // Check fire rate (melee doesn't consume ammo)
    const now = performance.now()
    const timeSinceLastFire = (now - this._lastFireTime) / 1000
    const fireInterval = 1 / this.fireRate

    if (timeSinceLastFire < fireInterval) {
      return { success: false, damage: 0 }
    }

    this._lastFireTime = now
    this.emit('weapon:fire')

    // Perform melee range check
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

  /**
   * Override reload - melee weapons don't reload
   */
  async reload(): Promise<void> {
    // Do nothing
  }

  /**
   * Override toState - melee weapons don't track ammo
   */
  toState(): { id: string; currentAmmo: number; reserveAmmo: number } {
    return {
      id: this.id,
      currentAmmo: 1,
      reserveAmmo: 0,
    }
  }
}
