package com.zombieworldwar.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Vector3 data transfer object for 3D positions and rotations.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Vector3DTO {
    private Double x;
    private Double y;
    private Double z;
}
