# Implementation Plan

- [x] 1. 项目初始化与核心框架






  - [x] 1.1 创建项目结构和依赖配置

    - 创建目录结构 (core/, gameplay/, content/, presentation/, data/, assets/, data_files/, tests/)
    - 创建 requirements.txt (ursina, hypothesis, pytest, pyinstaller)
    - 创建 config.py 全局配置
    - 创建 main.py 入口文件
    - _Requirements: 10.3_

  - [x] 1.2 实现 GameManager 游戏状态管理

    - 实现 GameState 枚举
    - 实现状态切换逻辑 change_state()
    - 实现 start_new_game(), pause_game(), resume_game()
    - _Requirements: 1.1, 7.5_
  - [ ]* 1.3 编写 GameManager 单元测试
    - 测试状态转换逻辑
    - 测试游戏启动流程
    - _Requirements: 1.1_

- [x] 2. 数据层实现






  - [x] 2.1 实现 SaveSystem 存档系统

    - 实现 SaveData 数据类
    - 实现 serialize_to_json() 和 deserialize_from_json()
    - 实现 save_game() 和 load_game()
    - _Requirements: 10.1, 10.2, 10.5, 10.6_
  - [ ]* 2.2 编写属性测试: JSON序列化往返
    - **Property 27: JSON serialization round-trip**
    - **Validates: Requirements 10.5, 10.6**
  - [ ]* 2.3 编写属性测试: Save/Load往返
    - **Property 26: Save/Load round-trip**
    - **Validates: Requirements 10.1, 10.2**
  - [x] 2.4 实现 AssetLoader 资源加载器


    - 实现模型、贴图、音频加载
    - 实现资源缓存机制
    - _Requirements: 8.1_

- [x] 3. 角色系统实现






  - [x] 3.1 创建角色数据文件 characters.json

    - 定义104期训练兵团成员数据 (艾伦、三笠、阿尔敏、让、康尼、萨沙、莱纳、贝尔托特、尤弥尔、克里斯塔、马尔科、安妮)
    - 定义每个角色的stats、background、personality、relationships
    - _Requirements: 1.2, 1.3_

  - [x] 3.2 实现 Character 角色类

    - 实现 CharacterStats 数据类
    - 实现 load_from_json() 静态方法
    - 实现 get_dialogue_variant() 和 get_reaction()
    - _Requirements: 1.2, 1.4, 6.4_
  - [ ]* 3.3 编写属性测试: 角色属性应用一致性
    - **Property 1: Character stats application consistency**
    - **Validates: Requirements 1.2, 1.4**
  - [ ]* 3.4 编写属性测试: 角色信息完整性
    - **Property 2: Character info completeness**
    - **Validates: Requirements 1.3**

- [x] 4. Checkpoint - 确保所有测试通过





  - Ensure all tests pass, ask the user if questions arise.


- [-] 5. 资源管理系统实现




  - [x] 5.1 实现 ResourceSystem 资源管理


    - 实现 gas_level, blade_count, blade_durability 属性
    - 实现 consume_gas(), refill_gas()
    - 实现 switch_blade(), consume_blade_durability()
    - 实现警告阈值检测 (gas < 20%, blade < 2)
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  - [ ]* 5.2 编写属性测试: 低气体警告阈值
    - **Property 13: Low gas warning threshold**
    - **Validates: Requirements 4.2**
  - [ ]* 5.3 编写属性测试: 低刀刃警告阈值
    - **Property 14: Low blade warning threshold**
    - **Validates: Requirements 4.3**
  - [ ]* 5.4 编写属性测试: 补给站补充
    - **Property 15: Supply station refill**
    - **Validates: Requirements 4.4**
  - [ ]* 5.5 编写属性测试: 刀刃切换恢复耐久
    - **Property 16: Blade switch restores durability**
    - **Validates: Requirements 4.5**

- [-] 6. 立体机动装置系统实现




  - [x] 6.1 实现 ODMSystem 核心逻辑


    - 实现 HookState 数据类
    - 实现 fire_hook() 钩锁发射
    - 实现 release_hook() 钩锁释放
    - 实现 update_swing_physics() 摆荡物理
    - 实现 activate_boost() 气体推进
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_
  - [ ]* 6.2 编写属性测试: 钩锁附着有效性
    - **Property 3: Hook attachment validity**
    - **Validates: Requirements 2.1**
  - [ ]* 6.3 编写属性测试: 释放钩锁保持动量
    - **Property 4: Momentum preservation on hook release**
    - **Validates: Requirements 2.6**
  - [ ]* 6.4 编写属性测试: 推进消耗气体
    - **Property 5: Gas consumption on boost**
    - **Validates: Requirements 2.3**
  - [ ]* 6.5 编写属性测试: 气体耗尽禁用推进
    - **Property 6: Gas depletion disables boost**
    - **Validates: Requirements 2.5**

- [-] 7. 战斗系统实现




  - [x] 7.1 实现 CombatSystem 战斗逻辑


    - 实现 AttackResult 数据类
    - 实现 perform_slash() 斩击攻击
    - 实现 check_nape_hit() 后颈判定
    - 实现 calculate_damage() 伤害计算
    - 实现 update_combo() 连击系统
    - 实现 get_score_multiplier() 分数计算
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_
  - [ ]* 7.2 编写属性测试: 后颈命中造成击杀
    - **Property 7: Nape hit causes kill**
    - **Validates: Requirements 3.1**
  - [ ]* 7.3 编写属性测试: 非后颈命中不击杀
    - **Property 8: Non-nape hit preserves titan life**
    - **Validates: Requirements 3.2**
  - [ ]* 7.4 编写属性测试: 连击计数递增
    - **Property 9: Combo counter increments on consecutive kills**
    - **Validates: Requirements 3.3**
  - [ ]* 7.5 编写属性测试: 攻击消耗刀刃耐久
    - **Property 10: Blade durability decreases on attack**
    - **Validates: Requirements 3.4**
  - [ ]* 7.6 编写属性测试: 零耐久禁用攻击
    - **Property 11: Zero durability disables attack**
    - **Validates: Requirements 3.5**
  - [ ]* 7.7 编写属性测试: 击杀分数计算
    - **Property 12: Kill score calculation**
    - **Validates: Requirements 3.6**

- [x] 8. Checkpoint - 确保所有测试通过





  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. 巨人AI系统实现






  - [x] 9.1 创建巨人数据文件 titans.json

    - 定义普通巨人 (3m, 5m, 7m, 10m, 15m)
    - 定义奇行种巨人
    - 定义特殊巨人 (铠之巨人、超大型巨人等)
    - _Requirements: 5.1_


  - [ ] 9.2 实现 TitanAI 行为系统
    - 实现 TitanType 和 TitanState 枚举
    - 实现 detect_player() 玩家检测
    - 实现 pursue_target() 追踪逻辑
    - 实现 perform_attack() 和 perform_grab() 攻击
    - 实现 take_damage() 和 die() 受伤死亡
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  - [ ]* 9.3 编写属性测试: 巨人类型决定行为模式
    - **Property 17: Titan type determines behavior pattern**
    - **Validates: Requirements 5.1**
  - [ ]* 9.4 编写属性测试: 检测触发追踪
    - **Property 18: Detection triggers pursuit**
    - **Validates: Requirements 5.2**
  - [ ]* 9.5 编写属性测试: 攻击触发响应
    - **Property 19: Attack triggers response**
    - **Validates: Requirements 5.3**

- [x] 10. 剧情系统实现

  - [x] 10.1 创建剧情数据文件 stories.json
    - 定义第一季章节 (希干希纳陷落、托洛斯特防卫战、女巨人篇)
    - 定义第二季章节 (兽之巨人、乌特加尔德城)
    - 定义第三季章节 (王政篇、玛利亚之墙夺还战)
    - 为每个角色定义差异化对话
    - _Requirements: 6.1, 6.2, 6.3_
  - [x] 10.2 实现 StorySystem 剧情管理


    - 实现 StoryChapter 数据类
    - 实现 load_chapter() 章节加载
    - 实现 unlock_next_chapter() 解锁逻辑
    - 实现 get_cutscene() 获取过场
    - 实现 get_character_perspective() 角色视角
    - _Requirements: 6.1, 6.2, 6.4, 6.5_
  - [ ]* 10.3 编写属性测试: 任务完成解锁下一章节
    - **Property 20: Mission completion unlocks next chapter**
    - **Validates: Requirements 6.1**
  - [ ]* 10.4 编写属性测试: 角色特定对话
    - **Property 21: Character-specific dialogue**
    - **Validates: Requirements 6.2**
  - [ ]* 10.5 编写属性测试: 角色反应一致性
    - **Property 22: Character reaction consistency**
    - **Validates: Requirements 6.5**

- [x] 11. 关卡系统实现






  - [x] 11.1 创建关卡数据文件 levels.json

    - 定义托洛斯特区关卡
    - 定义巨树森林关卡
    - 定义希干希纳区关卡
    - 定义各关卡的巨人生成点和任务目标
    - _Requirements: 7.1, 7.2_


  - [ ] 11.2 实现 LevelSystem 关卡管理
    - 实现 SpawnPoint 和 LevelData 数据类
    - 实现 load_level() 关卡加载
    - 实现 spawn_titan() 巨人生成
    - 实现 check_objectives() 目标检查
    - 实现 complete_level() 和 fail_level()
    - _Requirements: 7.1, 7.2, 7.4, 7.5_
  - [ ]* 11.3 编写属性测试: 关卡环境加载
    - **Property 23: Level environment loading**
    - **Validates: Requirements 7.1**
  - [ ]* 11.4 编写属性测试: 巨人生成准确性
    - **Property 24: Titan spawn accuracy**
    - **Validates: Requirements 7.2**
  - [ ]* 11.5 编写属性测试: 目标完成触发结果
    - **Property 25: Objective completion triggers results**
    - **Validates: Requirements 7.4**

- [x] 12. Checkpoint - 确保所有测试通过





  - Ensure all tests pass, ask the user if questions arise.


- [-] 13. 输入控制系统实现




  - [x] 13.1 实现 InputManager 输入管理


    - 实现键盘映射 (WASD移动、空格跳跃、鼠标左键攻击、鼠标右键钩锁、Shift推进)
    - 实现输入事件分发
    - 实现控制教程显示
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_
  - [ ]* 13.2 编写属性测试: 移动输入映射
    - **Property 28: Movement input mapping**
    - **Validates: Requirements 11.1**
  - [ ]* 13.3 编写属性测试: 钩锁输入触发发射
    - **Property 29: Hook input triggers fire**
    - **Validates: Requirements 11.2**
  - [ ]* 13.4 编写属性测试: 攻击输入触发斩击
    - **Property 30: Attack input triggers slash**
    - **Validates: Requirements 11.3**

- [x] 14. 玩家实体整合






  - [x] 14.1 实现 Player 玩家实体

    - 整合 Character、ODMSystem、CombatSystem、ResourceSystem
    - 实现玩家模型加载和动画
    - 实现碰撞检测
    - 实现生命值系统
    - _Requirements: 1.4, 2.4, 3.4, 4.1_

  - [x] 14.2 实现玩家与巨人交互

    - 实现攻击碰撞检测
    - 实现被抓取QTE
    - 实现死亡处理
    - _Requirements: 3.1, 5.5, 7.5_

- [x] 15. UI系统实现






  - [x] 15.1 实现 HUD 游戏界面

    - 实现气体和刀刃显示
    - 实现生命值显示
    - 实现连击计数显示
    - 实现警告指示器
    - _Requirements: 4.1, 4.2, 4.3_

  - [x] 15.2 实现菜单系统

    - 实现主菜单 (新游戏、继续、设置、退出)
    - 实现角色选择界面
    - 实现暂停菜单
    - 实现结果界面
    - _Requirements: 1.1, 1.3, 7.4, 7.5_

  - [x] 15.3 实现对话系统

    - 实现对话框UI
    - 实现过场动画播放
    - 实现角色立绘显示
    - _Requirements: 6.2_

- [x] 16. 图形渲染系统实现





  - [x] 16.1 实现卡通渲染着色器


    - 创建 cel-shading 着色器
    - 实现描边效果
    - _Requirements: 8.1_

  - [x] 16.2 实现视觉特效

    - 实现速度线效果
    - 实现运动模糊
    - 实现巨人蒸汽消散效果
    - _Requirements: 8.2, 8.3_

- [x] 17. 音频系统实现








  - [x] 17.1 实现 AudioSystem 音频管理






    - 实现音效播放 (ODM、战斗、巨人)
    - 实现背景音乐播放
    - 实现音量控制
    - _Requirements: 9.1, 9.2, 9.3, 9.4_

- [x] 18. Checkpoint - 确保所有测试通过





  - Ensure all tests pass, ask the user if questions arise.

- [x] 19. 场景管理与游戏流程






  - [x] 19.1 实现 SceneManager 场景管理

    - 实现场景切换逻辑
    - 实现加载画面
    - _Requirements: 7.1_

  - [x] 19.2 实现完整游戏流程

    - 整合主菜单 -> 角色选择 -> 剧情 -> 关卡 -> 结果
    - 实现章节解锁流程
    - 实现存档/读档流程
    - _Requirements: 6.1, 10.1, 10.2_

- [ ] 20. 游戏内容填充







  - [ ] 20.1 创建占位3D模型
    - 创建玩家角色占位模型
    - 创建巨人占位模型
    - 创建环境占位模型 (建筑、树木、城墙)
    - _Requirements: 8.1_
  - [ ] 20.2 创建占位音频
    - 创建ODM音效占位
    - 创建战斗音效占位
    - 创建背景音乐占位
    - _Requirements: 9.1, 9.2, 9.3_
  - [ ] 20.3 完善剧情内容
    - 完善所有角色对话变体
    - 完善过场动画脚本
    - _Requirements: 6.2, 6.4, 6.5_

- [ ] 21. 打包与分发
  - [ ] 21.1 配置 PyInstaller 打包
    - 创建 build.spec 配置文件
    - 配置资源文件打包
    - 配置依赖打包
    - _Requirements: 10.3_
  - [ ] 21.2 生成可执行文件
    - 执行打包命令
    - 测试独立运行
    - 创建安装程序 (可选: 使用 NSIS 或 Inno Setup)
    - _Requirements: 10.3, 10.4_

- [ ] 22. Final Checkpoint - 确保所有测试通过
  - Ensure all tests pass, ask the user if questions arise.

