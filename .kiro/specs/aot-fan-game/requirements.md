# Requirements Document

## Introduction

本文档定义了一款基于《进击的巨人》(Attack on Titan)的全年龄向第三人称动作同人游戏的需求规范。游戏核心玩法围绕立体机动装置(3D Maneuver Gear/ODM Gear)展开，玩家可选择104期训练兵团任意成员体验动漫第一至第三季的剧情。游戏使用Python技术栈开发，支持本地运行及打包为可执行文件分发。

## Glossary

- **ODM Gear (立体机动装置)**: 调查兵团使用的特殊装备，通过钩锁和气体推进实现高速空中机动
- **Titan (巨人)**: 游戏中的主要敌人，需攻击后颈弱点才能击杀
- **Nape (后颈)**: 巨人的唯一弱点，位于颈部后方
- **104th Training Corps (104期训练兵团)**: 可选角色所属的训练兵团
- **Survey Corps (调查兵团)**: 游戏主要剧情所在的兵团
- **Gas (气体)**: ODM装置的燃料，消耗品
- **Blade (刀刃)**: 用于斩杀巨人的武器，消耗品
- **Grappling Hook (钩锁)**: ODM装置的抓取组件，用于固定和摆荡
- **Cel-Shading (卡通渲染)**: 模拟动漫风格的渲染技术
- **Player Character (玩家角色)**: 玩家控制的104期成员

## Requirements

### Requirement 1: 角色选择系统

**User Story:** As a player, I want to select any member of the 104th Training Corps as my playable character, so that I can experience the story from different perspectives based on each character's unique personality and abilities.

#### Acceptance Criteria

1. WHEN the player starts a new game THEN the Game System SHALL display a character selection screen with all available 104th Training Corps members
2. WHEN the player selects a character THEN the Game System SHALL load that character's unique stats, dialogue, and perspective for the story
3. WHEN displaying character information THEN the Game System SHALL show character name, portrait, base stats, and brief background description
4. WHILE a character is selected THEN the Game System SHALL apply that character's unique movement speed, attack power, and stamina modifiers throughout gameplay

### Requirement 2: 立体机动装置核心机制

**User Story:** As a player, I want to use the ODM Gear to perform high-speed aerial maneuvers, so that I can experience the thrilling movement system from the anime.

#### Acceptance Criteria

1. WHEN the player activates the grappling hook THEN the ODM System SHALL fire a hook toward the aimed direction and attach to valid surfaces within range
2. WHEN the hook is attached THEN the ODM System SHALL simulate physics-based rope swinging with realistic momentum
3. WHEN the player activates propulsion boost THEN the ODM System SHALL accelerate the player character in the current movement direction while consuming gas
4. WHILE the player is airborne THEN the ODM System SHALL allow directional control for aerial maneuvering
5. WHEN gas is depleted THEN the ODM System SHALL disable propulsion boost and reduce hook retraction speed
6. WHEN the player releases the hook THEN the ODM System SHALL detach from the surface and preserve current momentum

### Requirement 3: 战斗系统

**User Story:** As a player, I want to attack and defeat Titans by targeting their weak points, so that I can experience the satisfying combat from the anime.

#### Acceptance Criteria

1. WHEN the player performs a slash attack near a Titan's nape THEN the Combat System SHALL deal critical damage and trigger a kill animation
2. WHEN the player attacks non-nape body parts THEN the Combat System SHALL deal reduced damage without killing the Titan
3. WHEN the player performs consecutive successful nape attacks THEN the Combat System SHALL track and display combo count
4. WHILE attacking THEN the Combat System SHALL consume blade durability per strike
5. WHEN blade durability reaches zero THEN the Combat System SHALL disable slash attacks until the player equips a new blade
6. WHEN the player successfully kills a Titan THEN the Combat System SHALL award score points based on attack style and combo multiplier

### Requirement 4: 资源管理系统

**User Story:** As a player, I want to manage my gas and blade supplies, so that I can make strategic decisions during combat.

#### Acceptance Criteria

1. WHILE gameplay is active THEN the Resource System SHALL display current gas level and blade count on the HUD
2. WHEN gas level falls below 20 percent THEN the Resource System SHALL display a low gas warning indicator
3. WHEN blade count falls below 2 THEN the Resource System SHALL display a low blade warning indicator
4. WHEN the player interacts with a supply station THEN the Resource System SHALL refill gas and blades to maximum capacity
5. WHEN the player presses the blade switch key THEN the Resource System SHALL replace the current blade with a fresh one from inventory

### Requirement 5: 巨人AI系统

**User Story:** As a player, I want Titans to behave according to their types and react to my actions, so that combat feels challenging and authentic.

#### Acceptance Criteria

1. WHEN a Titan spawns THEN the AI System SHALL assign behavior patterns based on Titan type (Normal, Abnormal, or Special)
2. WHILE a player is within detection range THEN the AI System SHALL cause the Titan to track and pursue the player
3. WHEN the player attacks a Titan THEN the AI System SHALL trigger defensive or aggressive response behaviors
4. WHEN a Titan attempts to grab the player THEN the AI System SHALL execute a grab attack with a telegraphed wind-up animation
5. IF the player is grabbed by a Titan THEN the Combat System SHALL initiate a quick-time event for escape

### Requirement 6: 剧情系统

**User Story:** As a player, I want to experience the story from Season 1 to Season 3 of the anime, so that I can relive the epic narrative while playing.

#### Acceptance Criteria

1. WHEN the player completes a mission THEN the Story System SHALL unlock the next sequential story chapter
2. WHEN a story chapter begins THEN the Story System SHALL display narrative cutscenes with dialogue appropriate to the selected character's perspective
3. WHILE in story mode THEN the Story System SHALL present missions that follow the anime's major plot events from Season 1 through Season 3
4. WHEN the player selects a different character THEN the Story System SHALL adjust dialogue and internal monologue to reflect that character's personality and knowledge
5. WHEN a key story event occurs THEN the Story System SHALL trigger character-specific reactions based on their relationships and background

### Requirement 7: 游戏关卡系统

**User Story:** As a player, I want to play through various iconic locations from the anime, so that I can feel immersed in the world.

#### Acceptance Criteria

1. WHEN a mission loads THEN the Level System SHALL generate the appropriate environment (Trost District, Forest of Giant Trees, Wall areas, etc.)
2. WHEN the level loads THEN the Level System SHALL spawn Titans at designated spawn points based on mission parameters
3. WHILE in a level THEN the Level System SHALL provide sufficient vertical structures for ODM Gear traversal
4. WHEN mission objectives are completed THEN the Level System SHALL trigger mission completion and display results screen
5. WHEN the player character health reaches zero THEN the Level System SHALL display game over screen with retry option

### Requirement 8: 视觉呈现系统

**User Story:** As a player, I want the game to have an anime-style visual presentation, so that it feels authentic to the source material.

#### Acceptance Criteria

1. WHEN rendering characters and environments THEN the Graphics System SHALL apply cel-shading techniques to achieve anime-style visuals
2. WHEN the player performs ODM maneuvers THEN the Graphics System SHALL display speed lines and motion blur effects
3. WHEN a Titan is killed THEN the Graphics System SHALL render steam dissolution effects on the Titan body
4. WHILE gameplay is active THEN the Graphics System SHALL maintain a minimum frame rate of 30 frames per second on target hardware
5. WHEN displaying UI elements THEN the Graphics System SHALL use a visual style consistent with the anime aesthetic

### Requirement 9: 音频系统

**User Story:** As a player, I want appropriate sound effects and music, so that the game atmosphere matches the epic tone of the anime.

#### Acceptance Criteria

1. WHEN ODM Gear is activated THEN the Audio System SHALL play corresponding hook firing, cable tension, and gas release sound effects
2. WHEN combat actions occur THEN the Audio System SHALL play blade slash and Titan impact sound effects
3. WHILE in gameplay THEN the Audio System SHALL play background music appropriate to the current mission mood
4. WHEN a Titan is nearby THEN the Audio System SHALL adjust audio cues to indicate threat proximity

### Requirement 10: 游戏存档与打包

**User Story:** As a player, I want to save my progress and share the game with others, so that I can continue playing later and let friends enjoy the game.

#### Acceptance Criteria

1. WHEN the player triggers a save action THEN the Save System SHALL persist current progress, unlocked chapters, and character stats to local storage
2. WHEN the player loads a save file THEN the Save System SHALL restore the exact game state from the saved data
3. WHEN the game is built for distribution THEN the Build System SHALL package all assets and dependencies into a standalone executable installer
4. WHEN a user runs the installer on a Windows system THEN the Build System SHALL install the game without requiring additional runtime dependencies
5. WHEN serializing save data THEN the Save System SHALL encode game state to JSON format
6. WHEN deserializing save data THEN the Save System SHALL decode JSON and reconstruct the equivalent game state

### Requirement 11: 控制系统

**User Story:** As a player, I want intuitive controls for movement and combat, so that I can focus on the action without struggling with the interface.

#### Acceptance Criteria

1. WHEN the player presses movement keys THEN the Control System SHALL move the character in the corresponding direction relative to camera orientation
2. WHEN the player presses the hook key THEN the Control System SHALL fire the grappling hook toward the camera's aim point
3. WHEN the player presses the attack key THEN the Control System SHALL execute a slash attack in the aimed direction
4. WHEN the player presses the boost key THEN the Control System SHALL activate gas propulsion
5. WHEN the game starts THEN the Control System SHALL display a controls tutorial overlay for new players

