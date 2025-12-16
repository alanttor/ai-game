import type { Vector3, EventCallback } from '../types'
import { ZombieStateType } from '../types'
import { AudioManager, SoundEffect, SoundType, MusicTrack, AudioConfig } from './AudioManager'

/**
 * Sound URLs - In a real game, these would point to actual audio files
 * For now, we define the structure for when audio assets are added
 */
export const SoundUrls = {
  // Weapon sounds
  [SoundEffect.PISTOL_FIRE]: '/audio/weapons/pistol_fire.mp3',
  [SoundEffect.RIFLE_FIRE]: '/audio/weapons/rifle_fire.mp3',
  [SoundEffect.SHOTGUN_FIRE]: '/audio/weapons/shotgun_fire.mp3',
  [SoundEffect.MELEE_SWING]: '/audio/weapons/melee_swing.mp3',
  [SoundEffect.RELOAD]: '/audio/weapons/reload.mp3',
  [SoundEffect.EMPTY_CLICK]: '/audio/weapons/empty_click.mp3',
  
  // Zombie sounds
  [SoundEffect.ZOMBIE_GROWL]: '/audio/zombies/growl.mp3',
  [SoundEffect.ZOMBIE_ATTACK]: '/audio/zombies/attack.mp3',
  [SoundEffect.ZOMBIE_DEATH]: '/audio/zombies/death.mp3',
  [SoundEffect.ZOMBIE_HIT]: '/audio/zombies/hit.mp3',
  
  // Player sounds
  [SoundEffect.PLAYER_HURT]: '/audio/player/hurt.mp3',
  [SoundEffect.PLAYER_DEATH]: '/audio/player/death.mp3',
  [SoundEffect.FOOTSTEP]: '/audio/player/footstep.mp3',
  [SoundEffect.JUMP]: '/audio/player/jump.mp3',
  [SoundEffect.LAND]: '/audio/player/land.mp3',
  
  // UI sounds
  [SoundEffect.BUTTON_CLICK]: '/audio/ui/click.mp3',
  [SoundEffect.MENU_OPEN]: '/audio/ui/menu_open.mp3',
  [SoundEffect.MENU_CLOSE]: '/audio/ui/menu_close.mp3',
  
  // Wave sounds
  [SoundEffect.WAVE_START]: '/audio/waves/wave_start.mp3',
  [SoundEffect.WAVE_COMPLETE]: '/audio/waves/wave_complete.mp3',
  [SoundEffect.PREPARATION_TICK]: '/audio/waves/tick.mp3',
  
  // Music tracks
  [MusicTrack.MENU]: '/audio/music/menu.mp3',
  [MusicTrack.AMBIENT]: '/audio/music/ambient.mp3',
  [MusicTrack.COMBAT]: '/audio/music/combat.mp3',
  [MusicTrack.TENSE]: '/audio/music/tense.mp3',
  [MusicTrack.GAME_OVER]: '/audio/music/game_over.mp3',
}

/**
 * Zombie ambient sound configuration
 */
interface ZombieAmbientSound {
  soundId: string | null
  lastPlayTime: number
  interval: number
}

/**
 * GameAudioController - Integrates AudioManager with game systems
 * Handles weapon sounds, zombie sounds, and ambient audio
 * Requirements: 10.1, 10.2
 */
export class GameAudioController {
  private audioManager: AudioManager
  private isInitialized: boolean = false
  
  // Zombie ambient sounds tracking
  private zombieAmbientSounds: Map<string, ZombieAmbientSound> = new Map()
  private zombieGrowlMinInterval: number = 3.0  // Minimum seconds between growls
  private zombieGrowlMaxInterval: number = 8.0  // Maximum seconds between growls
  
  // Player position for 3D audio
  private playerPosition: Vector3 = { x: 0, y: 0, z: 0 }
  
  // Active looping sounds
  private activeLoopingSounds: Map<string, string> = new Map()
  
  // Event listeners
  private eventListeners: Map<string, Set<EventCallback>> = new Map()

  constructor(audioManager: AudioManager) {
    this.audioManager = audioManager
  }

  /**
   * Initialize the game audio controller
   * Preloads all game sounds
   */
  async init(): Promise<void> {
    if (this.isInitialized) return
    
    // Preload all sounds (in a real game, handle missing files gracefully)
    const soundsToLoad: Array<{ id: string; url: string; type: SoundType }> = []
    
    // Add weapon sounds
    soundsToLoad.push(
      { id: SoundEffect.PISTOL_FIRE, url: SoundUrls[SoundEffect.PISTOL_FIRE], type: SoundType.SFX },
      { id: SoundEffect.RIFLE_FIRE, url: SoundUrls[SoundEffect.RIFLE_FIRE], type: SoundType.SFX },
      { id: SoundEffect.SHOTGUN_FIRE, url: SoundUrls[SoundEffect.SHOTGUN_FIRE], type: SoundType.SFX },
      { id: SoundEffect.MELEE_SWING, url: SoundUrls[SoundEffect.MELEE_SWING], type: SoundType.SFX },
      { id: SoundEffect.RELOAD, url: SoundUrls[SoundEffect.RELOAD], type: SoundType.SFX },
      { id: SoundEffect.EMPTY_CLICK, url: SoundUrls[SoundEffect.EMPTY_CLICK], type: SoundType.SFX },
    )
    
    // Add zombie sounds
    soundsToLoad.push(
      { id: SoundEffect.ZOMBIE_GROWL, url: SoundUrls[SoundEffect.ZOMBIE_GROWL], type: SoundType.AMBIENT },
      { id: SoundEffect.ZOMBIE_ATTACK, url: SoundUrls[SoundEffect.ZOMBIE_ATTACK], type: SoundType.SFX },
      { id: SoundEffect.ZOMBIE_DEATH, url: SoundUrls[SoundEffect.ZOMBIE_DEATH], type: SoundType.SFX },
      { id: SoundEffect.ZOMBIE_HIT, url: SoundUrls[SoundEffect.ZOMBIE_HIT], type: SoundType.SFX },
    )
    
    // Add player sounds
    soundsToLoad.push(
      { id: SoundEffect.PLAYER_HURT, url: SoundUrls[SoundEffect.PLAYER_HURT], type: SoundType.SFX },
      { id: SoundEffect.PLAYER_DEATH, url: SoundUrls[SoundEffect.PLAYER_DEATH], type: SoundType.SFX },
      { id: SoundEffect.FOOTSTEP, url: SoundUrls[SoundEffect.FOOTSTEP], type: SoundType.SFX },
      { id: SoundEffect.JUMP, url: SoundUrls[SoundEffect.JUMP], type: SoundType.SFX },
      { id: SoundEffect.LAND, url: SoundUrls[SoundEffect.LAND], type: SoundType.SFX },
    )
    
    // Add wave sounds
    soundsToLoad.push(
      { id: SoundEffect.WAVE_START, url: SoundUrls[SoundEffect.WAVE_START], type: SoundType.SFX },
      { id: SoundEffect.WAVE_COMPLETE, url: SoundUrls[SoundEffect.WAVE_COMPLETE], type: SoundType.SFX },
      { id: SoundEffect.PREPARATION_TICK, url: SoundUrls[SoundEffect.PREPARATION_TICK], type: SoundType.UI },
    )
    
    // Add music tracks
    soundsToLoad.push(
      { id: MusicTrack.MENU, url: SoundUrls[MusicTrack.MENU], type: SoundType.MUSIC },
      { id: MusicTrack.AMBIENT, url: SoundUrls[MusicTrack.AMBIENT], type: SoundType.MUSIC },
      { id: MusicTrack.COMBAT, url: SoundUrls[MusicTrack.COMBAT], type: SoundType.MUSIC },
      { id: MusicTrack.TENSE, url: SoundUrls[MusicTrack.TENSE], type: SoundType.MUSIC },
      { id: MusicTrack.GAME_OVER, url: SoundUrls[MusicTrack.GAME_OVER], type: SoundType.MUSIC },
    )
    
    // Try to load sounds, but don't fail if files don't exist
    for (const sound of soundsToLoad) {
      try {
        await this.audioManager.loadSound(sound.id, sound.url, sound.type)
      } catch (error) {
        // Sound file not found - this is expected until audio assets are added
        console.debug(`Audio file not found: ${sound.url}`)
      }
    }
    
    this.isInitialized = true
  }


  // ==================== Weapon Sounds ====================

  /**
   * Play weapon fire sound with 3D positioning
   * Requirements: 10.1
   * @param weaponType - Type of weapon being fired
   * @param position - Position of the weapon
   */
  playWeaponFire(weaponType: string, position: Vector3): void {
    let soundId: SoundEffect
    
    switch (weaponType.toLowerCase()) {
      case 'pistol':
        soundId = SoundEffect.PISTOL_FIRE
        break
      case 'rifle':
        soundId = SoundEffect.RIFLE_FIRE
        break
      case 'shotgun':
        soundId = SoundEffect.SHOTGUN_FIRE
        break
      case 'melee':
        soundId = SoundEffect.MELEE_SWING
        break
      default:
        soundId = SoundEffect.PISTOL_FIRE
    }
    
    // Play as 3D sound at weapon position
    this.audioManager.play3D(soundId, position, {
      volume: 1.0,
      refDistance: 5,
      maxDistance: 50,
    })
  }

  /**
   * Play reload sound
   */
  playReload(position: Vector3): void {
    this.audioManager.play3D(SoundEffect.RELOAD, position, {
      volume: 0.8,
      refDistance: 2,
      maxDistance: 20,
    })
  }

  /**
   * Play empty magazine click
   */
  playEmptyClick(position: Vector3): void {
    this.audioManager.play3D(SoundEffect.EMPTY_CLICK, position, {
      volume: 0.6,
      refDistance: 1,
      maxDistance: 10,
    })
  }

  // ==================== Zombie Sounds ====================

  /**
   * Play zombie growl with 3D positioning
   * Requirements: 10.2
   * @param position - Position of the zombie
   */
  playZombieGrowl(position: Vector3): void {
    this.audioManager.play3D(SoundEffect.ZOMBIE_GROWL, position, {
      volume: 0.7,
      refDistance: 5,
      maxDistance: AudioConfig.MAX_DISTANCE,
      rolloffFactor: 1.5,
    })
  }

  /**
   * Play zombie attack sound
   * @param position - Position of the zombie
   */
  playZombieAttack(position: Vector3): void {
    this.audioManager.play3D(SoundEffect.ZOMBIE_ATTACK, position, {
      volume: 0.9,
      refDistance: 3,
      maxDistance: 30,
    })
  }

  /**
   * Play zombie death sound
   * @param position - Position of the zombie
   */
  playZombieDeath(position: Vector3): void {
    this.audioManager.play3D(SoundEffect.ZOMBIE_DEATH, position, {
      volume: 0.8,
      refDistance: 5,
      maxDistance: 40,
    })
  }

  /**
   * Play zombie hit sound
   * @param position - Position of the zombie
   */
  playZombieHit(position: Vector3): void {
    this.audioManager.play3D(SoundEffect.ZOMBIE_HIT, position, {
      volume: 0.7,
      refDistance: 3,
      maxDistance: 30,
    })
  }

  /**
   * Register a zombie for ambient sounds
   * @param zombieId - Unique zombie identifier
   */
  registerZombie(zombieId: string): void {
    if (!this.zombieAmbientSounds.has(zombieId)) {
      this.zombieAmbientSounds.set(zombieId, {
        soundId: null,
        lastPlayTime: 0,
        interval: this.getRandomGrowlInterval(),
      })
    }
  }

  /**
   * Unregister a zombie from ambient sounds
   * @param zombieId - Unique zombie identifier
   */
  unregisterZombie(zombieId: string): void {
    const ambient = this.zombieAmbientSounds.get(zombieId)
    if (ambient?.soundId) {
      this.audioManager.stopSound(ambient.soundId)
    }
    this.zombieAmbientSounds.delete(zombieId)
  }

  /**
   * Update zombie ambient sounds
   * Requirements: 10.2
   * @param _deltaTime - Time since last update (unused, timing based on performance.now)
   * @param zombies - Array of zombie data with id and position
   */
  updateZombieAmbientSounds(
    _deltaTime: number,
    zombies: Array<{ id: string; position: Vector3; state: ZombieStateType }>
  ): void {
    const currentTime = performance.now() / 1000
    
    for (const zombie of zombies) {
      // Skip dying zombies
      if (zombie.state === ZombieStateType.DYING) continue
      
      let ambient = this.zombieAmbientSounds.get(zombie.id)
      
      if (!ambient) {
        this.registerZombie(zombie.id)
        ambient = this.zombieAmbientSounds.get(zombie.id)!
      }
      
      // Check if it's time for a new growl
      if (currentTime - ambient.lastPlayTime >= ambient.interval) {
        // Calculate distance to player for volume adjustment
        const distance = this.calculateDistance(zombie.position, this.playerPosition)
        
        // Only play if within hearing range
        if (distance < AudioConfig.MAX_DISTANCE) {
          this.playZombieGrowl(zombie.position)
          ambient.lastPlayTime = currentTime
          ambient.interval = this.getRandomGrowlInterval()
        }
      }
    }
  }

  /**
   * Get random interval for zombie growls
   */
  private getRandomGrowlInterval(): number {
    return this.zombieGrowlMinInterval + 
      Math.random() * (this.zombieGrowlMaxInterval - this.zombieGrowlMinInterval)
  }

  /**
   * Calculate distance between two positions
   */
  private calculateDistance(pos1: Vector3, pos2: Vector3): number {
    const dx = pos1.x - pos2.x
    const dy = pos1.y - pos2.y
    const dz = pos1.z - pos2.z
    return Math.sqrt(dx * dx + dy * dy + dz * dz)
  }


  // ==================== Player Sounds ====================

  /**
   * Play player hurt sound
   */
  playPlayerHurt(): void {
    this.audioManager.play(SoundEffect.PLAYER_HURT, { volume: 1.0 })
  }

  /**
   * Play player death sound
   */
  playPlayerDeath(): void {
    this.audioManager.play(SoundEffect.PLAYER_DEATH, { volume: 1.0 })
  }

  /**
   * Play footstep sound
   * @param position - Player position
   */
  playFootstep(position: Vector3): void {
    // Slight random pitch variation for variety
    const pitchVariation = 0.9 + Math.random() * 0.2
    this.audioManager.play3D(SoundEffect.FOOTSTEP, position, {
      volume: 0.4,
      playbackRate: pitchVariation,
      refDistance: 1,
      maxDistance: 15,
    })
  }

  /**
   * Play jump sound
   */
  playJump(): void {
    this.audioManager.play(SoundEffect.JUMP, { volume: 0.6 })
  }

  /**
   * Play land sound
   */
  playLand(): void {
    this.audioManager.play(SoundEffect.LAND, { volume: 0.5 })
  }

  // ==================== Wave Sounds ====================

  /**
   * Play wave start alert sound
   * Requirements: 10.3
   */
  playWaveStart(): void {
    this.audioManager.play(SoundEffect.WAVE_START, { volume: 1.0 })
  }

  /**
   * Play wave complete sound
   */
  playWaveComplete(): void {
    this.audioManager.play(SoundEffect.WAVE_COMPLETE, { volume: 1.0 })
  }

  /**
   * Play preparation countdown tick
   */
  playPreparationTick(): void {
    this.audioManager.play(SoundEffect.PREPARATION_TICK, { volume: 0.5 })
  }

  // ==================== Music Control ====================

  /**
   * Play menu music
   */
  playMenuMusic(): void {
    this.audioManager.playMusic(MusicTrack.MENU, true)
  }

  /**
   * Play ambient/exploration music
   */
  playAmbientMusic(): void {
    this.audioManager.playMusic(MusicTrack.AMBIENT, true)
  }

  /**
   * Play combat music
   * Requirements: 10.3
   */
  playCombatMusic(): void {
    this.audioManager.playMusic(MusicTrack.COMBAT, true)
  }

  /**
   * Play tense/danger music
   * Requirements: 10.4
   */
  playTenseMusic(): void {
    this.audioManager.playMusic(MusicTrack.TENSE, true)
  }

  /**
   * Play game over music
   */
  playGameOverMusic(): void {
    this.audioManager.playMusic(MusicTrack.GAME_OVER, true)
  }

  /**
   * Stop all music
   */
  stopMusic(): void {
    this.audioManager.stopMusic()
  }

  // ==================== UI Sounds ====================

  /**
   * Play button click sound
   */
  playButtonClick(): void {
    this.audioManager.play(SoundEffect.BUTTON_CLICK, { volume: 0.5 })
  }

  /**
   * Play menu open sound
   */
  playMenuOpen(): void {
    this.audioManager.play(SoundEffect.MENU_OPEN, { volume: 0.6 })
  }

  /**
   * Play menu close sound
   */
  playMenuClose(): void {
    this.audioManager.play(SoundEffect.MENU_CLOSE, { volume: 0.6 })
  }

  // ==================== State Management ====================

  /**
   * Update player position for distance calculations
   * @param position - Current player position
   */
  setPlayerPosition(position: Vector3): void {
    this.playerPosition = { ...position }
  }

  /**
   * Update audio based on game state
   * Call this each frame
   * @param _deltaTime - Time since last update (unused, reserved for future use)
   */
  update(_deltaTime: number): void {
    // Update listener position if camera is set
    // This is handled automatically by Three.js AudioListener attached to camera
  }

  /**
   * Handle game pause
   * Requirements: 10.5
   */
  onGamePause(): void {
    this.audioManager.pause()
  }

  /**
   * Handle game resume
   * Requirements: 10.5
   */
  onGameResume(): void {
    this.audioManager.resume()
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

  // ==================== Cleanup ====================

  /**
   * Dispose of all resources
   */
  dispose(): void {
    // Stop all zombie ambient sounds
    this.zombieAmbientSounds.forEach((ambient) => {
      if (ambient.soundId) {
        this.audioManager.stopSound(ambient.soundId)
      }
    })
    this.zombieAmbientSounds.clear()
    
    // Clear active looping sounds
    this.activeLoopingSounds.forEach((soundId) => {
      this.audioManager.stopSound(soundId)
    })
    this.activeLoopingSounds.clear()
    
    // Clear event listeners
    this.eventListeners.clear()
  }

  /**
   * Get the underlying AudioManager
   */
  getAudioManager(): AudioManager {
    return this.audioManager
  }
}
