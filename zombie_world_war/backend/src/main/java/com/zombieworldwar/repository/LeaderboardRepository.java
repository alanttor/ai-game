package com.zombieworldwar.repository;

import com.zombieworldwar.entity.LeaderboardEntry;
import com.zombieworldwar.entity.User;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * Repository for LeaderboardEntry entity operations.
 * Requirements: 7.1, 7.2, 7.3, 11.3
 */
@Repository
public interface LeaderboardRepository extends JpaRepository<LeaderboardEntry, Long> {
    
    /**
     * Get all leaderboard entries sorted by score descending with pagination.
     * Requirements: 7.2, 11.3
     */
    Page<LeaderboardEntry> findAllByOrderByScoreDesc(Pageable pageable);
    
    /**
     * Get top N entries by score.
     * Requirements: 7.2, 7.3
     */
    List<LeaderboardEntry> findTop10ByOrderByScoreDesc();
    
    /**
     * Get user's highest score entry.
     * Requirements: 7.2
     */
    Optional<LeaderboardEntry> findTopByUserOrderByScoreDesc(User user);
    
    /**
     * Calculate rank for a given score.
     * Requirements: 7.2
     */
    @Query("SELECT COUNT(l) + 1 FROM LeaderboardEntry l WHERE l.score > :score")
    Long findRankByScore(@Param("score") Integer score);
    
    /**
     * Count entries with higher score (for rank calculation).
     * Requirements: 7.3
     */
    @Query("SELECT COUNT(l) FROM LeaderboardEntry l WHERE l.score > :score")
    Long countEntriesWithHigherScore(@Param("score") Integer score);
    
    /**
     * Find all entries for a specific user.
     * Requirements: 7.2
     */
    List<LeaderboardEntry> findByUserOrderByScoreDesc(User user);
    
    /**
     * Find entries by user ID.
     * Requirements: 7.2
     */
    @Query("SELECT l FROM LeaderboardEntry l WHERE l.user.id = :userId ORDER BY l.score DESC")
    List<LeaderboardEntry> findByUserId(@Param("userId") Long userId);
}
