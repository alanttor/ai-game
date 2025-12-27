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
│  📁 programmin- prompt-word-demo/  ← 被部署到 GitHub Pages      │
│  ├── index.html                    ← 导航页入口                  │
│  ├── *.html                        ← 各个项目页面                │
│  ├── favicon.svg                   ← 网站图标                    │
│  └── data/                                                      │
│      └── projects.json             ← 用户项目数据（GitHub API读写）│
│                                                                 │
│  📁 chinese_horror_game/           ← 未部署                      │
│  📁 Fanren-Attack on Titan/        ← 未部署                      │
│  📁 zombie_world_war/              ← 未部署                      │
│  📁 .github/workflows/             ← 部署配置                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 部署方式说明

### 当前部署范围

| 文件夹 | 是否部署 | 说明 |
|--------|---------|------|
| `programmin- prompt-word-demo/` | ✅ 是 | 通过 workflow 指定部署 |
| `chinese_horror_game/` | ❌ 否 | 未包含在部署路径中 |
| `Fanren-Attack on Titan/` | ❌ 否 | 未包含在部署路径中 |
| `zombie_world_war/` | ❌ 否 | 未包含在部署路径中 |

### 部署类型

**✅ 仅部署了前端（纯静态网站）**

- 没有后端服务器
- 没有数据库服务
- 所有逻辑在浏览器端运行
- 数据存储通过 GitHub API 直接操作仓库文件

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
          path: 'programmin- prompt-word-demo'  # 只部署这个文件夹
      
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

**关键代码** (`index.html`):

```javascript
const GITHUB_CONFIG = {
    owner: 'alanttor',
    repo: 'ai-game',
    path: 'programmin- prompt-word-demo/data/projects.json',
    token: '%%GITHUB_TOKEN%%'  // 构建时替换
};

const Storage = {
    fileSha: null,
    
    async getProjects() {
        const res = await fetch(`https://api.github.com/repos/.../contents/...`, {
            headers: { 'Authorization': `token ${GITHUB_CONFIG.token}` }
        });
        const data = await res.json();
        this.fileSha = data.sha;  // 保存SHA用于后续更新
        return JSON.parse(atob(data.content));
    },
    
    async saveProjects(projects) {
        await fetch(`https://api.github.com/repos/.../contents/...`, {
            method: 'PUT',
            headers: { 'Authorization': `token ${GITHUB_CONFIG.token}` },
            body: JSON.stringify({
                message: '更新项目数据',
                content: btoa(JSON.stringify(projects)),
                sha: this.fileSha,  // 必须提供当前文件的SHA
                branch: 'master'
            })
        });
    }
};
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

## 扩展部署其他文件夹

如果想同时部署 `chinese_horror_game` 等其他项目，有两种方式：

### 方式一：修改部署路径为根目录

```yaml
# .github/workflows/deploy.yml
- name: Upload artifact
  uses: actions/upload-pages-artifact@v3
  with:
    path: '.'  # 部署整个仓库
```

### 方式二：创建多个部署 workflow

为每个项目创建独立的 GitHub Pages 仓库

---

## 注意事项

1. **Token 安全**: Classic Token 暴露后应立即删除重新生成
2. **API 限制**: GitHub API 有速率限制（认证用户 5000次/小时）
3. **文件大小**: GitHub Contents API 单文件限制 1MB
4. **并发写入**: 多用户同时写入可能产生冲突（SHA 不匹配）

---

## 文件清单

```
programmin- prompt-word-demo/
├── index.html                 # 导航页（含存储逻辑）
├── hexagon-bouncing-ball.html # 六边形弹跳小球
├── chimney-demolition.html    # 砖块烟囱爆破
├── solar-system.html          # 太阳系模拟器
├── particle-vortex.html       # 粒子漩涡
├── corporate-website.html     # 企业官网模板
├── weather-cards.html         # 动画天气卡片
├── typing-game.html           # 打字练习游戏
├── quantum-simulator.html     # 量子波函数模拟器
├── favicon.svg                # 网站图标
├── data/
│   └── projects.json          # 用户项目数据
└── DEPLOYMENT_GUIDE.md        # 本文档
```

---

## 更新日志

- **2025-12-27**: 初始部署，实现 GitHub Pages + GitHub API 存储方案
