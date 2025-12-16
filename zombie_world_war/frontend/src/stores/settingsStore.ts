import { defineStore } from 'pinia'

/**
 * Game settings interface
 * Requirements: 1.2, 10.5
 */
export interface GameSettings {
  // Controls
  mouseSensitivity: number      // 1-100, default 50
  invertMouseY: boolean         // Invert vertical mouse movement
  
  // Audio
  masterVolume: number          // 0-100, default 80
  musicVolume: number           // 0-100, default 70
  sfxVolume: number             // 0-100, default 90
  ambientVolume: number         // 0-100, default 60
  
  // Graphics
  targetFPS: number             // 30, 60, or 120
  shadowQuality: 'low' | 'medium' | 'high'
  drawDistance: 'low' | 'medium' | 'high'
  
  // Gameplay
  showCrosshair: boolean
  showDamageNumbers: boolean
  screenShake: boolean
}

/**
 * Default settings
 */
export const DEFAULT_SETTINGS: GameSettings = {
  // Controls
  mouseSensitivity: 50,
  invertMouseY: false,
  
  // Audio
  masterVolume: 80,
  musicVolume: 70,
  sfxVolume: 90,
  ambientVolume: 60,
  
  // Graphics
  targetFPS: 60,
  shadowQuality: 'medium',
  drawDistance: 'medium',
  
  // Gameplay
  showCrosshair: true,
  showDamageNumbers: true,
  screenShake: true,
}


const SETTINGS_KEY = 'zww_settings'

/**
 * Settings Pinia Store
 * Manages game settings with localStorage persistence
 * Requirements: 1.2, 10.5
 */
export const useSettingsStore = defineStore('settings', {
  state: (): { settings: GameSettings } => ({
    settings: { ...DEFAULT_SETTINGS },
  }),

  getters: {
    /**
     * Get mouse sensitivity as a multiplier (0.02 - 2.0)
     */
    mouseSensitivityMultiplier: (state): number => {
      return state.settings.mouseSensitivity / 50
    },

    /**
     * Get master volume as a decimal (0.0 - 1.0)
     */
    masterVolumeDecimal: (state): number => {
      return state.settings.masterVolume / 100
    },

    /**
     * Get music volume as a decimal (0.0 - 1.0)
     */
    musicVolumeDecimal: (state): number => {
      return state.settings.musicVolume / 100
    },

    /**
     * Get SFX volume as a decimal (0.0 - 1.0)
     */
    sfxVolumeDecimal: (state): number => {
      return state.settings.sfxVolume / 100
    },

    /**
     * Get ambient volume as a decimal (0.0 - 1.0)
     */
    ambientVolumeDecimal: (state): number => {
      return state.settings.ambientVolume / 100
    },
  },

  actions: {
    /**
     * Initialize settings from localStorage
     */
    initSettings() {
      const stored = localStorage.getItem(SETTINGS_KEY)
      if (stored) {
        try {
          const parsed = JSON.parse(stored)
          this.settings = { ...DEFAULT_SETTINGS, ...parsed }
        } catch {
          // Use defaults if parsing fails
          this.settings = { ...DEFAULT_SETTINGS }
        }
      }
    },


    /**
     * Save settings to localStorage
     */
    saveSettings() {
      localStorage.setItem(SETTINGS_KEY, JSON.stringify(this.settings))
    },

    /**
     * Update a single setting
     */
    updateSetting<K extends keyof GameSettings>(key: K, value: GameSettings[K]) {
      this.settings[key] = value
      this.saveSettings()
    },

    /**
     * Update multiple settings at once
     */
    updateSettings(updates: Partial<GameSettings>) {
      this.settings = { ...this.settings, ...updates }
      this.saveSettings()
    },

    /**
     * Reset all settings to defaults
     */
    resetToDefaults() {
      this.settings = { ...DEFAULT_SETTINGS }
      this.saveSettings()
    },

    /**
     * Reset controls settings to defaults
     */
    resetControlsToDefaults() {
      this.settings.mouseSensitivity = DEFAULT_SETTINGS.mouseSensitivity
      this.settings.invertMouseY = DEFAULT_SETTINGS.invertMouseY
      this.saveSettings()
    },

    /**
     * Reset audio settings to defaults
     */
    resetAudioToDefaults() {
      this.settings.masterVolume = DEFAULT_SETTINGS.masterVolume
      this.settings.musicVolume = DEFAULT_SETTINGS.musicVolume
      this.settings.sfxVolume = DEFAULT_SETTINGS.sfxVolume
      this.settings.ambientVolume = DEFAULT_SETTINGS.ambientVolume
      this.saveSettings()
    },

    /**
     * Reset graphics settings to defaults
     */
    resetGraphicsToDefaults() {
      this.settings.targetFPS = DEFAULT_SETTINGS.targetFPS
      this.settings.shadowQuality = DEFAULT_SETTINGS.shadowQuality
      this.settings.drawDistance = DEFAULT_SETTINGS.drawDistance
      this.saveSettings()
    },
  },
})
