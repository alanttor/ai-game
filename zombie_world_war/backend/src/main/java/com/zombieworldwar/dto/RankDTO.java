package com.zombieworldwar.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * DTO for user rank information.
 * Requirements: 7.2
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class RankDTO {
    private Long userId;
    private String playerName;
    private Integer highestScore;
    private Long rank;
    private Integer waveReached;
}
