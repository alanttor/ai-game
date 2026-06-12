# 纸人归魂 - 中式恐怖文字冒险游戏 (Chinese Horror Game)

一款基于 Flask 后端与原生 JavaScript/CSS 驱动的民国背景中式恐怖文字冒险游戏。游戏融合了传统民俗禁忌与现代声画 jumpscare（跳吓）互动系统。

---

## 👻 游戏简介

*民国二十三年深秋，你收到父亲的求救信，信中提到老宅中的纸人“活了”。当你踏入陈家老宅，一段尘封六十年的冤魂复仇故事逐渐揭开...*

---

## 🛠️ 技术栈

- **后端开发**: Python 3.8+, Flask 3.x
- **状态存储**: Flask Session (基于加密 Cookie，免数据库持久化)
- **前端页面**: 原生 HTML5, CSS3, JavaScript (ES6)
- **声效引擎**: Web Audio API (基于 OscillatorNode 动态波形合成，零音频资源加载依赖)

---

## 📂 项目结构

```
chinese_horror_game/
├── app.py              # Flask 主程序（场景有向图路由、随机事件状态机与 Session 逻辑）
├── scenes_extra.py     # 额外场景定义 (解耦扩展剧情)
├── requirements.txt    # 项目依赖 (flask, flask-cors)
├── static/             # 静态资源层
│   ├── css/
│   │   └── style.css   # 迷雾渐变、抖动、屏幕扭曲、低理智视觉特效定义
│   ├── js/
│   │   └── game.js      # 前端状态渲染、Web Audio 合成音轨与键盘按键交互绑定
│   └── favicon.svg     # 网站图标
└── templates/
    └── index.html      # 主页面渲染模版 (支持打字机效果及动态 choices 挂载)
```

---

## ⚙️ 核心系统实现逻辑

### 1. 理智系统 (Sanity System)
玩家拥有初始为 100 的理智值。
- 做出危险选择（如回头、强行开门）会导致理智下降。
- **动态干扰**: 理智低于 50 会触发屏幕泛红闪烁；理智低于 30 将大幅提高随机恐怖事件的发动概率，文字产生物理抖动；理智归 0 时直接触发死亡结局。

### 2. 算法动态合成音效
前端 [game.js](./static/js/game.js#L247) 基于 HTML5 **Web Audio API**，免除了加载 MP3 等静态资源的需求。
- **心跳过速效果**: 使用正弦波（`sine`）在低频区间每隔 500ms 产生一次指数衰减的脉冲。
- **女鬼惨叫**: 采用锯齿波（`sawtooth`）高频振荡，并动态使用 `exponentialRampToValueAtTime` 产生声学刺耳感。

### 3. 多分支与有向图剧情跳转
场景跳转通过单向依赖图（Directed Acyclic Graph）设计。在 [app.py](./app.py) 中定义，前端通过 POST 请求发送玩家选项的 index。后端拦截校验：
- **require_item / require_flag**: 校验会话状态中是否存在特定物品（如火折子、钥匙）或是否满足特定剧情分支前置，从而动态激活/禁用选择按钮。

---

## 🚀 快速启动

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动 Flask 后端

```bash
python app.py
```

### 3. 访问游戏
在浏览器中打开 `http://127.0.0.1:5000` 即可开始游玩。

---

## ⚠️ 游玩须知
- 游戏包含突发性视听刺激（Jumpscare）及恐怖心理压迫。
- 建议佩戴耳机，在暗光环境下游玩以获取最佳氛围。
- 心脏疾病患者及易惊吓者请酌情游玩。

---

## 📄 许可证
本项目采用 MIT 许可证授权。
