package com.zombieworldwar.service;

import com.zombieworldwar.dto.LeaderboardEntryDTO;
import com.zombieworldwar.dto.RankDTO;
import com.zombieworldwar.dto.ScoreResponse;
import com.zombieworldwar.dto.ScoreSubmitDTO;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

/**
 * Leaderboard service interface for score submission and ranking.
 * Requirements: 7.1, 7.2, 7.3, 11.3
 */
public interface LeaderboardService {
    
    /**
     * Submit a score to the leaderboard.
     * Requirements: 7.1
     * 
     * @param scoreSubmit the score submission data
     * @param userId the authenticated user's ID
     * @return ScoreResponse with rank and top 10 status
     */
    ScoreResponse submitScore(ScoreSubmitDTO scoreSubmit, Long userId);
    
    /**
     * Get top scores with pagination.
     * Requirements: 7.2, 11.3
     * 
     * @param pageable pagination parameters
     * @return Page of leaderboard entries sorted by score descending
     */
    Page<LeaderboardEntryDTO> getTopScores(Pageable pageable);
    
    /**
     * Get a user's rank and highest score.
     * Requirements: 7.2, 7.3
     * 
     * @param userId the user's ID
     * @return RankDTO with user's rank information
     */
    RankDTO getUserRank(Long userId);
}
