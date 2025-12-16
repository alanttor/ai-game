import * as THREE from 'three'
import type { Vector3, EventCallback } from '../types'

/**
 * Audio configuration constants
 */
export const AudioConfig = {
  // Master volume settings
  MASTER_VOLUME: 1.0,
  MUSIC_VOLUME: 0.5,
  SFX_VOLUME: 0.8,
  AMBIENT_VOLUME: 0.6,
  
  // Pause volume reduction (50% as per Requirements 10.5)
  PAUSE_VOLUME_MULTIPLIER: 0.5,
  
  // 3D audio settings
  REF_DISTANCE: 1,        // Reference distance for volume falloff
  MAX_DISTANCE: 100,      // Maximum distance for audio
  ROLLOFF_FACTOR: 1,      // How quickly volume decreases with distance
  
  // Crossfade settings
  CROSSFADE_DURATION: 2.0, // Seconds for music crossfade
}

/**
 * Audio events
 */
export enum AudioEvent {
  VOLUME_CHANGED = 'audio:volumeChanged',
  MUSIC_CHANGED = 'audio:musicChanged',
  SOUND_PLAYED = 'audio:soundPlayed',
  LOADED = 'audio:loaded',
  ERROR = 'audio:error',
}

/**
 * Sound types for categorization
 */
export enum SoundType {
  SFX = 'sfx',
  MUSIC = 'music',
  AMBIENT = 'ambient',
  UI = 'ui',
}

/**
 * Music track identifiers
 */
export enum MusicTrack {
  MENU = 'menu',
  AMBIENT = 'ambient',
  COMBAT = 'combat',
  TENSE = 'tense',
  GAME_OVER = 'gameOver',
}

/**
 * Sound effect identifiers
 */
export enum SoundEffect {
  // Weapon sounds
  PISTOL_FIRE = 'pistolFire',
  RIFLE_FIRE = 'rifleFire',
  SHOTGUN_FIRE = 'shotgunFire',
  MELEE_SWING = 'meleeSwing',
  RELOAD = 'reload',
  EMPTY_CLICK = 'emptyClick',
  
  // Zombie sounds
  ZOMBIE_GROWL = 'zombieGrowl',
  ZOMBIE_ATTACK = 'zombieAttack',
  ZOMBIE_DEATH = 'zombieDeath',
  ZOMBIE_HIT = 'zombieHit',
  
  // Player sounds
  PLAYER_HURT = 'playerHurt',
  PLAYER_DEATH = 'playerDeath',
  FOOTSTEP = 'footstep',
  JUMP = 'jump',
  LAND = 'land',
  
  // UI sounds
  BUTTON_CLICK = 'buttonClick',
  MENU_OPEN = 'menuOpen',
  MENU_CLOSE = 'menuClose',
  
  // Wave sounds
  WAVE_START = 'waveStart',
  WAVE_COMPLETE = 'waveComplete',
  PREPARATION_TICK = 'preparationTick',
}

/**
 * Cached sound data
 */
interface CachedSound {
  buffer: AudioBuffer
  type: SoundType
}

/**
 * Active sound instance
 */
interface ActiveSound {
  source: AudioBufferSourceNode
  gainNode: GainNode
  pannerNode?: PannerNode
  type: SoundType
  startTime: number
}


/**
 * AudioManager - Manages all game audio including 3D spatial sound, music, and effects
 * Uses Web Audio API for 3D positional audio
 * Requirements: 10.1, 10.2, 10.3, 10.4, 10.5
 */
export class AudioManager {
  // Audio context
  private audioContext: AudioContext | null = null
  private listener: THREE.AudioListener | null = null
  
  // Volume controls
  private _masterVolume: number = AudioConfig.MASTER_VOLUME
  private _musicVolume: number = AudioConfig.MUSIC_VOLUME
  private _sfxVolume: number = AudioConfig.SFX_VOLUME
  private _ambientVolume: number = AudioConfig.AMBIENT_VOLUME
  
  // Pause state
  private _isPaused: boolean = false
  private prePauseVolumes: { master: number; music: number; sfx: number; ambient: number } | null = null
  
  // Sound cache
  private soundCache: Map<string, CachedSound> = new Map()
  private loadingPromises: Map<string, Promise<AudioBuffer>> = new Map()
  
  // Active sounds
  private activeSounds: Map<string, ActiveSound> = new Map()
  private soundIdCounter: number = 0
  
  // Music state
  private currentMusicTrack: MusicTrack | null = null
  private currentMusicSource: AudioBufferSourceNode | null = null
  private currentMusicGain: GainNode | null = null
  private nextMusicSource: AudioBufferSourceNode | null = null
  private nextMusicGain: GainNode | null = null
  private isCrossfading: boolean = false
  
  // Gain nodes for volume control
  private masterGain: GainNode | null = null
  private musicGain: GainNode | null = null
  private sfxGain: GainNode | null = null
  private ambientGain: GainNode | null = null
  
  // Event listeners
  private eventListeners: Map<string, Set<EventCallback>> = new Map()
  
  // Three.js camera reference for listener position
  private camera: THREE.Camera | null = null

  constructor() {
    // Audio context will be created on first user interaction
  }

  /**
   * Initialize the audio manager
   * Must be called after user interaction due to browser autoplay policies
   */
  async init(camera?: THREE.Camera): Promise<void> {
    try {
      // Create audio context
      this.audioContext = new (window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext)()
      
      // Resume context if suspended (browser autoplay policy)
      if (this.audioContext.state === 'suspended') {
        await this.audioContext.resume()
      }
      
      // Create gain nodes for volume control
      this.masterGain = this.audioContext.createGain()
      this.musicGain = this.audioContext.createGain()
      this.sfxGain = this.audioContext.createGain()
      this.ambientGain = this.audioContext.createGain()
      
      // Connect gain nodes: category -> master -> destination
      this.musicGain.connect(this.masterGain)
      this.sfxGain.connect(this.masterGain)
      this.ambientGain.connect(this.masterGain)
      this.masterGain.connect(this.audioContext.destination)
      
      // Set initial volumes
      this.masterGain.gain.value = this._masterVolume
      this.musicGain.gain.value = this._musicVolume
      this.sfxGain.gain.value = this._sfxVolume
      this.ambientGain.gain.value = this._ambientVolume
      
      // Create Three.js audio listener for 3D audio
      this.listener = new THREE.AudioListener()
      
      // Attach listener to camera if provided
      if (camera) {
        this.setCamera(camera)
      }
      
      this.emit(AudioEvent.LOADED)
    } catch (error) {
      console.error('Failed to initialize AudioManager:', error)
      this.emit(AudioEvent.ERROR, { error })
    }
  }

  /**
   * Set the camera for 3D audio listener positioning
   */
  setCamera(camera: THREE.Camera): void {
    this.camera = camera
    if (this.listener && camera) {
      camera.add(this.listener)
    }
  }

  /**
   * Get the Three.js audio listener
   */
  getListener(): THREE.AudioListener | null {
    return this.listener
  }

  // ==================== Sound Loading ====================

  /**
   * Load a sound file and cache it
   * @param id - Unique identifier for the sound
   * @param url - URL to the audio file
   * @param type - Type of sound (sfx, music, ambient, ui)
   */
  async loadSound(id: string, url: string, type: SoundType = SoundType.SFX): Promise<void> {
    if (this.soundCache.has(id)) return
    
    // Check if already loading
    if (this.loadingPromises.has(id)) {
      await this.loadingPromises.get(id)
      return
    }
    
    const loadPromise = this.loadAudioBuffer(url)
    this.loadingPromises.set(id, loadPromise)
    
    try {
      const buffer = await loadPromise
      this.soundCache.set(id, { buffer, type })
    } finally {
      this.loadingPromises.delete(id)
    }
  }

  /**
   * Load audio buffer from URL
   */
  private async loadAudioBuffer(url: string): Promise<AudioBuffer> {
    if (!this.audioContext) {
      throw new Error('AudioContext not initialized')
    }
    
    const response = await fetch(url)
    const arrayBuffer = await response.arrayBuffer()
    return await this.audioContext.decodeAudioData(arrayBuffer)
  }

  /**
   * Preload multiple sounds
   */
  async preloadSounds(sounds: Array<{ id: string; url: string; type: SoundType }>): Promise<void> {
    await Promise.all(sounds.map(s => this.loadSound(s.id, s.url, s.type)))
  }

  /**
   * Check if a sound is loaded
   */
  isSoundLoaded(id: string): boolean {
    return this.soundCache.has(id)
  }


  // ==================== Sound Playback ====================

  /**
   * Play a 2D sound effect (non-positional)
   * @param id - Sound identifier
   * @param options - Playback options
   * @returns Sound instance ID for later control
   */
  play(id: string, options: {
    volume?: number
    loop?: boolean
    playbackRate?: number
  } = {}): string | null {
    const cached = this.soundCache.get(id)
    if (!cached || !this.audioContext) return null
    
    const { volume = 1.0, loop = false, playbackRate = 1.0 } = options
    
    // Create source
    const source = this.audioContext.createBufferSource()
    source.buffer = cached.buffer
    source.loop = loop
    source.playbackRate.value = playbackRate
    
    // Create gain node for this sound
    const gainNode = this.audioContext.createGain()
    gainNode.gain.value = volume
    
    // Connect to appropriate category gain
    const categoryGain = this.getCategoryGain(cached.type)
    source.connect(gainNode)
    gainNode.connect(categoryGain)
    
    // Generate unique ID
    const soundId = `sound_${this.soundIdCounter++}`
    
    // Track active sound
    this.activeSounds.set(soundId, {
      source,
      gainNode,
      type: cached.type,
      startTime: this.audioContext.currentTime,
    })
    
    // Clean up when sound ends
    source.onended = () => {
      this.activeSounds.delete(soundId)
    }
    
    // Start playback
    source.start()
    
    this.emit(AudioEvent.SOUND_PLAYED, { id, soundId, type: cached.type })
    
    return soundId
  }

  /**
   * Play a 3D positional sound
   * Requirements: 10.1, 10.2
   * @param id - Sound identifier
   * @param position - 3D position of the sound source
   * @param options - Playback options
   * @returns Sound instance ID for later control
   */
  play3D(id: string, position: Vector3, options: {
    volume?: number
    loop?: boolean
    playbackRate?: number
    refDistance?: number
    maxDistance?: number
    rolloffFactor?: number
  } = {}): string | null {
    const cached = this.soundCache.get(id)
    if (!cached || !this.audioContext) return null
    
    const {
      volume = 1.0,
      loop = false,
      playbackRate = 1.0,
      refDistance = AudioConfig.REF_DISTANCE,
      maxDistance = AudioConfig.MAX_DISTANCE,
      rolloffFactor = AudioConfig.ROLLOFF_FACTOR,
    } = options
    
    // Create source
    const source = this.audioContext.createBufferSource()
    source.buffer = cached.buffer
    source.loop = loop
    source.playbackRate.value = playbackRate
    
    // Create panner for 3D positioning
    const pannerNode = this.audioContext.createPanner()
    pannerNode.panningModel = 'HRTF'
    pannerNode.distanceModel = 'inverse'
    pannerNode.refDistance = refDistance
    pannerNode.maxDistance = maxDistance
    pannerNode.rolloffFactor = rolloffFactor
    pannerNode.setPosition(position.x, position.y, position.z)
    
    // Create gain node for this sound
    const gainNode = this.audioContext.createGain()
    gainNode.gain.value = volume
    
    // Connect: source -> panner -> gain -> category gain
    const categoryGain = this.getCategoryGain(cached.type)
    source.connect(pannerNode)
    pannerNode.connect(gainNode)
    gainNode.connect(categoryGain)
    
    // Generate unique ID
    const soundId = `sound_${this.soundIdCounter++}`
    
    // Track active sound
    this.activeSounds.set(soundId, {
      source,
      gainNode,
      pannerNode,
      type: cached.type,
      startTime: this.audioContext.currentTime,
    })
    
    // Clean up when sound ends
    source.onended = () => {
      this.activeSounds.delete(soundId)
    }
    
    // Start playback
    source.start()
    
    this.emit(AudioEvent.SOUND_PLAYED, { id, soundId, type: cached.type, position })
    
    return soundId
  }

  /**
   * Update position of a 3D sound
   * @param soundId - Sound instance ID
   * @param position - New position
   */
  updateSoundPosition(soundId: string, position: Vector3): void {
    const sound = this.activeSounds.get(soundId)
    if (sound?.pannerNode) {
      sound.pannerNode.setPosition(position.x, position.y, position.z)
    }
  }

  /**
   * Stop a specific sound
   * @param soundId - Sound instance ID
   */
  stopSound(soundId: string): void {
    const sound = this.activeSounds.get(soundId)
    if (sound) {
      try {
        sound.source.stop()
      } catch {
        // Sound may have already ended
      }
      this.activeSounds.delete(soundId)
    }
  }

  /**
   * Stop all sounds of a specific type
   */
  stopAllSounds(type?: SoundType): void {
    this.activeSounds.forEach((sound, id) => {
      if (!type || sound.type === type) {
        try {
          sound.source.stop()
        } catch {
          // Sound may have already ended
        }
        this.activeSounds.delete(id)
      }
    })
  }

  /**
   * Get the appropriate gain node for a sound type
   */
  private getCategoryGain(type: SoundType): GainNode {
    switch (type) {
      case SoundType.MUSIC:
        return this.musicGain!
      case SoundType.AMBIENT:
        return this.ambientGain!
      case SoundType.SFX:
      case SoundType.UI:
      default:
        return this.sfxGain!
    }
  }


  // ==================== Music System ====================

  /**
   * Play background music with optional crossfade
   * Requirements: 10.3, 10.4
   * @param track - Music track identifier
   * @param crossfade - Whether to crossfade from current track
   */
  async playMusic(track: MusicTrack, crossfade: boolean = true): Promise<void> {
    if (!this.audioContext || !this.musicGain) return
    
    const cached = this.soundCache.get(track)
    if (!cached) {
      console.warn(`Music track not loaded: ${track}`)
      return
    }
    
    // If same track is already playing, do nothing
    if (this.currentMusicTrack === track && this.currentMusicSource) return
    
    if (crossfade && this.currentMusicSource && !this.isCrossfading) {
      await this.crossfadeToTrack(track, cached.buffer)
    } else {
      this.playMusicImmediate(track, cached.buffer)
    }
    
    this.currentMusicTrack = track
    this.emit(AudioEvent.MUSIC_CHANGED, { track })
  }

  /**
   * Play music immediately without crossfade
   */
  private playMusicImmediate(track: MusicTrack, buffer: AudioBuffer): void {
    if (!this.audioContext || !this.musicGain) return
    
    // Stop current music
    this.stopMusic()
    
    // Create new source
    this.currentMusicSource = this.audioContext.createBufferSource()
    this.currentMusicSource.buffer = buffer
    this.currentMusicSource.loop = true
    
    // Create gain for this track
    this.currentMusicGain = this.audioContext.createGain()
    this.currentMusicGain.gain.value = 1.0
    
    // Connect
    this.currentMusicSource.connect(this.currentMusicGain)
    this.currentMusicGain.connect(this.musicGain)
    
    // Start
    this.currentMusicSource.start()
    this.currentMusicTrack = track
  }

  /**
   * Crossfade to a new music track
   * Requirements: 10.4
   */
  private async crossfadeToTrack(track: MusicTrack, buffer: AudioBuffer): Promise<void> {
    if (!this.audioContext || !this.musicGain) return
    
    this.isCrossfading = true
    
    // Create new source
    this.nextMusicSource = this.audioContext.createBufferSource()
    this.nextMusicSource.buffer = buffer
    this.nextMusicSource.loop = true
    
    // Create gain for new track (start at 0)
    this.nextMusicGain = this.audioContext.createGain()
    this.nextMusicGain.gain.value = 0
    
    // Connect
    this.nextMusicSource.connect(this.nextMusicGain)
    this.nextMusicGain.connect(this.musicGain)
    
    // Start new track
    this.nextMusicSource.start()
    
    // Crossfade
    const duration = AudioConfig.CROSSFADE_DURATION
    const currentTime = this.audioContext.currentTime
    
    // Fade out current
    if (this.currentMusicGain) {
      this.currentMusicGain.gain.linearRampToValueAtTime(0, currentTime + duration)
    }
    
    // Fade in new
    this.nextMusicGain.gain.linearRampToValueAtTime(1, currentTime + duration)
    
    // Wait for crossfade to complete
    await new Promise(resolve => setTimeout(resolve, duration * 1000))
    
    // Stop old track
    if (this.currentMusicSource) {
      try {
        this.currentMusicSource.stop()
      } catch {
        // May have already stopped
      }
    }
    
    // Swap references
    this.currentMusicSource = this.nextMusicSource
    this.currentMusicGain = this.nextMusicGain
    this.nextMusicSource = null
    this.nextMusicGain = null
    this.currentMusicTrack = track
    
    this.isCrossfading = false
  }

  /**
   * Stop current music
   */
  stopMusic(): void {
    if (this.currentMusicSource) {
      try {
        this.currentMusicSource.stop()
      } catch {
        // May have already stopped
      }
      this.currentMusicSource = null
    }
    this.currentMusicGain = null
    this.currentMusicTrack = null
  }

  /**
   * Get current music track
   */
  getCurrentMusicTrack(): MusicTrack | null {
    return this.currentMusicTrack
  }

  // ==================== Volume Control ====================

  /**
   * Set master volume
   */
  setMasterVolume(volume: number): void {
    this._masterVolume = Math.max(0, Math.min(1, volume))
    if (this.masterGain) {
      this.masterGain.gain.value = this._masterVolume
    }
    this.emit(AudioEvent.VOLUME_CHANGED, { type: 'master', volume: this._masterVolume })
  }

  /**
   * Set music volume
   */
  setMusicVolume(volume: number): void {
    this._musicVolume = Math.max(0, Math.min(1, volume))
    if (this.musicGain) {
      this.musicGain.gain.value = this._musicVolume
    }
    this.emit(AudioEvent.VOLUME_CHANGED, { type: 'music', volume: this._musicVolume })
  }

  /**
   * Set SFX volume
   */
  setSfxVolume(volume: number): void {
    this._sfxVolume = Math.max(0, Math.min(1, volume))
    if (this.sfxGain) {
      this.sfxGain.gain.value = this._sfxVolume
    }
    this.emit(AudioEvent.VOLUME_CHANGED, { type: 'sfx', volume: this._sfxVolume })
  }

  /**
   * Set ambient volume
   */
  setAmbientVolume(volume: number): void {
    this._ambientVolume = Math.max(0, Math.min(1, volume))
    if (this.ambientGain) {
      this.ambientGain.gain.value = this._ambientVolume
    }
    this.emit(AudioEvent.VOLUME_CHANGED, { type: 'ambient', volume: this._ambientVolume })
  }

  // Volume getters
  get masterVolume(): number { return this._masterVolume }
  get musicVolume(): number { return this._musicVolume }
  get sfxVolume(): number { return this._sfxVolume }
  get ambientVolume(): number { return this._ambientVolume }


  // ==================== Pause Handling ====================

  /**
   * Pause audio - reduces all volume by 50%
   * Requirements: 10.5
   */
  pause(): void {
    if (this._isPaused) return
    
    this._isPaused = true
    
    // Store current volumes
    this.prePauseVolumes = {
      master: this._masterVolume,
      music: this._musicVolume,
      sfx: this._sfxVolume,
      ambient: this._ambientVolume,
    }
    
    // Reduce all volumes by 50%
    const multiplier = AudioConfig.PAUSE_VOLUME_MULTIPLIER
    
    if (this.masterGain) {
      this.masterGain.gain.value = this._masterVolume * multiplier
    }
  }

  /**
   * Resume audio - restores original volume
   * Requirements: 10.5
   */
  resume(): void {
    if (!this._isPaused) return
    
    this._isPaused = false
    
    // Restore volumes
    if (this.prePauseVolumes) {
      if (this.masterGain) {
        this.masterGain.gain.value = this.prePauseVolumes.master
      }
      this.prePauseVolumes = null
    }
  }

  /**
   * Check if audio is paused
   */
  get isPaused(): boolean {
    return this._isPaused
  }

  // ==================== Listener Position ====================

  /**
   * Update listener position (call each frame)
   * The listener position is automatically updated if attached to camera
   * This method is for manual position updates if needed
   */
  updateListenerPosition(position: Vector3, forward: Vector3, up: Vector3 = { x: 0, y: 1, z: 0 }): void {
    if (!this.audioContext) return
    
    const listener = this.audioContext.listener
    
    if (listener.positionX) {
      // Modern API
      listener.positionX.value = position.x
      listener.positionY.value = position.y
      listener.positionZ.value = position.z
      listener.forwardX.value = forward.x
      listener.forwardY.value = forward.y
      listener.forwardZ.value = forward.z
      listener.upX.value = up.x
      listener.upY.value = up.y
      listener.upZ.value = up.z
    } else {
      // Legacy API
      listener.setPosition(position.x, position.y, position.z)
      listener.setOrientation(forward.x, forward.y, forward.z, up.x, up.y, up.z)
    }
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
   * Dispose of all audio resources
   */
  dispose(): void {
    // Stop all sounds
    this.stopAllSounds()
    this.stopMusic()
    
    // Clear cache
    this.soundCache.clear()
    this.loadingPromises.clear()
    this.activeSounds.clear()
    
    // Remove listener from camera
    if (this.listener && this.camera) {
      this.camera.remove(this.listener)
    }
    
    // Close audio context
    if (this.audioContext) {
      this.audioContext.close()
      this.audioContext = null
    }
    
    // Clear references
    this.listener = null
    this.camera = null
    this.masterGain = null
    this.musicGain = null
    this.sfxGain = null
    this.ambientGain = null
    
    // Clear event listeners
    this.eventListeners.clear()
  }

  /**
   * Check if audio context is initialized
   */
  isInitialized(): boolean {
    return this.audioContext !== null && this.audioContext.state !== 'closed'
  }

  /**
   * Get audio context state
   */
  getContextState(): AudioContextState | null {
    return this.audioContext?.state ?? null
  }
}
