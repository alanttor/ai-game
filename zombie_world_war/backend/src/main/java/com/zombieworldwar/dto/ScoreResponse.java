package com.zombieworldwar.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Response DTO for score submission.
 * Requirements: 7.1, 7.3
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ScoreResponse {
    private Long entryId;
    private Boolean success;
    private Long rank;
    private Boolean isTopTen;
    private String message;
}
