package com.zombieworldwar.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Wave state data transfer object.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class WaveStateDTO {
    private Integer currentWave;
    private Integer zombiesKilled;
    private Integer totalZombiesInWave;
    private Boolean isPreparationPhase;
}
