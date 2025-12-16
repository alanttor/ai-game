import apiClient from './client'
import type { GameState } from '@engine/types'
import type { SaveSummary, SaveResponse } from '@/stores/gameStore'

/**
 * Game state DTO matching backend structure
 */
interface GameStateDTO {
  player: {
    position: { x: number; y: number; z: number }
    rotation: { x: number; y: number; z: number }
    health: number
    stamina: number
    weapons: Array<{
      id: string
      currentAmmo: number
      reserveAmmo: number
    }>
    currentWeaponIndex: number
  }
  wave: {
    currentWave: number
    zombiesKilled: number
    totalZombiesInWave: number
    isPreparationPhase: boolean
  }
  zombies: Array<{
    id: string
    position: { x: number; y: number; z: number }
    health: number
    variant: string
    state: string
  }>
  score: number
  playTime: number
  timestamp: number
}

/**
 * Convert frontend GameState to backend DTO format
 */
function toGameStateDTO(state: GameState): GameStateDTO {
  return {
    player: {
      position: { x: state.player.position.x, y: state.player.position.y, z: state.player.position.z },
      rotation: { x: state.player.rotation.x, y: state.player.rotation.y, z: state.player.rotation.z },
      health: state.player.health,
      stamina: state.player.stamina,
      weapons: state.player.weapons.map(w => ({
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
    zombies: state.zombies.map(z => ({
      id: z.id,
      position: { x: z.position.x, y: z.position.y, z: z.position.z },
      health: z.health,
      variant: z.variant,
      state: z.state,
    })),
    score: state.score,
    playTime: state.playTime,
    timestamp: state.timestamp,
  }
}

/**
 * Game API endpoints for save/load operations
 * Requirements: 6.3, 6.5, 11.1, 11.2
 */
export const gameApi = {
  /**
   * Save the current game state to backend
   * Requirements: 6.3, 11.1
   * 
   * @param gameState - The current game state to save
   * @returns SaveResponse with save ID and status
   * @throws Error if save operation fails (Requirement 6.5)
   */
  async saveGame(gameState: GameState): Promise<SaveResponse> {
    try {
      const dto = toGameStateDTO(gameState)
      const response = await apiClient.post<SaveResponse>('/game/save', dto)
      return response.data
    } catch (error) {
      // Requirement 6.5: Display error message and retain current game state
      const message = error instanceof Error ? error.message : 'Failed to save game'
      throw new Error(`Save failed: ${message}`)
    }
  },

  /**
   * Load a saved game state from backend
   * Requirements: 6.3, 11.2
   * 
   * @param saveId - The ID of the save to load
   * @returns The loaded GameState
   * @throws Error if load operation fails
   */
  async loadGame(saveId: number): Promise<GameState> {
    try {
      const response = await apiClient.get<GameStateDTO>(`/game/load/${saveId}`)
      const dto = response.data
      
      // Convert DTO back to GameState
      return {
        player: {
          position: dto.player.position,
          rotation: dto.player.rotation,
          health: dto.player.health,
          stamina: dto.player.stamina,
          weapons: dto.player.weapons,
          currentWeaponIndex: dto.player.currentWeaponIndex,
        },
        wave: dto.wave,
        zombies: dto.zombies.map(z => ({
          id: z.id,
          position: z.position,
          health: z.health,
          variant: z.variant as GameState['zombies'][0]['variant'],
          state: z.state as GameState['zombies'][0]['state'],
        })),
        score: dto.score,
        playTime: dto.playTime,
        timestamp: dto.timestamp,
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to load game'
      throw new Error(`Load failed: ${message}`)
    }
  },

  /**
   * List all saved games for the authenticated user
   * Requirements: 11.2
   * 
   * @returns Array of save summaries
   */
  async listSaves(): Promise<SaveSummary[]> {
    try {
      const response = await apiClient.get<SaveSummary[]>('/game/saves')
      return response.data
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to list saves'
      throw new Error(`List saves failed: ${message}`)
    }
  },

  /**
   * Delete a saved game
   * Requirements: 8.5
   * 
   * @param saveId - The ID of the save to delete
   */
  async deleteSave(saveId: number): Promise<void> {
    try {
      await apiClient.delete(`/game/save/${saveId}`)
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to delete save'
      throw new Error(`Delete save failed: ${message}`)
    }
  },
}

export default gameApi
