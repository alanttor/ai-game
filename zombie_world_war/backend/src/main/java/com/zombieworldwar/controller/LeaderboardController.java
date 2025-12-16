package com.zombieworldwar.controller;

import com.zombieworldwar.dto.LeaderboardEntryDTO;
import com.zombieworldwar.dto.RankDTO;
import com.zombieworldwar.dto.ScoreResponse;
import com.zombieworldwar.dto.ScoreSubmitDTO;
import com.zombieworldwar.security.JwtUserPrincipal;
import com.zombieworldwar.service.LeaderboardService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

/**
 * Leaderboard controller for score submission and ranking.
 * Requirements: 7.1, 7.2, 11.3
 */
@RestController
@RequestMapping("/api/leaderboard")
@RequiredArgsConstructor
@Slf4j
public class LeaderboardController {
    
    private final LeaderboardService leaderboardService;
    
    /**
     * Submit a score to the leaderboard.
     * POST /api/leaderboard/submit
     * Requirements: 7.1
     */
    @PostMapping("/submit")
    public ResponseEntity<ScoreResponse> submitScore(
            @Valid @RequestBody ScoreSubmitDTO scoreSubmit,
            @AuthenticationPrincipal JwtUserPrincipal principal) {
        
        log.info("Score submission request from user: {}", principal.getUsername());
        ScoreResponse response = leaderboardService.submitScore(scoreSubmit, principal.getUserId());
        return ResponseEntity.ok(response);
    }
    
    /**
     * Get top scores with pagination.
     * GET /api/leaderboard/top
     * Requirements: 7.2, 11.3
     */
    @GetMapping("/top")
    public ResponseEntity<Page<LeaderboardEntryDTO>> getTopScores(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        
        log.info("Get top scores request - page: {}, size: {}", page, size);
        
        // Limit page size to prevent excessive queries
        int limitedSize = Math.min(size, 100);
        Pageable pageable = PageRequest.of(page, limitedSize);
        
        Page<LeaderboardEntryDTO> scores = leaderboardService.getTopScores(pageable);
        return ResponseEntity.ok(scores);
    }
    
    /**
     * Get a user's rank and highest score.
     * GET /api/leaderboard/rank/{userId}
     * Requirements: 7.2
     */
    @GetMapping("/rank/{userId}")
    public ResponseEntity<RankDTO> getUserRank(@PathVariable Long userId) {
        log.info("Get rank request for user ID: {}", userId);
        RankDTO rank = leaderboardService.getUserRank(userId);
        return ResponseEntity.ok(rank);
    }
}
