package com.zombieworldwar.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * Game state data transfer object for save/load operations.
 * Requirements: 11.1, 11.2
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class GameStateDTO {
    private PlayerStateDTO player;
    private WaveStateDTO wave;
    private List<ZombieStateDTO> zombies;
    private Integer score;
    private Long playTime;
    private Long timestamp;
}
