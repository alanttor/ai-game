package com.zombieworldwar.exception;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Map;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ErrorResponse {
    private String error;
    private Map<String, String> details;

    public ErrorResponse(String error) {
        this.error = error;
    }
}
