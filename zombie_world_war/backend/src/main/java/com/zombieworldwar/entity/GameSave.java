package com.zombieworldwar.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(name = "game_saves")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class GameSave {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;
    
    @Column(name = "game_state_json", columnDefinition = "JSON", nullable = false)
    private String gameStateJson;
    
    @Column(name = "wave_reached")
    private Integer waveReached;
    
    @Column
    private Integer score;
    
    @Column(name = "saved_at")
    private LocalDateTime savedAt;
    
    @PrePersist
    protected void onCreate() {
        savedAt = LocalDateTime.now();
    }
    
    @PreUpdate
    protected void onUpdate() {
        savedAt = LocalDateTime.now();
    }
}
