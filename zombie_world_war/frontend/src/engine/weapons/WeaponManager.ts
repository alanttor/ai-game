import * as THREE from 'three'
import { Weapon, FireResult, WeaponEvent } from './Weapon'
import { Pistol } from './Pistol'
import { Rifle } from './Rifle'
import { Shotgun } from './Shotgun'
import { MeleeWeapon } from './MeleeWeapon'
import type { EventCallback, WeaponState } from '../types'

/**
 * WeaponManager events
 */
export enum WeaponManagerEvent {
  WEAPON_SWITCHED = 'weaponManager:switched',
  WEAPON_FIRED = 'weaponManager:fired',
  WEAPON_RELOAD_START = 'weaponManager:reloadStart',
  WEAPON_RELOAD_END = 'weaponManager:reloadEnd',
  AMMO_CHANGED = 'weaponManager:ammoChanged',
  WEAPON_EMPTY = 'weaponManager:empty',
}

/**
 * Maximum number of weapon slots
 */
const MAX_WEAPON_SLOTS = 4

/**
 * WeaponManager - Manages player's weapon inventory and switching
 * Requirements: 2.1, 2.2, 2.3, 2.4, 2.6
 */
export class WeaponManager {
  // Weapon inventory (4 slots)
  private weapons: (Weapon | null)[] = [null, null, null, null]
  private currentWeaponIndex: number = 0

  // Event listeners
  private eventListeners: Map<string, Set<EventCallback>> = new Map()

  constructor() {
    // Initialize with default weapons
    this.initializeDefaultWeapons()
  }

  /**
   * Initialize default weapon loadout
   */
  private initializeDefaultWeapons(): void {
    this.weapons[0] = new Pistol()
    this.weapons[1] = new Rifle()
    this.weapons[2] = new Shotgun()
    this.weapons[3] = new MeleeWeapon()

    // Subscribe to weapon events
    this.weapons.forEach((weapon) => {
      if (weapon) {
        this.subscribeToWeaponEvents(weapon)
      }
    })
  }

  /**
   * Subscribe to a weapon's events
   */
  private subscribeToWeaponEvents(weapon: Weapon): void {
    weapon.on(WeaponEvent.FIRE, () => {
      if (weapon === this.getCurrentWeapon()) {
        this.emit(WeaponManagerEvent.WEAPON_FIRED, { weapon })
      }
    })

    weapon.on(WeaponEvent.RELOAD_START, () => {
      if (weapon === this.getCurrentWeapon()) {
        this.emit(WeaponManagerEvent.WEAPON_RELOAD_START, { weapon })
      }
    })

    weapon.on(WeaponEvent.RELOAD_END, () => {
      if (weapon === this.getCurrentWeapon()) {
        this.emit(WeaponManagerEvent.WEAPON_RELOAD_END, { weapon })
      }
    })

    weapon.on(WeaponEvent.AMMO_CHANGED, (data) => {
      if (weapon === this.getCurrentWeapon()) {
        this.emit(WeaponManagerEvent.AMMO_CHANGED, { weapon, ...data as object })
      }
    })

    weapon.on(WeaponEvent.EMPTY, () => {
      if (weapon === this.getCurrentWeapon()) {
        this.emit(WeaponManagerEvent.WEAPON_EMPTY, { weapon })
      }
    })
  }

  // ==================== Weapon Access ====================

  /**
   * Get current weapon
   */
  getCurrentWeapon(): Weapon | null {
    return this.weapons[this.currentWeaponIndex]
  }

  /**
   * Get current weapon index
   */
  getCurrentWeaponIndex(): number {
    return this.currentWeaponIndex
  }

  /**
   * Get weapon at slot
   */
  getWeaponAtSlot(slot: number): Weapon | null {
    if (slot < 0 || slot >= MAX_WEAPON_SLOTS) return null
    return this.weapons[slot]
  }

  /**
   * Get all weapons
   */
  getAllWeapons(): (Weapon | null)[] {
    return [...this.weapons]
  }

  /**
   * Get number of weapons
   */
  getWeaponCount(): number {
    return this.weapons.filter((w) => w !== null).length
  }

  // ==================== Weapon Switching ====================

  /**
   * Switch to weapon at specific slot
   * Requirements: 2.4
   * 
   * @param slot - Weapon slot (0-3)
   * @returns true if switch was successful
   */
  switchToSlot(slot: number): boolean {
    if (slot < 0 || slot >= MAX_WEAPON_SLOTS) return false
    if (this.weapons[slot] === null) return false
    if (slot === this.currentWeaponIndex) return false

    // Cancel current weapon's reload
    const currentWeapon = this.getCurrentWeapon()
    if (currentWeapon) {
      currentWeapon.cancelReload()
    }

    const previousIndex = this.currentWeaponIndex
    this.currentWeaponIndex = slot

    this.emit(WeaponManagerEvent.WEAPON_SWITCHED, {
      previousIndex,
      currentIndex: slot,
      weapon: this.getCurrentWeapon(),
    })

    return true
  }

  /**
   * Cycle to next weapon
   * Requirements: 2.3
   * 
   * @returns true if switch was successful
   */
  cycleNext(): boolean {
    const startIndex = this.currentWeaponIndex
    let nextIndex = (this.currentWeaponIndex + 1) % MAX_WEAPON_SLOTS

    // Find next available weapon
    while (nextIndex !== startIndex) {
      if (this.weapons[nextIndex] !== null) {
        return this.switchToSlot(nextIndex)
      }
      nextIndex = (nextIndex + 1) % MAX_WEAPON_SLOTS
    }

    return false
  }

  /**
   * Cycle to previous weapon
   * Requirements: 2.3
   * 
   * @returns true if switch was successful
   */
  cyclePrevious(): boolean {
    const startIndex = this.currentWeaponIndex
    let prevIndex = (this.currentWeaponIndex - 1 + MAX_WEAPON_SLOTS) % MAX_WEAPON_SLOTS

    // Find previous available weapon
    while (prevIndex !== startIndex) {
      if (this.weapons[prevIndex] !== null) {
        return this.switchToSlot(prevIndex)
      }
      prevIndex = (prevIndex - 1 + MAX_WEAPON_SLOTS) % MAX_WEAPON_SLOTS
    }

    return false
  }

  // ==================== Weapon Actions ====================

  /**
   * Fire current weapon
   * Requirements: 2.1, 2.6
   */
  fire(origin: THREE.Vector3, direction: THREE.Vector3, scene?: THREE.Scene): FireResult {
    const weapon = this.getCurrentWeapon()
    if (!weapon) {
      return { success: false, damage: 0 }
    }

    return weapon.fire(origin, direction, scene)
  }

  /**
   * Reload current weapon
   * Requirements: 2.2
   */
  async reload(): Promise<void> {
    const weapon = this.getCurrentWeapon()
    if (!weapon) return

    await weapon.reload()
  }

  /**
   * Check if current weapon can fire
   */
  canFire(): boolean {
    const weapon = this.getCurrentWeapon()
    return weapon ? weapon.canFire() : false
  }

  /**
   * Check if current weapon can reload
   */
  canReload(): boolean {
    const weapon = this.getCurrentWeapon()
    return weapon ? weapon.canReload() : false
  }

  /**
   * Check if current weapon is reloading
   */
  isReloading(): boolean {
    const weapon = this.getCurrentWeapon()
    return weapon ? weapon.isReloading : false
  }

  // ==================== Weapon Management ====================

  /**
   * Set weapon at slot
   */
  setWeaponAtSlot(slot: number, weapon: Weapon | null): void {
    if (slot < 0 || slot >= MAX_WEAPON_SLOTS) return

    // Unsubscribe from old weapon
    const oldWeapon = this.weapons[slot]
    if (oldWeapon) {
      // Note: In a full implementation, we'd properly unsubscribe
    }

    this.weapons[slot] = weapon

    // Subscribe to new weapon
    if (weapon) {
      this.subscribeToWeaponEvents(weapon)
    }
  }

  /**
   * Add ammo to a specific weapon type
   */
  addAmmoToWeapon(weaponId: string, amount: number): void {
    const weapon = this.weapons.find((w) => w?.id === weaponId)
    if (weapon) {
      weapon.addAmmo(amount)
    }
  }

  // ==================== Serialization ====================

  /**
   * Get weapon states for saving
   */
  toState(): { weapons: WeaponState[]; currentWeaponIndex: number } {
    return {
      weapons: this.weapons.map((w) =>
        w ? w.toState() : { id: '', currentAmmo: 0, reserveAmmo: 0 }
      ),
      currentWeaponIndex: this.currentWeaponIndex,
    }
  }

  /**
   * Restore weapon states from save
   */
  fromState(state: { weapons: WeaponState[]; currentWeaponIndex: number }): void {
    state.weapons.forEach((weaponState, index) => {
      const weapon = this.weapons[index]
      if (weapon && weaponState.id === weapon.id) {
        weapon.fromState(weaponState)
      }
    })

    this.currentWeaponIndex = state.currentWeaponIndex
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
