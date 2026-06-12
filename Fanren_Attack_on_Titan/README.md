# 凡人修仙 - 进击的巨人 3D 动作游戏原型

基于 Python & Ursina 3D 引擎开发的《进击的巨人》同人动作游戏系统架构原型。本系统目前实现了高解耦的底层框架设计，主要支持模块化游戏系统的逻辑测试与验证。

---

## 🛠️ 技术栈

- **开发语言**: Python 3.8+
- **3D 引擎**: Ursina 3D Engine (基于 Panda3D)
- **依赖库**: `ursina>=5.0.0` (详见 [requirements.txt](./requirements.txt))

---

## 📂 项目结构与架构设计

项目采用严格的职责分离（SoC）架构，将核心引擎、玩法、内容与表现层完全解耦：

```
Fanren_Attack_on_Titan/
├── main.py                     # 游戏系统主测试入口
├── config.py                   # 全局图形、音频与控制配置
├── requirements.txt            # 项目依赖
├── core/                       # 核心引擎管理模块
│   ├── game_controller.py      # 系统协调器 (Mediator)，汇总音频、存档、剧情及关卡系统
│   ├── game_manager.py         # 状态机控制器，驱动游戏场景状态切换
│   ├── input_manager.py        # 输入映射系统，接管键盘与鼠标的动作映射
│   └── scene_manager.py        # 负责实体在场景中的创建与垃圾回收
├── gameplay/                   # 玩法机制系统
│   ├── player.py               # 玩家第一/三人称控制器，物理及碰撞处理
│   ├── odm_system.py           # 立体机动装置 (ODM) 绳索拉力及轨迹物理引擎
│   ├── combat_system.py        # 刀刃损耗、攻击盒检测与割后颈判定
│   ├── titan_ai.py             # 巨人行为树模型 (包含追踪、闲逛、攻击状态机)
│   ├── player_titan_interaction.py # 攀爬、抓取及死亡等动态连结交互
│   └── resource_system.py      # 瓦斯罐及双刀片资源更新器
├── content/                    # 静态与动态内容管理
│   ├── character.py            # 角色能力参数与技能组定义
│   ├── level_system.py         # 关卡出生点、通关规则及敌军配置数据
│   └── story_system.py         # 战役章节和对话文本定义
├── presentation/               # 表现与渲染层
│   ├── audio.py                # 3D 空间音频驱动，提供 Ursina/Mock 双兼容运行环境
│   ├── graphics.py             # 视角抖动、模糊后处理及光照环境管理
│   ├── visual_effects.py       # 斩击刀光、喷气尾迹和血迹飞溅等粒子系统
│   └── ui/                     # 游戏菜单、选人与主战斗界面的 HTML/CSS UI 定义
└── data/                       # 基础持久化层
    ├── asset_loader.py         # 异步资源载入器，无 Ursina 环境下自动退避至 Placeholder 模式
    └── save_system.py          # 基于 JSON 的游戏进度存档读写系统
```

---

## ⚙️ 核心系统设计逻辑

### 1. 立体机动物理 (ODM System)
通过 [odm_system.py](./gameplay/odm_system.py) 模块计算双锚点的拉力力矩、向心力以及钢丝绳的卷绕缩短速度。
$$F_{\text{rope}} = k \cdot (L_{\text{current}} - L_{\text{target}})$$
系统通过检测玩家视角准星的目标法线决定挂钩定点。

### 2. 弱耦合容错性
资源加载器 [asset_loader.py](./data/asset_loader.py) 与音频控制器 [audio.py](./presentation/audio.py) 拥有自动检测环境退避机制。
- 当未装载 `ursina` 库或无法开辟 3D 渲染窗口时，系统会自动启动 **Mock 占位符模式**，从而使单元测试及非图形服务器依然可以运行逻辑层。

---

## 🚀 启动与测试

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动系统级别测试 (非图形化控制台测试)
直接运行 `main.py` 将初始化 `GameController` 状态机，调用核心系统并加载关卡配置数据，以测试架构是否正常组装：

```bash
python main.py
```

### 3. 运行 3D 图形主游戏 (需要安装 Ursina 环境支持)
在完整游戏主循环整合完成后，通过将 `game_manager.py` 中的 `app.run()` 激活来唤醒 3D 视口。

---

## 📄 许可协议
本项目基于 MIT License 协议开源。
