# Zombie World War - Frontend Client

3D 第一人称射击游戏《僵尸世界大战》的前端 WebGL 客户端。基于 Vue 3 + TypeScript 与 3D 渲染引擎 Three.js 独立构建，展示了前端高级 3D 游戏开发的核心设计。

---

## 🛠️ 技术栈

- **开发框架**: Vue 3 (Composition API)
- **编译/构建**: Vite, TypeScript
- **3D 引擎**: Three.js (WebGL)
- **状态管理**: Pinia
- **网络通信**: Axios
- **单元测试**: Vitest, Vue Test Utils

---

## 📂 核心引擎设计

前端 3D 逻辑位于 `src/engine` 目录下，按系统精细拆分：

- **渲染主循环 (`GameEngine.ts`)**: 
  - 实现双更新回路。采用固定步长物理更新（`fixedUpdate`）与可变步长画面插值渲染更新（`update` & `render`），保证动作计算不依赖于屏幕刷新率。
- **场景与光源管理 (`SceneManager.ts`)**: 
  - 动态光影追踪。手电筒及环境光源位置将随着玩家的绝对坐标进行实时平滑插值（Lerp），渲染高性能迷雾与阴影特效。
- **角色物理与位移控制 (`Player.ts` & `PlayerPhysics.ts`)**: 
  - 自研简单的 Box 碰撞体检测。支持重力坠落、起跳曲线计算以及贴合不规则障碍物的摩擦滑动摩擦物理运算。
- **第一人称视口跟随 (`FirstPersonCamera.ts`)**: 
  - 接管 `PointerLockControls` 并配合鼠标输入偏移计算俯仰角（Pitch）与偏航角（Yaw），做出了物理级的镜头微震与消抖。
- **枪械射击与光线投影 (`weapons/`)**: 
  - 运用 Three.js 的 `Raycaster` 空间光线投射，以镜头中心点法线方向在三维空间中进行碰撞穿透求交，实时计算开枪弹痕位置与僵尸受击部位。
- **渐进式画质降级优化 (`performance/`)**: 
  - `LODManager` 会根据玩家与模型的距离自动切换三维物体的骨骼复杂度，且由 `PerformanceMonitor` 实时监控 FPS，若发生连续掉帧将自动调低渲染画质等级。

---

## 🚀 本地运行

### 1. 运行准备
确保您的计算机上已安装 **Node.js 18+**。

### 2. 步骤
```bash
# 1. 安装项目所有依赖
npm install

# 2. 启动本地开发服务 (支持 HMR 热更新)
npm run dev

# 3. 构建高兼容性 Web 静态包
npm run build

# 4. 执行单元与集成测试
npm run test
```

### 3. API 连接配置
前端接口的基准路径（Base URL）在 `src/api/config.ts` 或 `vite.config.ts` 的代理中定义，默认反向代理至后端的 `http://localhost:8080` 服务。

---

## 📄 License
MIT License.
