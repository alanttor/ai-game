/**
 * Core type definitions for the game engine
 */

// Vector3 type for 3D positions and directions
export interface Vector3 {
  x: number
  y: number
  z: number
}

// Euler rotation type
export interface Euler {
  x: number
  y: number
  z: number
}

// Game state types
export interface GameState {
  player: PlayerState
  wave: WaveState
  zombies: ZombieState[]
  score: number
  playTime: number
  timestamp: number
}

export interface PlayerState {
  position: Vector3
  rotation: Euler
  health: number
  stamina: number
  weapons: WeaponState[]
  currentWeaponIndex: number
}

export interface WeaponState {
  id: string
  currentAmmo: number
  reserveAmmo: number
}

export interface WaveState {
  currentWave: number
  zombiesKilled: number
  totalZombiesInWave: number
  isPreparationPhase: boolean
}

export interface ZombieState {
  id: string
  position: Vector3
  health: number
  variant: ZombieVariant
  state: ZombieStateType
}

// Enums
export enum WeaponType {
  PISTOL = 'pistol',
  RIFLE = 'rifle',
  SHOTGUN = 'shotgun',
  MELEE = 'melee',
}

export enum ZombieVariant {
  WALKER = 'walker',
  RUNNER = 'runner',
  BRUTE = 'brute',
  CRAWLER = 'crawler',
}

export enum ZombieStateType {
  IDLE = 'idle',
  WANDERING = 'wandering',
  CHASING = 'chasing',
  ATTACKING = 'attacking',
  DYING = 'dying',
}

// Event callback type
export type EventCallback = (data?: unknown) => void

// Game engine events
export enum GameEvent {
  GAME_START = 'game:start',
  GAME_PAUSE = 'game:pause',
  GAME_RESUME = 'game:resume',
  GAME_STOP = 'game:stop',
  GAME_OVER = 'game:over',
  WAVE_START = 'wave:start',
  WAVE_END = 'wave:end',
  PLAYER_DAMAGE = 'player:damage',
  PLAYER_DEATH = 'player:death',
  ZOMBIE_SPAWN = 'zombie:spawn',
  ZOMBIE_DEATH = 'zombie:death',
}
