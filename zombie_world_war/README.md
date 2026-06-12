# 僵尸世界大战 (Zombie World War) - 3D 联机射击游戏

一款基于前后端分离架构的 3D 第一人称射击（FPS）网络游戏。前端使用 Vue 3 + TypeScript 配合 Three.js 引擎实现 3D 物理与交互；后端基于 Spring Boot 3 提供安全的 JWT 认证、玩家存档持久化以及全球排行榜功能。

---

## 🏗️ 架构与技术栈

项目由两个子工程组成，采用前后端分离的方式协同运行：

```
zombie_world_war/
├── frontend/                  # 前端 3D 游戏客户端
│   ├── 技术栈: Vue 3, TypeScript, Three.js, Pinia, Axios, Vite
│   └── 提供 3D 场景渲染、第一人称视角控制器、僵尸 AI 寻路、空间音效及本地碰撞检测。
└── backend/                   # 后端 Web API 服务端
    ├── 技术栈: Java 17, Spring Boot 3, Spring Security, JWT, MySQL / H2, Hibernate (JPA)
    └── 提供用户注册登录验证、游戏进度云存档读写、实时积分排行榜同步。
```

---

## 📂 项目模块结构

```
zombie_world_war/
├── backend/                   # 后端 Spring Boot 源码
│   ├── src/main/java/com/zombieworldwar/
│   │   ├── config/            # 跨域 CORS 与 Security 拦截器配置
│   │   ├── controller/        # Auth、Game 保存、Leaderboard API 控制器
│   │   ├── entity/            # User、SaveState、Score 数据库实体
│   │   ├── repository/        # JPA 数据访问持久层
│   │   ├── security/          # JWT 令牌解析、加解密与用户上下上下文过滤
│   │   └── service/           # 积分计算与游戏存档版本控制业务逻辑
│   └── pom.xml                # 后端依赖管理 (Spring Boot Starter)
│
└── frontend/                  # 前端 Vue 3 + Three.js 源码
    ├── src/
    │   ├── engine/            # 核心 3D 物理与逻辑渲染引擎
    │   │   ├── GameEngine.ts       # 核心循环控制器 (Timestep Loop & RequestAnimationFrame)
    │   │   ├── SceneManager.ts     # 3D 灯光、天空盒、物体销毁与网格管理
    │   │   ├── PlayerPhysics.ts    # 玩家重力、惯性、障碍物边缘碰撞检测
    │   │   ├── FirstPersonCamera.ts# 第一人称相机跟随与视角消抖
    │   │   ├── zombies/            # 僵尸状态机（游荡、警戒、撕咬玩家）
    │   │   ├── weapons/            # 枪械机制（射击射线检测、弹夹管理、重新装填）
    │   │   └── performance/        # LOD 降级和对象池性能优化监控
    │   ├── views/             # 玩家注册、选枪、商城与排行榜的 Vue 组件面页
    │   ├── App.vue            # 前端入口组件
    │   └── main.ts            # 前端挂载与 Pinia 状态管理库初始化
    └── package.json           # 前端依赖配置
```

---

## 🚀 部署与运行

### 1. 运行后端服务 (Java Spring Boot)
请确保已安装 JDK 17 及 Maven，并启动本地 MySQL。

1. **创建数据库**:
   ```sql
   CREATE DATABASE zombie_world_war CHARACTER SET utf8mb4;
   ```
2. **修改配置文件**:
   在 `backend/src/main/resources/application.yml` 中配置您的 MySQL 连接用户名与密码，或设置环境变量：
   ```bash
   export DB_USERNAME=root
   export DB_PASSWORD=yourpassword
   export JWT_SECRET=your-minimum-32-characters-jwt-secret-key-string
   ```
3. **编译并启动**:
   ```bash
   cd backend
   mvn clean package
   mvn spring-boot:run
   ```
   后端将在 `http://localhost:8080` 启动。

### 2. 运行前端客户端 (Vite + Vue 3)
请确保已安装 Node.js 18+ 环境。

1. **安装依赖**:
   ```bash
   cd frontend
   npm install
   ```
2. **开发模式运行**:
   ```bash
   npm run dev
   ```
   前端将在 `http://localhost:5173` 启动，在浏览器中打开即可开始游玩。

---

## 📄 许可协议
本仓库基于 MIT License 协议开源。
