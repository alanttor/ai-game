import * as THREE from 'three'
import type { EventCallback } from '../types'

/**
 * Time of day phases
 */
export enum TimeOfDay {
  DAWN = 'dawn',
  DAY = 'day',
  DUSK = 'dusk',
  NIGHT = 'night',
}

/**
 * Lighting environment type
 */
export enum LightingEnvironment {
  EXTERIOR = 'exterior',
  INTERIOR = 'interior',
}

/**
 * Lighting events
 */
export enum LightingEvent {
  TIME_CHANGED = 'lighting:timeChanged',
  ENVIRONMENT_CHANGED = 'lighting:environmentChanged',
  CYCLE_COMPLETE = 'lighting:cycleComplete',
}

/**
 * Time of day configuration
 */
interface TimeConfig {
  ambientColor: number
  ambientIntensity: number
  sunColor: number
  sunIntensity: number
  sunPosition: THREE.Vector3
  fogColor: number
  fogNear: number
  fogFar: number
  skyColor: number
}

/**
 * LightingManager - Handles dynamic lighting, day/night cycle, and shadows
 * Requirements: 5.2, 5.4
 */
export class LightingManager {
  private scene: THREE.Scene

  // Lights
  private ambientLight: THREE.AmbientLight
  private sunLight: THREE.DirectionalLight
  private hemisphereLight: THREE.HemisphereLight
  private interiorLights: THREE.PointLight[] = []

  // Day/night cycle
  private dayNightEnabled: boolean = false
  private cycleTime: number = 0 // 0-1, where 0.5 is noon
  private cycleDuration: number = 600 // seconds for full cycle (10 minutes)
  private currentTimeOfDay: TimeOfDay = TimeOfDay.DAY

  // Environment state
  private currentEnvironment: LightingEnvironment = LightingEnvironment.EXTERIOR
  private transitionProgress: number = 1 // 0-1 for smooth transitions
  private transitionSpeed: number = 2 // units per second

  // Event system
  private eventListeners: Map<string, Set<EventCallback>> = new Map()

  // Time configurations
  private timeConfigs: Map<TimeOfDay, TimeConfig> = new Map()


  constructor(scene: THREE.Scene) {
    this.scene = scene

    // Initialize lights
    this.ambientLight = new THREE.AmbientLight(0x404040, 0.5)
    this.sunLight = new THREE.DirectionalLight(0xffffff, 1)
    this.hemisphereLight = new THREE.HemisphereLight(0x87ceeb, 0x362d26, 0.3)

    this.initTimeConfigs()
    this.setupLights()
  }

  /**
   * Initialize time of day configurations
   */
  private initTimeConfigs(): void {
    // Dawn (6 AM)
    this.timeConfigs.set(TimeOfDay.DAWN, {
      ambientColor: 0x4a3c5c,
      ambientIntensity: 0.4,
      sunColor: 0xff8844,
      sunIntensity: 0.6,
      sunPosition: new THREE.Vector3(-80, 20, 0),
      fogColor: 0x5c4a6a,
      fogNear: 30,
      fogFar: 150,
      skyColor: 0x5c4a6a,
    })

    // Day (12 PM)
    this.timeConfigs.set(TimeOfDay.DAY, {
      ambientColor: 0x404050,
      ambientIntensity: 0.5,
      sunColor: 0xffffff,
      sunIntensity: 1.0,
      sunPosition: new THREE.Vector3(50, 100, 50),
      fogColor: 0x1a1a2e,
      fogNear: 50,
      fogFar: 200,
      skyColor: 0x1a1a2e,
    })

    // Dusk (6 PM)
    this.timeConfigs.set(TimeOfDay.DUSK, {
      ambientColor: 0x5c3c4a,
      ambientIntensity: 0.4,
      sunColor: 0xff6633,
      sunIntensity: 0.5,
      sunPosition: new THREE.Vector3(80, 15, 0),
      fogColor: 0x4a3c5c,
      fogNear: 25,
      fogFar: 120,
      skyColor: 0x4a3c5c,
    })

    // Night (12 AM)
    this.timeConfigs.set(TimeOfDay.NIGHT, {
      ambientColor: 0x101020,
      ambientIntensity: 0.2,
      sunColor: 0x8888ff,
      sunIntensity: 0.15,
      sunPosition: new THREE.Vector3(-50, 80, -50),
      fogColor: 0x0a0a15,
      fogNear: 20,
      fogFar: 100,
      skyColor: 0x0a0a15,
    })
  }

  /**
   * Setup lights in the scene
   */
  private setupLights(): void {
    // Add ambient light
    this.scene.add(this.ambientLight)

    // Configure sun/directional light with shadows
    this.sunLight.castShadow = true
    this.sunLight.shadow.mapSize.width = 2048
    this.sunLight.shadow.mapSize.height = 2048
    this.sunLight.shadow.camera.near = 0.5
    this.sunLight.shadow.camera.far = 500
    this.sunLight.shadow.camera.left = -100
    this.sunLight.shadow.camera.right = 100
    this.sunLight.shadow.camera.top = 100
    this.sunLight.shadow.camera.bottom = -100
    this.sunLight.shadow.bias = -0.0001
    this.sunLight.shadow.normalBias = 0.02
    this.scene.add(this.sunLight)

    // Add hemisphere light for ambient sky/ground color
    this.scene.add(this.hemisphereLight)

    // Apply default day configuration
    this.applyTimeConfig(TimeOfDay.DAY)
  }

  /**
   * Apply a time of day configuration
   */
  private applyTimeConfig(timeOfDay: TimeOfDay): void {
    const config = this.timeConfigs.get(timeOfDay)
    if (!config) return

    this.ambientLight.color.setHex(config.ambientColor)
    this.ambientLight.intensity = config.ambientIntensity

    this.sunLight.color.setHex(config.sunColor)
    this.sunLight.intensity = config.sunIntensity
    this.sunLight.position.copy(config.sunPosition)

    // Update fog
    this.scene.fog = new THREE.Fog(config.fogColor, config.fogNear, config.fogFar)
    if (this.scene.background instanceof THREE.Color) {
      this.scene.background.setHex(config.skyColor)
    } else {
      this.scene.background = new THREE.Color(config.skyColor)
    }

    this.currentTimeOfDay = timeOfDay
    this.emit(LightingEvent.TIME_CHANGED, { timeOfDay })
  }

  /**
   * Interpolate between two time configurations
   */
  private interpolateTimeConfigs(from: TimeOfDay, to: TimeOfDay, t: number): void {
    const fromConfig = this.timeConfigs.get(from)
    const toConfig = this.timeConfigs.get(to)
    if (!fromConfig || !toConfig) return

    // Interpolate colors
    const ambientColor = new THREE.Color(fromConfig.ambientColor).lerp(
      new THREE.Color(toConfig.ambientColor), t
    )
    const sunColor = new THREE.Color(fromConfig.sunColor).lerp(
      new THREE.Color(toConfig.sunColor), t
    )
    const fogColor = new THREE.Color(fromConfig.fogColor).lerp(
      new THREE.Color(toConfig.fogColor), t
    )
    const skyColor = new THREE.Color(fromConfig.skyColor).lerp(
      new THREE.Color(toConfig.skyColor), t
    )

    // Interpolate values
    const ambientIntensity = THREE.MathUtils.lerp(fromConfig.ambientIntensity, toConfig.ambientIntensity, t)
    const sunIntensity = THREE.MathUtils.lerp(fromConfig.sunIntensity, toConfig.sunIntensity, t)
    const fogNear = THREE.MathUtils.lerp(fromConfig.fogNear, toConfig.fogNear, t)
    const fogFar = THREE.MathUtils.lerp(fromConfig.fogFar, toConfig.fogFar, t)

    // Interpolate sun position
    const sunPosition = new THREE.Vector3().lerpVectors(fromConfig.sunPosition, toConfig.sunPosition, t)

    // Apply interpolated values
    this.ambientLight.color.copy(ambientColor)
    this.ambientLight.intensity = ambientIntensity
    this.sunLight.color.copy(sunColor)
    this.sunLight.intensity = sunIntensity
    this.sunLight.position.copy(sunPosition)
    this.scene.fog = new THREE.Fog(fogColor.getHex(), fogNear, fogFar)
    
    if (this.scene.background instanceof THREE.Color) {
      this.scene.background.copy(skyColor)
    } else {
      this.scene.background = skyColor
    }
  }


  /**
   * Update the lighting system
   * @param deltaTime Time since last update in seconds
   */
  update(deltaTime: number): void {
    // Update day/night cycle if enabled
    if (this.dayNightEnabled) {
      this.updateDayNightCycle(deltaTime)
    }

    // Update environment transition
    if (this.transitionProgress < 1) {
      this.transitionProgress = Math.min(1, this.transitionProgress + deltaTime * this.transitionSpeed)
      this.updateEnvironmentTransition()
    }
  }

  /**
   * Update day/night cycle
   */
  private updateDayNightCycle(deltaTime: number): void {
    const previousTime = this.cycleTime
    this.cycleTime = (this.cycleTime + deltaTime / this.cycleDuration) % 1

    // Determine current and next time of day
    const timePhases: { start: number; end: number; phase: TimeOfDay }[] = [
      { start: 0, end: 0.2, phase: TimeOfDay.NIGHT },
      { start: 0.2, end: 0.3, phase: TimeOfDay.DAWN },
      { start: 0.3, end: 0.7, phase: TimeOfDay.DAY },
      { start: 0.7, end: 0.8, phase: TimeOfDay.DUSK },
      { start: 0.8, end: 1, phase: TimeOfDay.NIGHT },
    ]

    let currentPhase: TimeOfDay = TimeOfDay.DAY
    let nextPhase: TimeOfDay = TimeOfDay.DAY
    let phaseProgress = 0

    for (let i = 0; i < timePhases.length; i++) {
      const phase = timePhases[i]
      if (this.cycleTime >= phase.start && this.cycleTime < phase.end) {
        currentPhase = phase.phase
        nextPhase = timePhases[(i + 1) % timePhases.length].phase
        phaseProgress = (this.cycleTime - phase.start) / (phase.end - phase.start)
        break
      }
    }

    // Interpolate between phases
    this.interpolateTimeConfigs(currentPhase, nextPhase, phaseProgress)

    // Check for phase change
    if (currentPhase !== this.currentTimeOfDay) {
      this.currentTimeOfDay = currentPhase
      this.emit(LightingEvent.TIME_CHANGED, { timeOfDay: currentPhase })
    }

    // Check for cycle completion
    if (previousTime > this.cycleTime) {
      this.emit(LightingEvent.CYCLE_COMPLETE, {})
    }
  }

  /**
   * Set the environment (interior/exterior)
   */
  setEnvironment(environment: LightingEnvironment): void {
    if (environment === this.currentEnvironment) return

    this.currentEnvironment = environment
    this.transitionProgress = 0
    this.emit(LightingEvent.ENVIRONMENT_CHANGED, { environment })
  }

  /**
   * Update environment transition (interior/exterior)
   */
  private updateEnvironmentTransition(): void {
    const t = this.transitionProgress

    if (this.currentEnvironment === LightingEnvironment.INTERIOR) {
      // Transition to interior lighting
      this.sunLight.intensity = THREE.MathUtils.lerp(
        this.sunLight.intensity,
        0.1,
        t
      )
      this.ambientLight.intensity = THREE.MathUtils.lerp(
        this.ambientLight.intensity,
        0.8,
        t
      )

      // Darken fog for interior
      if (this.scene.fog instanceof THREE.Fog) {
        this.scene.fog.near = THREE.MathUtils.lerp(this.scene.fog.near, 5, t)
        this.scene.fog.far = THREE.MathUtils.lerp(this.scene.fog.far, 50, t)
      }
    } else {
      // Restore exterior lighting based on current time
      const config = this.timeConfigs.get(this.currentTimeOfDay)
      if (config) {
        this.sunLight.intensity = THREE.MathUtils.lerp(
          this.sunLight.intensity,
          config.sunIntensity,
          t
        )
        this.ambientLight.intensity = THREE.MathUtils.lerp(
          this.ambientLight.intensity,
          config.ambientIntensity,
          t
        )

        if (this.scene.fog instanceof THREE.Fog) {
          this.scene.fog.near = THREE.MathUtils.lerp(this.scene.fog.near, config.fogNear, t)
          this.scene.fog.far = THREE.MathUtils.lerp(this.scene.fog.far, config.fogFar, t)
        }
      }
    }
  }

  /**
   * Check if a position is inside a building (for automatic environment switching)
   */
  checkEnvironment(position: THREE.Vector3, scene: THREE.Scene): LightingEnvironment {
    // Cast ray upward to check for ceiling
    const raycaster = new THREE.Raycaster(position, new THREE.Vector3(0, 1, 0))
    const intersects = raycaster.intersectObjects(scene.children, true)

    // If there's something above within 10 units with 'ceiling' in name, it's interior
    const isInterior = intersects.some(
      hit => hit.distance < 10 && hit.object.name.toLowerCase().includes('ceiling')
    )

    return isInterior ? LightingEnvironment.INTERIOR : LightingEnvironment.EXTERIOR
  }

  /**
   * Update lighting based on player position
   */
  updateForPosition(position: THREE.Vector3): void {
    const environment = this.checkEnvironment(position, this.scene)
    this.setEnvironment(environment)
  }

  /**
   * Add an interior point light
   */
  addInteriorLight(position: THREE.Vector3, color: number = 0xffaa55, intensity: number = 0.5, distance: number = 10): THREE.PointLight {
    const light = new THREE.PointLight(color, intensity, distance)
    light.position.copy(position)
    // Disable shadows on point lights to avoid exceeding MAX_TEXTURE_IMAGE_UNITS
    light.castShadow = false
    this.scene.add(light)
    this.interiorLights.push(light)
    return light
  }

  /**
   * Remove an interior light
   */
  removeInteriorLight(light: THREE.PointLight): void {
    const index = this.interiorLights.indexOf(light)
    if (index !== -1) {
      this.scene.remove(light)
      this.interiorLights.splice(index, 1)
    }
  }


  // ==================== Day/Night Cycle Controls ====================

  /**
   * Enable or disable day/night cycle
   */
  setDayNightCycleEnabled(enabled: boolean): void {
    this.dayNightEnabled = enabled
  }

  /**
   * Check if day/night cycle is enabled
   */
  isDayNightCycleEnabled(): boolean {
    return this.dayNightEnabled
  }

  /**
   * Set the cycle duration in seconds
   */
  setCycleDuration(seconds: number): void {
    this.cycleDuration = Math.max(60, seconds) // Minimum 1 minute
  }

  /**
   * Get the cycle duration
   */
  getCycleDuration(): number {
    return this.cycleDuration
  }

  /**
   * Set the current time (0-1, where 0.5 is noon)
   */
  setTime(time: number): void {
    this.cycleTime = Math.max(0, Math.min(1, time))
    
    // Immediately update lighting
    if (!this.dayNightEnabled) {
      // Determine time of day from time value
      if (time < 0.2 || time >= 0.8) {
        this.applyTimeConfig(TimeOfDay.NIGHT)
      } else if (time < 0.3) {
        this.applyTimeConfig(TimeOfDay.DAWN)
      } else if (time < 0.7) {
        this.applyTimeConfig(TimeOfDay.DAY)
      } else {
        this.applyTimeConfig(TimeOfDay.DUSK)
      }
    }
  }

  /**
   * Get the current time (0-1)
   */
  getTime(): number {
    return this.cycleTime
  }

  /**
   * Set time of day directly
   */
  setTimeOfDay(timeOfDay: TimeOfDay): void {
    this.applyTimeConfig(timeOfDay)
    
    // Set cycle time to match
    switch (timeOfDay) {
      case TimeOfDay.NIGHT:
        this.cycleTime = 0
        break
      case TimeOfDay.DAWN:
        this.cycleTime = 0.25
        break
      case TimeOfDay.DAY:
        this.cycleTime = 0.5
        break
      case TimeOfDay.DUSK:
        this.cycleTime = 0.75
        break
    }
  }

  /**
   * Get current time of day
   */
  getTimeOfDay(): TimeOfDay {
    return this.currentTimeOfDay
  }

  /**
   * Get current environment
   */
  getEnvironment(): LightingEnvironment {
    return this.currentEnvironment
  }

  // ==================== Shadow Controls ====================

  /**
   * Enable or disable shadows
   */
  setShadowsEnabled(enabled: boolean): void {
    this.sunLight.castShadow = enabled
    this.interiorLights.forEach(light => {
      light.castShadow = enabled
    })
  }

  /**
   * Set shadow quality
   */
  setShadowQuality(quality: 'low' | 'medium' | 'high' | 'ultra'): void {
    const sizes: Record<string, number> = {
      low: 512,
      medium: 1024,
      high: 2048,
      ultra: 4096,
    }

    const size = sizes[quality] || 1024
    this.sunLight.shadow.mapSize.width = size
    this.sunLight.shadow.mapSize.height = size
    this.sunLight.shadow.map?.dispose()
    this.sunLight.shadow.map = null as unknown as THREE.WebGLRenderTarget
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
      listeners.forEach(callback => callback(data))
    }
  }

  // ==================== Getters ====================

  getAmbientLight(): THREE.AmbientLight {
    return this.ambientLight
  }

  getSunLight(): THREE.DirectionalLight {
    return this.sunLight
  }

  getHemisphereLight(): THREE.HemisphereLight {
    return this.hemisphereLight
  }

  // ==================== Cleanup ====================

  dispose(): void {
    // Remove lights from scene
    this.scene.remove(this.ambientLight)
    this.scene.remove(this.sunLight)
    this.scene.remove(this.hemisphereLight)

    // Remove interior lights
    this.interiorLights.forEach(light => {
      this.scene.remove(light)
    })
    this.interiorLights = []

    // Dispose shadow maps
    this.sunLight.shadow.map?.dispose()

    // Clear event listeners
    this.eventListeners.clear()
  }
}
