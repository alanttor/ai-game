package com.zombieworldwar.service;

import com.zombieworldwar.dto.GameStateDTO;
import com.zombieworldwar.dto.SaveResponse;
import com.zombieworldwar.dto.SaveSummaryDTO;

import java.util.List;

/**
 * Game service interface for save/load operations.
 * Requirements: 6.3, 11.1, 11.2
 */
public interface GameService {
    
    /**
     * Save the current game state for a user.
     * Requirements: 6.3, 11.1
     * 
     * @param gameState the game state to save
     * @param userId the authenticated user's ID
     * @return SaveResponse with save ID and status
     */
    SaveResponse saveGame(GameStateDTO gameState, Long userId);
    
    /**
     * Load a saved game state by ID for a user.
     * Requirements: 11.2
     * 
     * @param saveId the save ID to load
     * @param userId the authenticated user's ID
     * @return the saved GameStateDTO
     */
    GameStateDTO loadGame(Long saveId, Long userId);
    
    /**
     * List all saved games for a user.
     * Requirements: 11.2
     * 
     * @param userId the authenticated user's ID
     * @return list of save summaries
     */
    List<SaveSummaryDTO> listSaves(Long userId);
    
    /**
     * Delete a saved game by ID for a user.
     * Requirements: 8.5
     * 
     * @param saveId the save ID to delete
     * @param userId the authenticated user's ID
     */
    void deleteSave(Long saveId, Long userId);
}
