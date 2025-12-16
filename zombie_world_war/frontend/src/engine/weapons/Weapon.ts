import * as THREE from 'three'
import { WeaponType } from '../types'
import type { EventCallback } from '../types'

/**
 * Weapon configuration interface
 */
export interface WeaponConfig {
  id: string
  name: string
  type: WeaponType
  damage: number
  fireRate: number          // Rounds per second
  magazineSize: number
  maxReserveAmmo: number
  reloadTime: number        // Seconds
  range: number             // Units
  spread?: number           // Accuracy spread in radians (for shotguns)
  pelletCount?: number      // Number of pellets (for shotguns)
}

/**
 * Weapon events
 */
export enum WeaponEvent {
  FIRE = 'weapon:fire',
  RELOAD_START = 'weapon:reloadStart',
  RELOAD_END = 'weapon:reloadEnd',
  AMMO_CHANGED = 'weapon:ammoChanged',
  EMPTY = 'weapon:empty',
}

/**
 * Hit information for a single hit
 */
export interface HitInfo {
  point: { x: number; y: number; z: number }
  normal?: { x: number; y: number; z: number }
  object?: THREE.Object3D
  zombieId?: string
}

/**
 * Fire result interface
 */
export interface FireResult {
  success: boolean
  damage: number
  hitPoint?: THREE.Vector3
  hitNormal?: THREE.Vector3
  hitObject?: THREE.Object3D
  hits?: HitInfo[]
}

/**
 * Abstract Weapon base class
 * Requirements: 2.1, 2.2
 */
export abstract class Weapon {
  // Configuration
  readonly id: string
  readonly name: string
  readonly type: WeaponType
  readonly damage: number
  readonly fireRate: number
  readonly magazineSize: number
  readonly maxReserveAmmo: number
  readonly reloadTime: number
  readonly range: number
  readonly spread: number
  readonly pelletCount: number

  // State
  protected _currentAmmo: number
  protected _reserveAmmo: number
  protected _isReloading: boolean = false
  protected _lastFireTime: number = 0
  protected _reloadPromise: Promise<void> | null = null

  // Event listeners
  private eventListeners: Map<string, Set<EventCallback>> = new Map()

  constructor(config: WeaponConfig) {
    this.id = config.id
    this.name = config.name
    this.type = config.type
    this.damage = config.damage
    this.fireRate = config.fireRate
    this.magazineSize = config.magazineSize
    this.maxReserveAmmo = config.maxReserveAmmo
    this.reloadTime = config.reloadTime
    this.range = config.range
    this.spread = config.spread ?? 0
    this.pelletCount = config.pelletCount ?? 1

    this._currentAmmo = this.magazineSize
    this._reserveAmmo = this.maxReserveAmmo
  }

  // ==================== Getters ====================

  get currentAmmo(): number {
    return this._currentAmmo
  }

  get reserveAmmo(): number {
    return this._reserveAmmo
  }

  get isReloading(): boolean {
    return this._isReloading
  }

  get totalAmmo(): number {
    return this._currentAmmo + this._reserveAmmo
  }

  // ==================== Core Methods ====================

  /**
   * Check if weapon can fire
   * Requirements: 2.6
   */
  canFire(): boolean {
    if (this._currentAmmo <= 0) return false
    if (this._isReloading) return false

    // Check fire rate
    const now = performance.now()
    const timeSinceLastFire = (now - this._lastFireTime) / 1000
    const fireInterval = 1 / this.fireRate

    return timeSinceLastFire >= fireInterval
  }

  /**
   * Check if weapon can reload
   * Requirements: 2.2
   */
  canReload(): boolean {
    if (this._isReloading) return false
    if (this._currentAmmo >= this.magazineSize) return false
    if (this._reserveAmmo <= 0) return false
    return true
  }

  /**
   * Fire the weapon - abstract method to be implemented by subclasses
   * Requirements: 2.1
   */
  abstract fire(origin: THREE.Vector3, direction: THREE.Vector3, scene?: THREE.Scene): FireResult

  /**
   * Perform the actual fire action (called by subclasses)
   * Returns true if fire was successful
   */
  protected performFire(): boolean {
    if (!this.canFire()) {
      if (this._currentAmmo <= 0) {
        this.emit(WeaponEvent.EMPTY)
      }
      return false
    }

    this._currentAmmo--
    this._lastFireTime = performance.now()

    this.emit(WeaponEvent.AMMO_CHANGED, {
      currentAmmo: this._currentAmmo,
      reserveAmmo: this._reserveAmmo,
    })

    this.emit(WeaponEvent.FIRE)

    return true
  }

  /**
   * Reload the weapon
   * Requirements: 2.2
   */
  async reload(): Promise<void> {
    if (!this.canReload()) return

    this._isReloading = true
    this.emit(WeaponEvent.RELOAD_START)

    // Create reload promise
    this._reloadPromise = new Promise<void>((resolve) => {
      setTimeout(() => {
        this.completeReload()
        resolve()
      }, this.reloadTime * 1000)
    })

    await this._reloadPromise
  }

  /**
   * Complete the reload process
   */
  protected completeReload(): void {
    if (!this._isReloading) return

    const ammoNeeded = this.magazineSize - this._currentAmmo
    const ammoToTransfer = Math.min(ammoNeeded, this._reserveAmmo)

    this._currentAmmo += ammoToTransfer
    this._reserveAmmo -= ammoToTransfer
    this._isReloading = false
    this._reloadPromise = null

    this.emit(WeaponEvent.RELOAD_END)
    this.emit(WeaponEvent.AMMO_CHANGED, {
      currentAmmo: this._currentAmmo,
      reserveAmmo: this._reserveAmmo,
    })
  }

  /**
   * Cancel reload (e.g., when switching weapons)
   */
  cancelReload(): void {
    this._isReloading = false
    this._reloadPromise = null
  }

  /**
   * Add ammo to reserve
   */
  addAmmo(amount: number): void {
    this._reserveAmmo = Math.min(this._reserveAmmo + amount, this.maxReserveAmmo)
    this.emit(WeaponEvent.AMMO_CHANGED, {
      currentAmmo: this._currentAmmo,
      reserveAmmo: this._reserveAmmo,
    })
  }

  /**
   * Set ammo directly (for loading saved state)
   */
  setAmmo(currentAmmo: number, reserveAmmo: number): void {
    this._currentAmmo = Math.max(0, Math.min(currentAmmo, this.magazineSize))
    this._reserveAmmo = Math.max(0, Math.min(reserveAmmo, this.maxReserveAmmo))
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

  protected emit(event: string, data?: unknown): void {
    const listeners = this.eventListeners.get(event)
    if (listeners) {
      listeners.forEach((callback) => callback(data))
    }
  }

  // ==================== Serialization ====================

  toState(): { id: string; currentAmmo: number; reserveAmmo: number } {
    return {
      id: this.id,
      currentAmmo: this._currentAmmo,
      reserveAmmo: this._reserveAmmo,
    }
  }

  fromState(state: { currentAmmo: number; reserveAmmo: number }): void {
    this.setAmmo(state.currentAmmo, state.reserveAmmo)
  }
}
