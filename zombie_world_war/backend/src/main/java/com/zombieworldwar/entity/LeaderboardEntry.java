package com.zombieworldwar.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(name = "leaderboard", indexes = {
    @Index(name = "idx_score", columnList = "score DESC")
})
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class LeaderboardEntry {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;
    
    @Column(nullable = false)
    private Integer score;
    
    @Column(name = "wave_reached", nullable = false)
    private Integer waveReached;
    
    @Column(name = "zombies_killed", nullable = false)
    private Integer zombiesKilled;
    
    @Column(name = "play_time_seconds", nullable = false)
    private Long playTimeSeconds;
    
    @Column(name = "achieved_at")
    private LocalDateTime achievedAt;
    
    @PrePersist
    protected void onCreate() {
        achievedAt = LocalDateTime.now();
    }
}
