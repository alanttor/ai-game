package com.zombieworldwar.repository;

import com.zombieworldwar.entity.GameSave;
import com.zombieworldwar.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * Repository for GameSave entity operations.
 * Requirements: 6.3, 11.1, 11.2
 */
@Repository
public interface GameSaveRepository extends JpaRepository<GameSave, Long> {
    
    /**
     * Find all saves for a user, ordered by most recent first.
     * Requirements: 11.2
     */
    List<GameSave> findByUserOrderBySavedAtDesc(User user);
    
    /**
     * Find a specific save by ID and user (for security).
     * Requirements: 8.5, 11.2
     */
    Optional<GameSave> findByIdAndUser(Long id, User user);
    
    /**
     * Delete a save by ID and user (for security).
     * Requirements: 8.5
     */
    void deleteByIdAndUser(Long id, User user);
    
    /**
     * Count saves for a user.
     */
    long countByUser(User user);
    
    /**
     * Find saves by user ID.
     * Requirements: 11.2
     */
    @Query("SELECT g FROM GameSave g WHERE g.user.id = :userId ORDER BY g.savedAt DESC")
    List<GameSave> findByUserId(@Param("userId") Long userId);
}
