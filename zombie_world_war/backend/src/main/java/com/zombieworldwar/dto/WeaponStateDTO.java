package com.zombieworldwar.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Weapon state data transfer object.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class WeaponStateDTO {
    private String id;
    private Integer currentAmmo;
    private Integer reserveAmmo;
}
