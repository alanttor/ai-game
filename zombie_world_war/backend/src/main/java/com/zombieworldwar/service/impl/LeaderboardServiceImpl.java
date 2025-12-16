package com.zombieworldwar.service.impl;

import com.zombieworldwar.dto.LeaderboardEntryDTO;
import com.zombieworldwar.dto.RankDTO;
import com.zombieworldwar.dto.ScoreResponse;
import com.zombieworldwar.dto.ScoreSubmitDTO;
import com.zombieworldwar.entity.LeaderboardEntry;
import com.zombieworldwar.entity.User;
import com.zombieworldwar.exception.ResourceNotFoundException;
import com.zombieworldwar.repository.LeaderboardRepository;
import com.zombieworldwar.repository.UserRepository;
import com.zombieworldwar.service.LeaderboardService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

/**
 * Implementation of LeaderboardService for score submission and ranking.
 * Requirements: 7.1, 7.2, 7.3, 11.3
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class LeaderboardServiceImpl implements LeaderboardService {
    
    private final LeaderboardRepository leaderboardRepository;
    private final UserRepository userRepository;
    
    private static final int TOP_TEN_THRESHOLD = 10;

    /**
     * Submit a score to the leaderboard.
     * Requirements: 7.1
     */
    @Override
    @Transactional
    public ScoreResponse submitScore(ScoreSubmitDTO scoreSubmit, Long userId) {
        log.info("Submitting score {} for user ID: {}", scoreSubmit.getScore(), userId);
        
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new ResourceNotFoundException("User not found with ID: " + userId));
        
        LeaderboardEntry entry = LeaderboardEntry.builder()
                .user(user)
                .score(scoreSubmit.getScore())
                .waveReached(scoreSubmit.getWaveReached())
                .zombiesKilled(scoreSubmit.getZombiesKilled())
                .playTimeSeconds(scoreSubmit.getPlayTimeSeconds())
                .build();
        
        LeaderboardEntry savedEntry = leaderboardRepository.save(entry);
        
        // Calculate rank for this score
        Long rank = leaderboardRepository.findRankByScore(savedEntry.getScore());
        boolean isTopTen = rank <= TOP_TEN_THRESHOLD;
        
        log.info("Score submitted successfully. Entry ID: {}, Rank: {}, Top 10: {}", 
                savedEntry.getId(), rank, isTopTen);
        
        String message = isTopTen 
                ? "Congratulations! You achieved a top 10 score!" 
                : "Score submitted successfully";
        
        return ScoreResponse.builder()
                .entryId(savedEntry.getId())
                .success(true)
                .rank(rank)
                .isTopTen(isTopTen)
                .message(message)
                .build();
    }
    
    /**
     * Get top scores with pagination.
     * Requirements: 7.2, 11.3
     */
    @Override
    @Transactional(readOnly = true)
    public Page<LeaderboardEntryDTO> getTopScores(Pageable pageable) {
        log.info("Getting top scores with page: {}, size: {}", 
                pageable.getPageNumber(), pageable.getPageSize());
        
        Page<LeaderboardEntry> entries = leaderboardRepository.findAllByOrderByScoreDesc(pageable);
        
        return entries.map(this::toDTO);
    }
    
    /**
     * Get a user's rank and highest score.
     * Requirements: 7.2, 7.3
     */
    @Override
    @Transactional(readOnly = true)
    public RankDTO getUserRank(Long userId) {
        log.info("Getting rank for user ID: {}", userId);
        
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new ResourceNotFoundException("User not found with ID: " + userId));
        
        Optional<LeaderboardEntry> highestEntry = leaderboardRepository.findTopByUserOrderByScoreDesc(user);
        
        if (highestEntry.isEmpty()) {
            log.info("No leaderboard entries found for user ID: {}", userId);
            return RankDTO.builder()
                    .userId(userId)
                    .playerName(user.getUsername())
                    .highestScore(0)
                    .rank(null)
                    .waveReached(0)
                    .build();
        }
        
        LeaderboardEntry entry = highestEntry.get();
        Long rank = leaderboardRepository.findRankByScore(entry.getScore());
        
        log.info("User {} has rank {} with score {}", user.getUsername(), rank, entry.getScore());
        
        return RankDTO.builder()
                .userId(userId)
                .playerName(user.getUsername())
                .highestScore(entry.getScore())
                .rank(rank)
                .waveReached(entry.getWaveReached())
                .build();
    }
    
    /**
     * Convert LeaderboardEntry entity to DTO.
     */
    private LeaderboardEntryDTO toDTO(LeaderboardEntry entry) {
        Long rank = leaderboardRepository.findRankByScore(entry.getScore());
        
        return LeaderboardEntryDTO.builder()
                .id(entry.getId())
                .userId(entry.getUser().getId())
                .playerName(entry.getUser().getUsername())
                .score(entry.getScore())
                .waveReached(entry.getWaveReached())
                .zombiesKilled(entry.getZombiesKilled())
                .playTimeSeconds(entry.getPlayTimeSeconds())
                .achievedAt(entry.getAchievedAt())
                .rank(rank)
                .build();
    }
}
