/**
 * GameStateSerializer - Handles serialization and deserialization of game state
 * Requirements: 6.1, 6.2, 12.1, 12.2, 12.3, 12.5
 */

import type { GameState, PlayerState, WeaponState, WaveState, ZombieState, Vector3 } from '../types'
import { ZombieVariant, ZombieStateType } from '../types'

/**
 * Error thrown when deserialization fails due to invalid JSON structure
 */
export class DeserializationError extends Error {
  public readonly field: string
  public readonly details: string

  constructor(field: string, details: string) {
    super(`Deserialization error at field '${field}': ${details}`)
    this.name = 'DeserializationError'
    this.field = field
    this.details = details
  }
}

/**
 * Rounds a number to 3 decimal places for Vector3 precision preservation
 * Requirements: 12.5
 */
function roundToThreeDecimals(value: number): number {
  return Math.round(value * 1000) / 1000
}

/**
 * Serializes a Vector3 with precision to 3 decimal places
 * Requirements: 12.5
 */
function serializeVector3(vec: Vector3): Vector3 {
  return {
    x: roundToThreeDecimals(vec.x),
    y: roundToThreeDecimals(vec.y),
    z: roundToThreeDecimals(vec.z),
  }
}

/**
 * Validates and deserializes a Vector3 from unknown input
 */
function deserializeVector3(data: unknown, fieldPath: string): Vector3 {
  if (typeof data !== 'object' || data === null) {
    throw new DeserializationError(fieldPath, 'Expected an object')
  }

  const obj = data as Record<string, unknown>

  if (typeof obj.x !== 'number') {
    throw new DeserializationError(`${fieldPath}.x`, 'Expected a number')
  }
  if (typeof obj.y !== 'number') {
    throw new DeserializationError(`${fieldPath}.y`, 'Expected a number')
  }
  if (typeof obj.z !== 'number') {
    throw new DeserializationError(`${fieldPath}.z`, 'Expected a number')
  }

  return {
    x: roundToThreeDecimals(obj.x),
    y: roundToThreeDecimals(obj.y),
    z: roundToThreeDecimals(obj.z),
  }
}

/**
 * Validates and deserializes a WeaponState from unknown input
 */
function deserializeWeaponState(data: unknown, fieldPath: string): WeaponState {
  if (typeof data !== 'object' || data === null) {
    throw new DeserializationError(fieldPath, 'Expected an object')
  }

  const obj = data as Record<string, unknown>

  if (typeof obj.id !== 'string') {
    throw new DeserializationError(`${fieldPath}.id`, 'Expected a string')
  }
  if (typeof obj.currentAmmo !== 'number') {
    throw new DeserializationError(`${fieldPath}.currentAmmo`, 'Expected a number')
  }
  if (typeof obj.reserveAmmo !== 'number') {
    throw new DeserializationError(`${fieldPath}.reserveAmmo`, 'Expected a number')
  }

  return {
    id: obj.id,
    currentAmmo: obj.currentAmmo,
    reserveAmmo: obj.reserveAmmo,
  }
}

/**
 * Validates and deserializes a PlayerState from unknown input
 */
function deserializePlayerState(data: unknown, fieldPath: string): PlayerState {
  if (typeof data !== 'object' || data === null) {
    throw new DeserializationError(fieldPath, 'Expected an object')
  }

  const obj = data as Record<string, unknown>

  if (typeof obj.health !== 'number') {
    throw new DeserializationError(`${fieldPath}.health`, 'Expected a number')
  }
  if (typeof obj.stamina !== 'number') {
    throw new DeserializationError(`${fieldPath}.stamina`, 'Expected a number')
  }
  if (typeof obj.currentWeaponIndex !== 'number') {
    throw new DeserializationError(`${fieldPath}.currentWeaponIndex`, 'Expected a number')
  }
  if (!Array.isArray(obj.weapons)) {
    throw new DeserializationError(`${fieldPath}.weapons`, 'Expected an array')
  }

  return {
    position: deserializeVector3(obj.position, `${fieldPath}.position`),
    rotation: deserializeVector3(obj.rotation, `${fieldPath}.rotation`),
    health: obj.health,
    stamina: obj.stamina,
    weapons: obj.weapons.map((w, i) => deserializeWeaponState(w, `${fieldPath}.weapons[${i}]`)),
    currentWeaponIndex: obj.currentWeaponIndex,
  }
}


/**
 * Validates and deserializes a WaveState from unknown input
 */
function deserializeWaveState(data: unknown, fieldPath: string): WaveState {
  if (typeof data !== 'object' || data === null) {
    throw new DeserializationError(fieldPath, 'Expected an object')
  }

  const obj = data as Record<string, unknown>

  if (typeof obj.currentWave !== 'number') {
    throw new DeserializationError(`${fieldPath}.currentWave`, 'Expected a number')
  }
  if (typeof obj.zombiesKilled !== 'number') {
    throw new DeserializationError(`${fieldPath}.zombiesKilled`, 'Expected a number')
  }
  if (typeof obj.totalZombiesInWave !== 'number') {
    throw new DeserializationError(`${fieldPath}.totalZombiesInWave`, 'Expected a number')
  }
  if (typeof obj.isPreparationPhase !== 'boolean') {
    throw new DeserializationError(`${fieldPath}.isPreparationPhase`, 'Expected a boolean')
  }

  return {
    currentWave: obj.currentWave,
    zombiesKilled: obj.zombiesKilled,
    totalZombiesInWave: obj.totalZombiesInWave,
    isPreparationPhase: obj.isPreparationPhase,
  }
}

/**
 * Validates that a value is a valid ZombieVariant
 */
function isValidZombieVariant(value: unknown): value is ZombieVariant {
  return Object.values(ZombieVariant).includes(value as ZombieVariant)
}

/**
 * Validates that a value is a valid ZombieStateType
 */
function isValidZombieStateType(value: unknown): value is ZombieStateType {
  return Object.values(ZombieStateType).includes(value as ZombieStateType)
}

/**
 * Validates and deserializes a ZombieState from unknown input
 */
function deserializeZombieState(data: unknown, fieldPath: string): ZombieState {
  if (typeof data !== 'object' || data === null) {
    throw new DeserializationError(fieldPath, 'Expected an object')
  }

  const obj = data as Record<string, unknown>

  if (typeof obj.id !== 'string') {
    throw new DeserializationError(`${fieldPath}.id`, 'Expected a string')
  }
  if (typeof obj.health !== 'number') {
    throw new DeserializationError(`${fieldPath}.health`, 'Expected a number')
  }
  if (!isValidZombieVariant(obj.variant)) {
    throw new DeserializationError(
      `${fieldPath}.variant`,
      `Expected one of: ${Object.values(ZombieVariant).join(', ')}`
    )
  }
  if (!isValidZombieStateType(obj.state)) {
    throw new DeserializationError(
      `${fieldPath}.state`,
      `Expected one of: ${Object.values(ZombieStateType).join(', ')}`
    )
  }

  return {
    id: obj.id,
    position: deserializeVector3(obj.position, `${fieldPath}.position`),
    health: obj.health,
    variant: obj.variant,
    state: obj.state,
  }
}


/**
 * GameStateSerializer class for serializing and deserializing game state
 * Requirements: 6.1, 6.2, 12.1, 12.2, 12.3, 12.5
 */
export class GameStateSerializer {
  /**
   * Serializes a GameState object to JSON string
   * Preserves Vector3 precision to 3 decimal places
   * Requirements: 6.1, 12.1, 12.5
   */
  static serialize(state: GameState): string {
    const serialized: GameState = {
      player: {
        position: serializeVector3(state.player.position),
        rotation: serializeVector3(state.player.rotation),
        health: state.player.health,
        stamina: state.player.stamina,
        weapons: state.player.weapons.map((w) => ({
          id: w.id,
          currentAmmo: w.currentAmmo,
          reserveAmmo: w.reserveAmmo,
        })),
        currentWeaponIndex: state.player.currentWeaponIndex,
      },
      wave: {
        currentWave: state.wave.currentWave,
        zombiesKilled: state.wave.zombiesKilled,
        totalZombiesInWave: state.wave.totalZombiesInWave,
        isPreparationPhase: state.wave.isPreparationPhase,
      },
      zombies: state.zombies.map((z) => ({
        id: z.id,
        position: serializeVector3(z.position),
        health: z.health,
        variant: z.variant,
        state: z.state,
      })),
      score: state.score,
      playTime: state.playTime,
      timestamp: state.timestamp,
    }

    return JSON.stringify(serialized)
  }

  /**
   * Deserializes a JSON string to GameState object
   * Validates all fields and throws DeserializationError for invalid input
   * Requirements: 6.2, 12.2, 12.4
   */
  static deserialize(json: string): GameState {
    let parsed: unknown

    try {
      parsed = JSON.parse(json)
    } catch (e) {
      throw new DeserializationError('root', 'Invalid JSON format')
    }

    if (typeof parsed !== 'object' || parsed === null) {
      throw new DeserializationError('root', 'Expected an object')
    }

    const obj = parsed as Record<string, unknown>

    if (typeof obj.score !== 'number') {
      throw new DeserializationError('score', 'Expected a number')
    }
    if (typeof obj.playTime !== 'number') {
      throw new DeserializationError('playTime', 'Expected a number')
    }
    if (typeof obj.timestamp !== 'number') {
      throw new DeserializationError('timestamp', 'Expected a number')
    }
    if (!Array.isArray(obj.zombies)) {
      throw new DeserializationError('zombies', 'Expected an array')
    }

    return {
      player: deserializePlayerState(obj.player, 'player'),
      wave: deserializeWaveState(obj.wave, 'wave'),
      zombies: obj.zombies.map((z, i) => deserializeZombieState(z, `zombies[${i}]`)),
      score: obj.score,
      playTime: obj.playTime,
      timestamp: obj.timestamp,
    }
  }
}
