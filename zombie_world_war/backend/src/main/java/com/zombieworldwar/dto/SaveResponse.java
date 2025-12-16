package com.zombieworldwar.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * Response DTO for save game operations.
 * Requirements: 11.1
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class SaveResponse {
    private Long saveId;
    private Boolean success;
    private String message;
    private LocalDateTime savedAt;
}
