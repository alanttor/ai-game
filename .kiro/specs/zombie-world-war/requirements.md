# Requirements Document

## Introduction

本文档定义了"Zombie World War"（丧尸世界大战）3D射击生存游戏的需求规格。该游戏设定在全球生化病毒爆发后的末日世界，玩家需要使用各种武器射杀丧尸，在废墟城市中生存。游戏采用Vue 3 + Three.js前端技术栈实现3D渲染和游戏交互，Spring Boot后端处理游戏数据、存档和排行榜等功能。

## Glossary

- **Player（玩家）**: 游戏中由用户控制的角色实体
- **Zombie（丧尸）**: 游戏中的敌对AI实体，会追踪并攻击玩家
- **Weapon（武器）**: 玩家用于攻击丧尸的装备，包括枪械和近战武器
- **Health（生命值）**: 玩家或丧尸的生存状态数值
- **Ammo（弹药）**: 枪械武器的消耗品
- **Wave（波次）**: 丧尸进攻的回合单位
- **Scene（场景）**: 游戏中的3D环境地图
- **GameState（游戏状态）**: 包含玩家数据、进度、分数等的游戏运行时状态
- **SaveData（存档数据）**: 持久化存储的游戏进度数据
- **Leaderboard（排行榜）**: 记录玩家最高分数的全局排名系统

## Requirements

### Requirement 1: 玩家角色控制

**User Story:** As a player, I want to control my character with keyboard and mouse, so that I can navigate the 3D world and aim at zombies.

#### Acceptance Criteria

1. WHEN the player presses W/A/S/D keys THEN the Player SHALL move forward/left/backward/right relative to the camera direction
2. WHEN the player moves the mouse THEN the Player camera SHALL rotate to follow the mouse movement with configurable sensitivity
3. WHEN the player presses the Space key THEN the Player SHALL jump with a fixed height of 2 units if currently on ground
4. WHEN the player presses the Shift key while moving THEN the Player SHALL sprint at 1.5x normal speed while consuming stamina
5. WHILE the Player stamina is zero THEN the Player SHALL move at normal speed only until stamina regenerates above 20%

### Requirement 2: 武器系统

**User Story:** As a player, I want to use different weapons to fight zombies, so that I can choose the best strategy for survival.

#### Acceptance Criteria

1. WHEN the player left-clicks THEN the Weapon SHALL fire a projectile or perform a melee attack based on weapon type
2. WHEN the player presses R key THEN the Weapon SHALL reload ammunition from inventory if current magazine is not full
3. WHEN the player scrolls mouse wheel THEN the Player SHALL switch to the next/previous weapon in inventory
4. WHEN the player presses number keys 1-4 THEN the Player SHALL equip the weapon in the corresponding slot
5. WHEN a weapon fires THEN the Weapon SHALL display muzzle flash effect and play corresponding sound
6. WHEN ammunition reaches zero THEN the Weapon SHALL prevent firing and display empty magazine indicator

### Requirement 3: 丧尸AI系统

**User Story:** As a player, I want zombies to behave realistically, so that the game provides a challenging and immersive experience.

#### Acceptance Criteria

1. WHEN a Zombie spawns THEN the Zombie SHALL have randomized appearance from predefined variants
2. WHEN the Player is within 30 units of a Zombie THEN the Zombie SHALL navigate toward the Player using pathfinding
3. WHEN a Zombie reaches melee range of 2 units THEN the Zombie SHALL perform attack animation and deal damage to Player
4. WHEN a Zombie receives damage THEN the Zombie SHALL display hit reaction and reduce health accordingly
5. WHEN Zombie health reaches zero THEN the Zombie SHALL play death animation and be removed after 5 seconds
6. WHILE a Zombie is not aware of Player THEN the Zombie SHALL wander randomly within spawn area

### Requirement 4: 波次生存系统

**User Story:** As a player, I want to survive increasingly difficult waves of zombies, so that I can test my skills and achieve high scores.

#### Acceptance Criteria

1. WHEN a wave starts THEN the GameState SHALL spawn zombies equal to (wave_number * 5 + 10) at designated spawn points
2. WHEN all zombies in current wave are eliminated THEN the GameState SHALL start a 30-second preparation phase
3. WHEN preparation phase ends THEN the GameState SHALL start the next wave with increased difficulty
4. WHEN a wave completes THEN the Player SHALL receive score points equal to (zombies_killed * 100 * wave_number)
5. WHEN Player health reaches zero THEN the GameState SHALL end the game and display final score

### Requirement 5: 3D渲染与场景

**User Story:** As a player, I want to explore a detailed 3D post-apocalyptic environment, so that I feel immersed in the zombie apocalypse setting.

#### Acceptance Criteria

1. WHEN the game loads THEN the Scene SHALL render a complete 3D environment with buildings, streets, and obstacles
2. WHEN the Player moves THEN the Scene SHALL update lighting and shadows in real-time
3. WHEN objects are far from camera THEN the Scene SHALL apply level-of-detail optimization to maintain 60 FPS
4. WHEN the Player enters a building THEN the Scene SHALL adjust ambient lighting to interior settings
5. WHEN environmental objects are destroyed THEN the Scene SHALL display particle effects and debris

### Requirement 6: 游戏存档系统

**User Story:** As a player, I want to save and load my game progress, so that I can continue playing later.

#### Acceptance Criteria

1. WHEN the player requests save THEN the SaveData SHALL serialize current GameState to JSON format
2. WHEN the player requests load THEN the SaveData SHALL deserialize JSON and restore GameState
3. WHEN save operation completes THEN the SaveData SHALL store data to backend database via REST API
4. WHEN load operation completes THEN the GameState SHALL restore player position, health, weapons, and wave progress
5. IF save operation fails THEN the SaveData SHALL display error message and retain current game state

### Requirement 7: 排行榜系统

**User Story:** As a player, I want to see global rankings, so that I can compare my performance with other players.

#### Acceptance Criteria

1. WHEN game ends THEN the Leaderboard SHALL submit player score to backend server
2. WHEN player views leaderboard THEN the Leaderboard SHALL display top 100 scores with player names and wave reached
3. WHEN player achieves top 10 score THEN the Leaderboard SHALL highlight the entry and display congratulation message
4. WHEN leaderboard data is requested THEN the Leaderboard SHALL return paginated results within 500ms

### Requirement 8: 用户认证系统

**User Story:** As a player, I want to create an account and login, so that my progress and scores are saved to my profile.

#### Acceptance Criteria

1. WHEN a user registers THEN the System SHALL validate email format and password strength (minimum 8 characters)
2. WHEN a user logs in with valid credentials THEN the System SHALL issue JWT token valid for 24 hours
3. WHEN a user logs in with invalid credentials THEN the System SHALL return authentication error without revealing which field is incorrect
4. WHEN JWT token expires THEN the System SHALL require re-authentication before allowing save operations
5. WHEN user is authenticated THEN the System SHALL associate all game saves and scores with user account

### Requirement 9: 游戏UI界面

**User Story:** As a player, I want clear and responsive UI elements, so that I can monitor my status and navigate game menus easily.

#### Acceptance Criteria

1. WHEN game is running THEN the UI SHALL display health bar, ammo count, current weapon, and wave number
2. WHEN player pauses game THEN the UI SHALL display pause menu with resume, save, settings, and quit options
3. WHEN player opens inventory THEN the UI SHALL display all collected weapons and items in grid layout
4. WHEN player takes damage THEN the UI SHALL display red vignette effect proportional to damage received
5. WHEN player health is below 25% THEN the UI SHALL display pulsing low health warning indicator

### Requirement 10: 音效与音乐系统

**User Story:** As a player, I want immersive audio feedback, so that the game atmosphere is enhanced.

#### Acceptance Criteria

1. WHEN weapon fires THEN the Audio System SHALL play weapon-specific sound effect with 3D spatial positioning
2. WHEN zombie is nearby THEN the Audio System SHALL play ambient zombie sounds with distance-based volume
3. WHEN wave starts THEN the Audio System SHALL play alert sound and increase background music intensity
4. WHEN player is in danger THEN the Audio System SHALL crossfade to tense music track
5. WHEN game is paused THEN the Audio System SHALL reduce all audio volume by 50%

### Requirement 11: 后端API服务

**User Story:** As a system, I want robust backend services, so that game data is reliably stored and retrieved.

#### Acceptance Criteria

1. WHEN frontend requests game save THEN the Backend SHALL accept POST request with GameState JSON and store to database
2. WHEN frontend requests game load THEN the Backend SHALL return saved GameState JSON for authenticated user
3. WHEN frontend requests leaderboard THEN the Backend SHALL return sorted score list with pagination support
4. WHEN API receives invalid request THEN the Backend SHALL return appropriate HTTP error code with error message
5. WHEN database operation fails THEN the Backend SHALL log error and return 500 status with generic error message

### Requirement 12: 游戏数据序列化

**User Story:** As a developer, I want consistent data serialization, so that game state can be reliably saved and restored.

#### Acceptance Criteria

1. WHEN GameState is serialized THEN the Serializer SHALL convert all game objects to JSON format
2. WHEN GameState is deserialized THEN the Serializer SHALL reconstruct all game objects from JSON
3. WHEN serialization completes THEN the Serializer SHALL produce identical GameState when round-tripped through serialize/deserialize
4. WHEN invalid JSON is provided THEN the Serializer SHALL throw validation error with specific field information
5. WHEN serializing Vector3 positions THEN the Serializer SHALL preserve precision to 3 decimal places
