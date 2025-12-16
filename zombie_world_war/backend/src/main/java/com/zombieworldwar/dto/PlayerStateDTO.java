package com.zombieworldwar.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * Player state data transfer object.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class PlayerStateDTO {
    private Vector3DTO position;
    private Vector3DTO rotation;
    private Integer health;
    private Integer stamina;
    private List<WeaponStateDTO> weapons;
    private Integer currentWeaponIndex;
}
