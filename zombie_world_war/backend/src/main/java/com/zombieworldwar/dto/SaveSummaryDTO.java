package com.zombieworldwar.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * Summary DTO for listing saved games.
 * Requirements: 11.2
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class SaveSummaryDTO {
    private Long id;
    private Integer waveReached;
    private Integer score;
    private LocalDateTime savedAt;
}
