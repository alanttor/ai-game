package com.zombieworldwar.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * Leaderboard entry data transfer object.
 * Requirements: 7.2, 11.3
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class LeaderboardEntryDTO {
    private Long id;
    private Long userId;
    private String playerName;
    private Integer score;
    private Integer waveReached;
    private Integer zombiesKilled;
    private Long playTimeSeconds;
    private LocalDateTime achievedAt;
    private Long rank;
}
