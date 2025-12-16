# Implementation Plan

## Phase 1: 项目初始化与基础架构

- [x] 1. 初始化前端Vue项目






  - [x] 1.1 使用Vite创建Vue 3 + TypeScript项目

    - 配置vite.config.ts，设置别名和构建选项
    - 安装核心依赖：three, @types/three, pinia, vue-router
    - 配置TypeScript严格模式
    - _Requirements: 5.1_


  - [x] 1.2 配置Three.js和游戏引擎基础结构


    - 创建src/engine目录结构
    - 实现GameEngine基础类框架
    - 配置Three.js渲染器初始化
    - _Requirements: 5.1, 5.2_
  - [ ]* 1.3 配置Vitest和fast-check测试框架
    - 安装vitest, @vue/test-utils, fast-check
    - 配置vitest.config.ts
    - 创建测试工具函数和生成器
    - _Requirements: 12.1_

- [x] 2. 初始化后端Spring Boot项目






  - [x] 2.1 创建Spring Boot项目结构

    - 使用Spring Initializr创建项目
    - 配置Maven依赖：Spring Web, Spring Data JPA, Spring Security, MySQL Driver
    - 设置application.yml配置文件
    - _Requirements: 11.1_

  - [x] 2.2 配置数据库和JPA

    - 创建MySQL数据库schema
    - 配置JPA实体扫描和Hibernate设置
    - 实现数据库迁移脚本
    - _Requirements: 11.1, 6.3_
  - [ ]* 2.3 配置JUnit 5和jqwik测试框架
    - 添加jqwik依赖
    - 配置测试数据库（H2内存数据库）
    - 创建测试基类和工具
    - _Requirements: 11.1_

- [x] 3. Checkpoint - 确保项目结构正确





  - Ensure all tests pass, ask the user if questions arise.

## Phase 2: 数据模型与序列化

- [x] 4. 实现前端数据模型






  - [x] 4.1 创建核心TypeScript接口和类型

    - 实现Vector3, GameState, PlayerState, WeaponState, WaveState接口
    - 创建ZombieState, ZombieVariant, WeaponType枚举
    - _Requirements: 12.1, 12.5_

  - [x] 4.2 实现GameState序列化器

    - 创建GameStateSerializer类
    - 实现serialize()和deserialize()方法
    - 处理Vector3精度保留（3位小数）
    - _Requirements: 6.1, 6.2, 12.1, 12.2, 12.3, 12.5_
  - [ ]* 4.3 编写属性测试：GameState序列化往返
    - **Property 19: GameState Serialization Round-Trip**
    - **Validates: Requirements 6.1, 6.2, 6.4, 12.1, 12.2, 12.3**
  - [ ]* 4.4 编写属性测试：Vector3精度保留
    - **Property 32: Vector3 Precision Preservation**
    - **Validates: Requirements 12.5**
  - [ ]* 4.5 编写属性测试：无效JSON反序列化错误
    - **Property 31: Invalid JSON Deserialization Error**
    - **Validates: Requirements 12.4**

- [x] 5. 实现后端数据模型





  - [x] 5.1 创建JPA实体类


    - 实现User, GameSave, LeaderboardEntry实体
    - 配置JPA注解和关系映射
    - _Requirements: 8.5, 6.3, 7.1_
  - [x] 5.2 创建DTO类


    - 实现GameStateDTO, SaveResponse, LeaderboardEntryDTO
    - 实现请求/响应DTO类
    - _Requirements: 11.1, 11.2, 11.3_
  - [x] 5.3 创建Repository接口


    - 实现UserRepository, GameSaveRepository, LeaderboardRepository
    - 添加自定义查询方法
    - _Requirements: 11.1, 11.2, 11.3_

- [x] 6. Checkpoint - 确保数据模型测试通过





  - Ensure all tests pass, ask the user if questions arise.

## Phase 3: 用户认证系统

- [x] 7. 实现后端认证服务








  - [x] 7.1 配置Spring Security和JWT


    - 创建SecurityConfig配置类
    - 实现JwtTokenProvider工具类
    - 配置密码加密（BCrypt）
    - _Requirements: 8.2, 8.4_
  - [x] 7.2 实现AuthService


    - 实现用户注册逻辑（邮箱格式、密码强度验证）
    - 实现登录逻辑和JWT生成
    - 实现token刷新逻辑
    - _Requirements: 8.1, 8.2, 8.3_
  - [x] 7.3 实现AuthController


    - 创建/api/auth/register端点
    - 创建/api/auth/login端点
    - 创建/api/auth/refresh端点
    - _Requirements: 8.1, 8.2, 8.4_
  - [ ]* 7.4 编写属性测试：邮箱和密码验证
    - **Property 23: Email and Password Validation**
    - **Validates: Requirements 8.1**
  - [ ]* 7.5 编写属性测试：JWT Token发放
    - **Property 24: JWT Token Issuance**
    - **Validates: Requirements 8.2**
  - [ ]* 7.6 编写属性测试：认证错误不透明性
    - **Property 25: Authentication Error Opacity**
    - **Validates: Requirements 8.3**
  - [ ]* 7.7 编写属性测试：过期Token拒绝
    - **Property 26: Expired Token Rejection**
    - **Validates: Requirements 8.4**

- [x] 8. 实现前端认证模块





  - [x] 8.1 创建认证Pinia Store


    - 实现useAuthStore
    - 管理token存储和刷新
    - _Requirements: 8.2, 8.4_
  - [x] 8.2 创建登录/注册Vue组件


    - 实现LoginForm.vue
    - 实现RegisterForm.vue
    - 添加表单验证
    - _Requirements: 8.1_
  - [x] 8.3 实现API客户端和拦截器


    - 创建axios实例配置
    - 实现JWT token自动附加
    - 实现token过期自动刷新
    - _Requirements: 8.4_

- [x] 9. Checkpoint - 确保认证系统测试通过





  - Ensure all tests pass, ask the user if questions arise.

## Phase 4: 游戏核心引擎

- [x] 10. 实现游戏引擎核心





  - [x] 10.1 创建GameEngine类


    - 实现游戏循环（requestAnimationFrame）
    - 实现init(), start(), pause(), resume(), stop()方法
    - 实现事件系统（on, emit）
    - _Requirements: 5.1_

  - [x] 10.2 实现InputManager
    - 键盘输入监听（WASD, Space, Shift, R, 1-4）
    - 鼠标输入监听（移动、点击、滚轮）
    - 输入状态管理
    - _Requirements: 1.1, 1.2, 2.1, 2.3, 2.4_
  - [x] 10.3 实现SceneManager
    - Three.js场景初始化
    - 相机和渲染器配置
    - 光照系统设置
    - _Requirements: 5.1, 5.2_

- [x] 11. 实现玩家控制系统





  - [x] 11.1 创建Player类


    - 实现位置、旋转、生命值、体力属性
    - 实现move(), jump(), sprint()方法
    - 实现takeDamage(), heal()方法
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_


  - [x] 11.2 实现第一人称相机控制
    - 鼠标视角控制（可配置灵敏度）
    - 相机跟随玩家位置

    - _Requirements: 1.2_

  - [x] 11.3 实现玩家物理和碰撞
    - 地面检测
    - 跳跃物理（固定高度2单位）
    - 墙壁碰撞
    - _Requirements: 1.3_
  - [ ]* 11.4 编写属性测试：玩家移动方向一致性
    - **Property 1: Player Movement Direction Consistency**
    - **Validates: Requirements 1.1**
  - [ ]* 11.5 编写属性测试：相机旋转比例
    - **Property 2: Camera Rotation Proportionality**
    - **Validates: Requirements 1.2**
  - [ ]* 11.6 编写属性测试：跳跃地面约束
    - **Property 3: Jump Ground Constraint**
    - **Validates: Requirements 1.3**
  - [ ]* 11.7 编写属性测试：冲刺速度和体力消耗
    - **Property 4: Sprint Speed and Stamina Consumption**
    - **Validates: Requirements 1.4**
  - [ ]* 11.8 编写属性测试：体力阈值强制
    - **Property 5: Stamina Threshold Enforcement**
    - **Validates: Requirements 1.5**

- [x] 12. Checkpoint - 确保玩家控制测试通过





  - Ensure all tests pass, ask the user if questions arise.

## Phase 5: 武器系统

- [x] 13. 实现武器系统





  - [x] 13.1 创建Weapon基类和武器类型


    - 实现Weapon抽象类
    - 实现Pistol, Rifle, Shotgun, MeleeWeapon子类
    - 配置武器属性（伤害、射速、弹匣容量等）
    - _Requirements: 2.1, 2.2_

  - [x] 13.2 实现射击和近战攻击

    - 实现fire()方法（射线检测）
    - 实现近战攻击范围检测
    - 实现弹药消耗逻辑
    - _Requirements: 2.1, 2.6_

  - [x] 13.3 实现换弹和武器切换

    - 实现reload()方法（异步，有换弹时间）
    - 实现武器切换逻辑（数字键、滚轮）
    - _Requirements: 2.2, 2.3, 2.4_

  - [x] 13.4 实现武器视觉效果

    - 枪口火焰效果
    - 武器模型动画
    - _Requirements: 2.5_
  - [ ]* 13.5 编写属性测试：武器射击动作一致性
    - **Property 6: Weapon Fire Action Consistency**
    - **Validates: Requirements 2.1**
  - [ ]* 13.6 编写属性测试：换弹弹药转移
    - **Property 7: Reload Ammo Transfer**
    - **Validates: Requirements 2.2**
  - [ ]* 13.7 编写属性测试：武器循环顺序
    - **Property 8: Weapon Cycling Order**
    - **Validates: Requirements 2.3, 2.4**
  - [ ]* 13.8 编写属性测试：空弹匣阻止射击
    - **Property 9: Empty Magazine Blocks Firing**
    - **Validates: Requirements 2.6**

- [x] 14. Checkpoint - 确保武器系统测试通过





  - Ensure all tests pass, ask the user if questions arise.

## Phase 6: 丧尸AI系统

- [x] 15. 实现丧尸AI





  - [x] 15.1 创建Zombie类


    - 实现基础属性（位置、生命值、伤害、速度）
    - 实现状态机（IDLE, WANDERING, CHASING, ATTACKING, DYING）
    - 实现变体系统（WALKER, RUNNER, BRUTE, CRAWLER）
    - _Requirements: 3.1, 3.6_

  - [x] 15.2 实现丧尸寻路和追踪

    - 实现玩家检测（30单位范围）
    - 实现简单寻路算法
    - 实现追踪行为
    - _Requirements: 3.2_
  - [x] 15.3 实现丧尸攻击和受伤


    - 实现近战攻击（2单位范围）
    - 实现受伤反馈和生命值减少
    - 实现死亡动画和移除
    - _Requirements: 3.3, 3.4, 3.5_

  - [x] 15.4 实现丧尸3D模型和动画

    - 加载丧尸模型
    - 实现行走、攻击、死亡动画
    - _Requirements: 3.1_
  - [ ]* 15.5 编写属性测试：丧尸变体有效性
    - **Property 10: Zombie Variant Validity**
    - **Validates: Requirements 3.1**
  - [ ]* 15.6 编写属性测试：丧尸追踪触发距离
    - **Property 11: Zombie Chase Trigger Distance**
    - **Validates: Requirements 3.2**
  - [ ]* 15.7 编写属性测试：丧尸攻击触发距离
    - **Property 12: Zombie Attack Trigger Distance**
    - **Validates: Requirements 3.3**
  - [ ]* 15.8 编写属性测试：丧尸伤害应用
    - **Property 13: Zombie Damage Application**
    - **Validates: Requirements 3.4**
  - [ ]* 15.9 编写属性测试：丧尸死亡状态转换
    - **Property 14: Zombie Death State Transition**
    - **Validates: Requirements 3.5**

- [x] 16. Checkpoint - 确保丧尸AI测试通过





  - Ensure all tests pass, ask the user if questions arise.

## Phase 7: 波次生存系统

- [x] 17. 实现波次管理器







  - [x] 17.1 创建WaveManager类





    - 实现波次状态管理
    - 实现丧尸生成公式（wave * 5 + 10）


    - 实现准备阶段计时（30秒）
    - _Requirements: 4.1, 4.2, 4.3_


  - [x] 17.2 实现分数计算系统





    - 实现击杀计分（zombies * 100 * wave）
    - 实现波次完成奖励
    - _Requirements: 4.4_
  - [x] 17.3 实现游戏结束逻辑





    - 实现玩家死亡检测
    - 实现游戏结束状态
    - 实现最终分数显示
    - _Requirements: 4.5_
  - [ ]* 17.4 编写属性测试：波次生成数量公式
    - **Property 15: Wave Spawn Count Formula**
    - **Validates: Requirements 4.1**
  - [ ]* 17.5 编写属性测试：波次完成触发准备阶段
    - **Property 16: Wave Completion Triggers Preparation**
    - **Validates: Requirements 4.2**
  - [ ]* 17.6 编写属性测试：分数计算公式
    - **Property 17: Score Calculation Formula**
    - **Validates: Requirements 4.4**
  - [ ]* 17.7 编写属性测试：玩家死亡游戏结束
    - **Property 18: Game Over on Player Death**
    - **Validates: Requirements 4.5**

- [x] 18. Checkpoint - 确保波次系统测试通过





  - Ensure all tests pass, ask the user if questions arise.

## Phase 8: 3D场景与渲染

- [x] 19. 实现游戏场景



  - [x] 19.1 创建末日城市场景
    - 设计场景布局（建筑、街道、障碍物）
    - 创建或导入3D模型
    - 配置场景光照
    - _Requirements: 5.1, 5.2_

  - [x] 19.2 实现动态光照系统
    - 实现日夜循环（可选）
    - 实现室内/室外光照切换
    - 实现阴影渲染
    - _Requirements: 5.2, 5.4_

  - [x] 19.3 实现LOD和性能优化
    - 实现距离LOD系统
    - 实现视锥剔除
    - 优化渲染性能（目标60FPS）
    - _Requirements: 5.3_

  - [x] 19.4 实现环境破坏效果

    - 实现可破坏物体
    - 实现粒子效果系统
    - _Requirements: 5.5_

- [x] 20. Checkpoint - 确保场景渲染正常





  - Ensure all tests pass, ask the user if questions arise.

## Phase 9: 游戏存档系统

- [x] 21. 实现后端存档服务
  - [x] 21.1 实现GameService
    - 实现saveGame()方法
    - 实现loadGame()方法
    - 实现listSaves()方法
    - _Requirements: 6.3, 11.1, 11.2_
  - [x] 21.2 实现GameController


    - 创建POST /api/game/save端点
    - 创建GET /api/game/load/{id}端点
    - 创建GET /api/game/saves端点
    - 创建DELETE /api/game/save/{id}端点
    - _Requirements: 11.1, 11.2_
  - [ ]* 21.3 编写属性测试：用户数据关联
    - **Property 27: User Data Association**
    - **Validates: Requirements 8.5**
  - [ ]* 21.4 编写属性测试：无效请求错误响应
    - **Property 30: Invalid Request Error Response**
    - **Validates: Requirements 11.4**

- [x] 22. 实现前端存档功能





  - [x] 22.1 创建存档Pinia Store


    - 实现useGameStore
    - 管理游戏状态
    - _Requirements: 6.1, 6.2_
  - [x] 22.2 实现存档API调用


    - 实现saveGame()函数
    - 实现loadGame()函数
    - 实现错误处理
    - _Requirements: 6.3, 6.5_
  - [ ]* 22.3 编写属性测试：存档失败状态保留
    - **Property 20: Save Failure State Preservation**
    - **Validates: Requirements 6.5**

- [x] 23. Checkpoint - 确保存档系统测试通过




  - Ensure all tests pass, ask the user if questions arise.

## Phase 10: 排行榜系统

- [x] 24. 实现后端排行榜服务





  - [x] 24.1 实现LeaderboardService


    - 实现submitScore()方法
    - 实现getTopScores()方法（分页）
    - 实现getUserRank()方法
    - _Requirements: 7.1, 7.2, 7.3, 11.3_

  - [x] 24.2 实现LeaderboardController

    - 创建POST /api/leaderboard/submit端点
    - 创建GET /api/leaderboard/top端点
    - 创建GET /api/leaderboard/rank/{userId}端点
    - _Requirements: 7.1, 7.2, 11.3_
  - [ ]* 24.3 编写属性测试：排行榜条目完整性
    - **Property 21: Leaderboard Entry Completeness**
    - **Validates: Requirements 7.2**
  - [ ]* 24.4 编写属性测试：Top 10检测
    - **Property 22: Top 10 Detection**
    - **Validates: Requirements 7.3**
  - [ ]* 24.5 编写属性测试：排行榜排序顺序
    - **Property 29: Leaderboard Sorting Order**
    - **Validates: Requirements 11.3**

- [x] 25. 实现前端排行榜界面






  - [x] 25.1 创建排行榜Vue组件

    - 实现LeaderboardView.vue
    - 实现分页显示
    - 实现Top 10高亮
    - _Requirements: 7.2, 7.3_

- [x] 26. Checkpoint - 确保排行榜系统测试通过





  - Ensure all tests pass, ask the user if questions arise.

## Phase 11: 游戏UI界面

- [x] 27. 实现游戏HUD


  - [x] 27.1 创建HUD组件
    - 实现生命值条显示
    - 实现弹药计数显示
    - 实现当前武器显示
    - 实现波次信息显示
    - _Requirements: 9.1_
  - [x] 27.2 实现伤害和低血量反馈
    - 实现受伤红色晕影效果
    - 实现低血量警告（<25%）
    - _Requirements: 9.4, 9.5_
  - [ ]* 27.3 编写属性测试：低血量警告阈值
    - **Property 28: Low Health Warning Threshold**
    - **Validates: Requirements 9.5**

- [x] 28. 实现游戏菜单





  - [x] 28.1 创建主菜单


    - 实现MainMenu.vue
    - 实现开始游戏、继续游戏、设置、退出选项
    - _Requirements: 9.2_
  - [x] 28.2 创建暂停菜单


    - 实现PauseMenu.vue
    - 实现继续、保存、设置、退出选项
    - _Requirements: 9.2_
  - [x] 28.3 创建物品栏界面


    - 实现InventoryView.vue
    - 实现武器网格显示
    - _Requirements: 9.3_

- [x] 29. Checkpoint - 确保UI组件正常工作





  - Ensure all tests pass, ask the user if questions arise.

## Phase 12: 音效系统

- [x] 30. 实现音效管理器






  - [x] 30.1 创建AudioManager类

    - 实现3D空间音效
    - 实现音量控制
    - 实现音效加载和缓存
    - _Requirements: 10.1, 10.2_

  - [x] 30.2 实现武器和丧尸音效

    - 添加武器射击音效
    - 添加丧尸环境音效
    - 实现距离衰减
    - _Requirements: 10.1, 10.2_

  - [x] 30.3 实现背景音乐系统

    - 实现动态音乐切换
    - 实现波次开始警报
    - 实现暂停时音量降低
    - _Requirements: 10.3, 10.4, 10.5_

## Phase 13: 集成与优化

- [x] 31. 系统集成






  - [x] 31.1 整合所有游戏系统

    - 连接前后端API
    - 整合游戏循环中的所有管理器
    - 实现完整游戏流程
    - _Requirements: All_

  - [x] 31.2 实现游戏配置系统

    - 创建游戏设置界面
    - 实现灵敏度、音量等配置
    - 实现配置持久化
    - _Requirements: 1.2, 10.5_

- [x] 32. 性能优化和Bug修复
  - [x] 32.1 性能分析和优化
    - 分析渲染性能瓶颈
    - 优化内存使用
    - 确保60FPS目标
    - _Requirements: 5.3_
  - [x] 32.2 Bug修复和稳定性
    - 修复已知问题
    - 处理边界情况
    - 确保游戏稳定运行
    - _Requirements: All_

- [x] 33. Final Checkpoint - 确保所有测试通过
  - Ensure all tests pass, ask the user if questions arise.
