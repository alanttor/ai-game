package com.zombieworldwar.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Zombie state data transfer object.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ZombieStateDTO {
    private String id;
    private Vector3DTO position;
    private Integer health;
    private String state;
    private String variant;
}
