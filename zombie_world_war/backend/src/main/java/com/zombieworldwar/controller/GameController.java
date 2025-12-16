package com.zombieworldwar.controller;

import com.zombieworldwar.dto.GameStateDTO;
import com.zombieworldwar.dto.SaveResponse;
import com.zombieworldwar.dto.SaveSummaryDTO;
import com.zombieworldwar.security.JwtUserPrincipal;
import com.zombieworldwar.service.GameService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * Game controller for save/load operations.
 * Requirements: 11.1, 11.2
 */
@RestController
@RequestMapping("/api/game")
@RequiredArgsConstructor
@Slf4j
public class GameController {
    
    private final GameService gameService;
    
    /**
     * Save the current game state.
     * POST /api/game/save
     * Requirements: 11.1
     */
    @PostMapping("/save")
    public ResponseEntity<SaveResponse> saveGame(
            @RequestBody GameStateDTO gameState,
            @AuthenticationPrincipal JwtUserPrincipal principal) {
        
        log.info("Save game request from user: {}", principal.getUsername());
        SaveResponse response = gameService.saveGame(gameState, principal.getUserId());
        
        if (response.getSuccess()) {
            return ResponseEntity.ok(response);
        } else {
            return ResponseEntity.internalServerError().body(response);
        }
    }
    
    /**
     * Load a saved game state by ID.
     * GET /api/game/load/{id}
     * Requirements: 11.2
     */
    @GetMapping("/load/{id}")
    public ResponseEntity<GameStateDTO> loadGame(
            @PathVariable("id") Long saveId,
            @AuthenticationPrincipal JwtUserPrincipal principal) {
        
        log.info("Load game request for save ID: {} from user: {}", saveId, principal.getUsername());
        GameStateDTO gameState = gameService.loadGame(saveId, principal.getUserId());
        return ResponseEntity.ok(gameState);
    }
    
    /**
     * List all saved games for the authenticated user.
     * GET /api/game/saves
     * Requirements: 11.2
     */
    @GetMapping("/saves")
    public ResponseEntity<List<SaveSummaryDTO>> listSaves(
            @AuthenticationPrincipal JwtUserPrincipal principal) {
        
        log.info("List saves request from user: {}", principal.getUsername());
        List<SaveSummaryDTO> saves = gameService.listSaves(principal.getUserId());
        return ResponseEntity.ok(saves);
    }
    
    /**
     * Delete a saved game by ID.
     * DELETE /api/game/save/{id}
     * Requirements: 8.5
     */
    @DeleteMapping("/save/{id}")
    public ResponseEntity<Void> deleteSave(
            @PathVariable("id") Long saveId,
            @AuthenticationPrincipal JwtUserPrincipal principal) {
        
        log.info("Delete save request for save ID: {} from user: {}", saveId, principal.getUsername());
        gameService.deleteSave(saveId, principal.getUserId());
        return ResponseEntity.noContent().build();
    }
}
