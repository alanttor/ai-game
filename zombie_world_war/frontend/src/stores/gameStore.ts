import { defineStore } from 'pinia'
import type { GameState } from '../engine/types'
import { GameStateSerializer } from '../engine/serialization/GameStateSerializer'

/**
 * Save summary returned from backend
 */
export interface SaveSummary {
  id: number
  waveReached: number
  score: number
  savedAt: string
}

/**
 * Save response from backend
 */
export interface SaveResponse {
  saveId: number
  success: boolean
  message: string
  savedAt: string
}

/**
 * Game store state interface
 * Requirements: 6.1, 6.2
 */
interface GameStoreState {
  gameState: GameState | null
  saves: SaveSummary[]
  currentSaveId: number | null
  isLoading: boolean
  isSaving: boolean
  error: string | null
  lastSaveTime: number | null
}

/**
 * Game Pinia Store
 * Manages game state, serialization, and save/load operations
 * Requirements: 6.1, 6.2
 */
export const useGameStore = defineStore('game', {
  state: (): GameStoreState => ({
    gameState: null,
    saves: [],
    currentSaveId: null,
    isLoading: false,
    isSaving: false,
    error: null,
    lastSaveTime: null,
  }),

  getters: {
    /**
     * Get current wave number
     */
    currentWave: (state): number => state.gameState?.wave.currentWave ?? 0,

    /**
     * Get player health
     */
    playerHealth: (state): number => state.gameState?.player.health ?? 0,

    /**
     * Get current score
     */
    score: (state): number => state.gameState?.score ?? 0,

    /**
     * Get play time in seconds
     */
    playTime: (state): number => state.gameState?.playTime ?? 0,

    /**
     * Check if game state exists
     */
    hasGameState: (state): boolean => state.gameState !== null,

    /**
     * Check if there are any saves
     */
    hasSaves: (state): boolean => state.saves.length > 0,

    /**
     * Get serialized game state as JSON string
     * Requirements: 6.1
     */
    serializedState: (state): string | null => {
      if (!state.gameState) return null
      return GameStateSerializer.serialize(state.gameState)
    },
  },

  actions: {
    /**
     * Set the current game state
     * Requirements: 6.1
     */
    setGameState(newState: GameState) {
      this.gameState = newState
      this.error = null
    },

    /**
     * Update game state from serialized JSON
     * Requirements: 6.2
     */
    setGameStateFromJson(json: string) {
      try {
        this.gameState = GameStateSerializer.deserialize(json)
        this.error = null
      } catch (e) {
        const errorMessage = e instanceof Error ? e.message : 'Failed to deserialize game state'
        this.error = errorMessage
        throw e
      }
    },

    /**
     * Clear the current game state
     */
    clearGameState() {
      this.gameState = null
      this.currentSaveId = null
    },

    /**
     * Set loading state
     */
    setLoading(loading: boolean) {
      this.isLoading = loading
    },

    /**
     * Set saving state
     */
    setSaving(saving: boolean) {
      this.isSaving = saving
    },

    /**
     * Set error message
     */
    setError(error: string | null) {
      this.error = error
    },

    /**
     * Set the list of saves
     */
    setSaves(saves: SaveSummary[]) {
      this.saves = saves
    },

    /**
     * Set current save ID after successful save/load
     */
    setCurrentSaveId(saveId: number | null) {
      this.currentSaveId = saveId
    },

    /**
     * Update last save time
     */
    updateLastSaveTime() {
      this.lastSaveTime = Date.now()
    },

    /**
     * Add a new save to the list
     */
    addSave(save: SaveSummary) {
      this.saves.unshift(save)
    },

    /**
     * Remove a save from the list
     */
    removeSave(saveId: number) {
      this.saves = this.saves.filter((s) => s.id !== saveId)
      if (this.currentSaveId === saveId) {
        this.currentSaveId = null
      }
    },

    /**
     * Clear all store data
     */
    clearAll() {
      this.gameState = null
      this.saves = []
      this.currentSaveId = null
      this.isLoading = false
      this.isSaving = false
      this.error = null
      this.lastSaveTime = null
    },
  },
})
