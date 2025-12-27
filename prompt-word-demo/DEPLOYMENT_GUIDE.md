# GitHub Pages 部署与永久存储技术文档

## 项目概述

本项目实现了一个纯前端的 HTML 互动项目展示平台，支持：
- GitHub Pages 静态网站托管
- GitHub API 实现数据永久存储（所有用户共享）
- 用户可在线添加自定义 HTML 项目

**线上地址**: `https://alanttor.github.io/ai-game/`

---

## 技术架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        GitHub 仓库 (ai-game)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📁 programmin- prompt-word-demo/  ← 纯前端项目 ✅ 可完整运行    │
│  ├── index.html                    ← 导航页入口                  │
│  ├── *.html                        ← 各个项目页面                │
│  ├── favicon.svg                   ← 网站图标                    │
│  └── data/                                                      │
│      └── projects.json             ← 用户项目数据（GitHub API读写）│
│                                                                 │
│  📁 chinese_horror_game/           ← Flask后端 ⚠️ 仅静态文件可访问│
│  📁 Fanren-Attack on Titan/        ← Python项目 ⚠️ 无法运行      │
│  📁 zombie_world_war/              ← 全栈项目 ⚠️ 后端无法运行    │
│  📁 .github/workflows/             ← 部署配置                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## GitHub Pages vs Nginx 对比

| 对比项 | GitHub Pages | Nginx 服务器 |
|--------|-------------|--------------|
| **服务器** | GitHub 提供，无需管理 | 需要自己购买/维护服务器 |
| **费用** | 免费 | 服务器费用 + 域名费用 |
| **域名** | `xxx.github.io` 或自定义 | 完全自定义 |
| **HTTPS** | 自动提供 | 需要自己配置证书 |
| **带宽/流量** | 有限制（100GB/月） | 取决于服务器配置 |
| **部署方式** | Git push 自动部署 | 手动上传或配置 CI/CD |
| **后端支持** | ❌ 不支持 | ✅ 可配合后端 |
| **数据库** | ❌ 不支持 | ✅ 可安装任意数据库 |
| **适用场景** | 个人博客、文档、纯前端项目 | 企业网站、全栈应用 |

**本质区别**：GitHub Pages 只能托管静态文件（HTML/CSS/JS/图片），无法运行服务器端代码。

---

## 前后端项目部署方案

### 问题：GitHub Pages 不够用的情况

当项目包含以下内容时，GitHub Pages **无法满足需求**：

- ❌ Python/Node.js/Java 等后端代码
- ❌ 数据库（MySQL/MongoDB/Redis）
- ❌ 需要服务器端渲染（SSR）
- ❌ WebSocket 长连接
- ❌ 文件上传/处理
- ❌ 定时任务

### 解决方案对比

| 方案 | 费用 | 难度 | 适用场景 |
|------|------|------|----------|
| **Vercel** | 免费额度 | ⭐ | Node.js/Python 轻量后端 |
| **Railway** | 免费额度 | ⭐⭐ | 全栈应用 + 数据库 |
| **Render** | 免费额度 | ⭐⭐ | 全栈应用 + 数据库 |
| **Fly.io** | 免费额度 | ⭐⭐ | Docker 容器部署 |
| **云服务器** | 付费 | ⭐⭐⭐ | 完全控制，企业级应用 |

### 推荐方案：前后端分离部署

```
┌─────────────────┐     API 请求      ┌─────────────────┐
│   前端 (静态)    │ ───────────────→ │   后端 (动态)    │
│  GitHub Pages   │ ←─────────────── │  Vercel/Railway │
│  免费托管        │     JSON 响应     │  免费额度        │
└─────────────────┘                   └─────────────────┘
                                              │
                                              ▼
                                      ┌─────────────────┐
                                      │    数据库       │
                                      │ Supabase/PlanetScale │
                                      │    免费额度      │
                                      └─────────────────┘
```

### 具体部署步骤（以 Flask 项目为例）

#### 方案一：Vercel 部署 Python 后端

1. 在项目根目录创建 `vercel.json`：
```json
{
  "builds": [
    { "src": "app.py", "use": "@vercel/python" }
  ],
  "routes": [
    { "src": "/(.*)", "dest": "app.py" }
  ]
}
```

2. 创建 `requirements.txt` 列出依赖

3. 在 Vercel 网站导入 GitHub 仓库，自动部署

4. 获得后端地址：`https://your-project.vercel.app`

#### 方案二：Railway 部署（支持数据库）

1. 注册 [railway.app](https://railway.app)
2. 连接 GitHub 仓库
3. 添加 PostgreSQL/MySQL 数据库服务
4. 自动部署，获得后端地址

---

## 前端入口不是 index.html 的情况

### 问题场景

某些前端框架（Vue/React）构建后的入口可能是：
- `dist/index.html`
- 需要特定路由配置
- SPA 单页应用需要所有路由指向同一文件

### 解决方案

#### 1. 修改构建输出目录

在 `deploy.yml` 中指定正确的目录：

```yaml
- name: Upload artifact
  uses: actions/upload-pages-artifact@v3
  with:
    path: 'your-project/dist'  # 指向构建输出目录
```

#### 2. SPA 路由问题（404 处理）

GitHub Pages 不支持服务端路由重写，需要创建 `404.html`：

```html
<!-- 404.html -->
<!DOCTYPE html>
<html>
<head>
  <script>
    // 将所有 404 重定向到首页，由前端路由处理
    const path = window.location.pathname;
    window.location.href = '/?redirect=' + encodeURIComponent(path);
  </script>
</head>
</html>
```

#### 3. 使用 HashRouter（推荐）

对于 React/Vue SPA，使用 Hash 路由避免 404 问题：

```javascript
// React
import { HashRouter } from 'react-router-dom';

// Vue
const router = createRouter({
  history: createWebHashHistory(),
  routes: [...]
});
```

URL 格式变为：`https://xxx.github.io/app/#/about`

#### 4. 接口地址作为入口

如果"前端"实际上是一个 API 服务，那它**不适合** GitHub Pages，应该：

- 部署到 Vercel/Railway 等支持后端的平台
- 或者创建一个简单的 HTML 页面作为 API 文档/测试界面

---

## 数据存储限制

### GitHub Contents API 限制

| 限制项 | 数值 |
|--------|------|
| 单文件大小 | **1 MB** |
| API 请求频率 | 5000 次/小时（认证用户） |
| 仓库大小建议 | < 1 GB |

### 本项目的限制措施

- 单个用户项目 HTML 限制 **100 KB**
- 实时显示代码大小
- 超限时阻止保存并提示

### 大数据量解决方案

如果数据量超过 GitHub API 限制：

1. **Supabase**（免费 PostgreSQL）
2. **PlanetScale**（免费 MySQL）
3. **MongoDB Atlas**（免费 MongoDB）
4. **Firebase**（Google 提供，免费额度）

---

## 多仓库 GitHub Pages 原理

```
GitHub 账号: alanttor
│
├── 仓库: alanttor.github.io (特殊仓库名)
│   └── 内容部署到: https://alanttor.github.io/
│
├── 仓库: ai-game
│   └── 内容部署到: https://alanttor.github.io/ai-game/
│
├── 仓库: blog
│   └── 内容部署到: https://alanttor.github.io/blog/
│
└── 其他仓库...
```

**规则**：
- `用户名.github.io` 仓库 → 根域名
- 其他仓库 → `/仓库名/` 子路径

---

## 核心技术实现

### 1. GitHub Actions 自动部署

**文件**: `.github/workflows/deploy.yml`

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: ["main", "master"]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      # 关键：构建时注入 Token，避免在代码中暴露
      - name: Inject GitHub Token
        run: |
          sed -i "s/%%GITHUB_TOKEN%%/${{ secrets.PROJECT_TOKEN }}/g" "programmin- prompt-word-demo/index.html"
      
      - name: Setup Pages
        uses: actions/configure-pages@v4
      
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: '.'  # 部署整个仓库
      
      - name: Deploy to GitHub Pages
        uses: actions/deploy-pages@v4
```

### 2. Token 安全注入机制

**问题**: 前端代码需要 GitHub Token 才能写入数据，但 Token 不能直接写在代码里

**解决方案**:
1. 代码中使用占位符 `%%GITHUB_TOKEN%%`
2. Token 存储在 GitHub Secrets（`PROJECT_TOKEN`）
3. 构建时通过 `sed` 命令替换占位符为真实 Token
4. 部署后的网站包含真实 Token，但源代码仓库中没有

```javascript
// 源代码中（安全）
token: '%%GITHUB_TOKEN%%'

// 部署后的网站中（自动替换）
token: 'ghp_xxxxxxxxxxxx'
```

### 3. GitHub API 数据存储

**原理**: 使用 GitHub Contents API 直接读写仓库中的 JSON 文件

```javascript
// 读取数据
GET https://api.github.com/repos/{owner}/{repo}/contents/{path}

// 写入数据
PUT https://api.github.com/repos/{owner}/{repo}/contents/{path}
{
  "message": "更新项目数据",
  "content": "base64编码的JSON内容",
  "sha": "文件的SHA值（更新时必需）",
  "branch": "master"
}
```

---

## 配置步骤（供后续参考）

### 1. 创建 GitHub Token

1. GitHub → Settings → Developer settings → Personal access tokens → **Tokens (classic)**
2. Generate new token (classic)
3. 勾选 `repo` 权限
4. 生成并复制 Token（以 `ghp_` 开头）

### 2. 添加 Repository Secret

1. 仓库 → Settings → Secrets and variables → Actions
2. New repository secret
3. Name: `PROJECT_TOKEN`
4. Value: 粘贴 Token

### 3. 启用 GitHub Pages

1. 仓库 → Settings → Pages
2. Source: **GitHub Actions**
3. 等待 workflow 运行完成

### 4. 初始化数据文件

确保 `data/projects.json` 文件存在且内容为 `[]`

---

## 常见问题

### Q: 为什么社区项目在其他设备看不到？
A: 早期版本 HTML 内容存在 localStorage（浏览器本地），已修复为存储到 GitHub。

### Q: 为什么保存失败显示 403？
A: Token 权限不足，需要使用 Classic Token 并勾选 `repo` 权限。

### Q: 为什么 Python 项目无法运行？
A: GitHub Pages 只支持静态文件，后端代码需要部署到 Vercel/Railway 等平台。

### Q: 文件太大怎么办？
A: 单个项目限制 100KB，如需更大存储请使用外部数据库服务。

---

## 文件清单

```
ai-game/
├── index.html                      # 仓库首页（项目导航）
├── .github/workflows/deploy.yml    # 部署配置
│
├── programmin- prompt-word-demo/   # HTML 互动项目
│   ├── index.html                  # 导航页（含存储逻辑）
│   ├── *.html                      # 各个项目页面
│   ├── favicon.svg                 # 网站图标
│   ├── data/projects.json          # 用户项目数据
│   └── DEPLOYMENT_GUIDE.md         # 本文档
│
├── chinese_horror_game/            # Flask 项目（需后端）
├── Fanren-Attack on Titan/         # Python 项目（需本地运行）
└── zombie_world_war/               # 全栈项目（需后端）
```

---

## 更新日志

- **2025-12-27**: 
  - 初始部署，实现 GitHub Pages + GitHub API 存储方案
  - 修复社区项目 HTML 存储问题（localStorage → GitHub）
  - 添加文件大小限制（100KB）
  - 扩展部署范围到整个仓库
  - 补充前后端项目部署方案文档
