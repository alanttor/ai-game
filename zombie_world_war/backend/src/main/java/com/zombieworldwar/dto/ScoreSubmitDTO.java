package com.zombieworldwar.dto;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * DTO for submitting scores to leaderboard.
 * Requirements: 7.1, 11.3
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ScoreSubmitDTO {
    @NotNull(message = "Score is required")
    @Min(value = 0, message = "Score must be non-negative")
    private Integer score;
    
    @NotNull(message = "Wave reached is required")
    @Min(value = 1, message = "Wave reached must be at least 1")
    private Integer waveReached;
    
    @NotNull(message = "Zombies killed is required")
    @Min(value = 0, message = "Zombies killed must be non-negative")
    private Integer zombiesKilled;
    
    @NotNull(message = "Play time is required")
    @Min(value = 0, message = "Play time must be non-negative")
    private Long playTimeSeconds;
}
