package com.zombieworldwar.service.impl;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.zombieworldwar.dto.GameStateDTO;
import com.zombieworldwar.dto.SaveResponse;
import com.zombieworldwar.dto.SaveSummaryDTO;
import com.zombieworldwar.entity.GameSave;
import com.zombieworldwar.entity.User;
import com.zombieworldwar.exception.ResourceNotFoundException;
import com.zombieworldwar.repository.GameSaveRepository;
import com.zombieworldwar.repository.UserRepository;
import com.zombieworldwar.service.GameService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

/**
 * Implementation of GameService for save/load operations.
 * Requirements: 6.3, 11.1, 11.2
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class GameServiceImpl implements GameService {
    
    private final GameSaveRepository gameSaveRepository;
    private final UserRepository userRepository;
    private final ObjectMapper objectMapper;
    
    @Override
    @Transactional
    public SaveResponse saveGame(GameStateDTO gameState, Long userId) {
        log.info("Saving game for user ID: {}", userId);
        
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new ResourceNotFoundException("User not found with ID: " + userId));
        
        try {
            String gameStateJson = objectMapper.writeValueAsString(gameState);
            
            GameSave gameSave = GameSave.builder()
                    .user(user)
                    .gameStateJson(gameStateJson)
                    .waveReached(gameState.getWave() != null ? gameState.getWave().getCurrentWave() : 1)
                    .score(gameState.getScore())
                    .build();
            
            GameSave savedGame = gameSaveRepository.save(gameSave);
            
            log.info("Game saved successfully with ID: {}", savedGame.getId());
            
            return SaveResponse.builder()
                    .saveId(savedGame.getId())
                    .success(true)
                    .message("Game saved successfully")
                    .savedAt(savedGame.getSavedAt())
                    .build();
                    
        } catch (JsonProcessingException e) {
            log.error("Failed to serialize game state", e);
            return SaveResponse.builder()
                    .success(false)
                    .message("Failed to save game: " + e.getMessage())
                    .build();
        }
    }

    
    @Override
    @Transactional(readOnly = true)
    public GameStateDTO loadGame(Long saveId, Long userId) {
        log.info("Loading game save ID: {} for user ID: {}", saveId, userId);
        
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new ResourceNotFoundException("User not found with ID: " + userId));
        
        GameSave gameSave = gameSaveRepository.findByIdAndUser(saveId, user)
                .orElseThrow(() -> new ResourceNotFoundException("Save not found with ID: " + saveId));
        
        try {
            GameStateDTO gameState = objectMapper.readValue(gameSave.getGameStateJson(), GameStateDTO.class);
            log.info("Game loaded successfully for save ID: {}", saveId);
            return gameState;
            
        } catch (JsonProcessingException e) {
            log.error("Failed to deserialize game state for save ID: {}", saveId, e);
            throw new RuntimeException("Failed to load game: " + e.getMessage(), e);
        }
    }
    
    @Override
    @Transactional(readOnly = true)
    public List<SaveSummaryDTO> listSaves(Long userId) {
        log.info("Listing saves for user ID: {}", userId);
        
        List<GameSave> saves = gameSaveRepository.findByUserId(userId);
        
        return saves.stream()
                .map(save -> SaveSummaryDTO.builder()
                        .id(save.getId())
                        .waveReached(save.getWaveReached())
                        .score(save.getScore())
                        .savedAt(save.getSavedAt())
                        .build())
                .collect(Collectors.toList());
    }
    
    @Override
    @Transactional
    public void deleteSave(Long saveId, Long userId) {
        log.info("Deleting save ID: {} for user ID: {}", saveId, userId);
        
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new ResourceNotFoundException("User not found with ID: " + userId));
        
        GameSave gameSave = gameSaveRepository.findByIdAndUser(saveId, user)
                .orElseThrow(() -> new ResourceNotFoundException("Save not found with ID: " + saveId));
        
        gameSaveRepository.delete(gameSave);
        log.info("Save deleted successfully for save ID: {}", saveId);
    }
}
