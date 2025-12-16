# 纸人归魂 - 中式恐怖文字冒险游戏

一款基于民国背景的中式恐怖文字冒险游戏，融合了传统民俗元素与现代恐怖叙事。

## 游戏简介

民国二十三年深秋，你收到父亲的求救信，信中提到老宅中的纸人"活了"。当你踏入陈家老宅，一段尘封六十年的冤魂复仇故事逐渐揭开...

## 技术栈

- 后端：Python Flask
- 前端：原生 HTML/CSS/JavaScript
- 无需数据库，使用 Session 存储游戏状态

## 快速开始

### 安装依赖

```bash
cd chinese_horror_game
pip install -r requirements.txt
```

### 运行游戏

```bash
python app.py
```

然后在浏览器中访问 `http://localhost:5000`

## 游戏特色

- **理智系统**：理智值会随着恐怖事件下降，过低会触发幻觉效果，归零则游戏结束
- **物品收集**：火折子、钥匙、朱砂等道具影响剧情走向
- **多结局设计**：6种不同结局，取决于你的选择
- **随机恐怖事件**：增加游戏的不可预测性
- **跳吓系统**：特定场景触发惊吓效果
- **氛围音效**：Web Audio API 生成的恐怖音效

## 项目结构

```
chinese_horror_game/
├── app.py              # Flask 主程序，包含核心场景
├── scenes_extra.py     # 额外场景定义
├── requirements.txt    # Python 依赖
├── static/
│   ├── css/style.css   # 游戏样式
│   ├── js/game.js      # 前端游戏逻辑
│   └── favicon.svg     # 网站图标
└── templates/
    └── index.html      # 游戏主页面
```

## 注意事项

- 本游戏包含恐怖元素，请在光线充足的环境下游玩
- 建议佩戴耳机以获得最佳体验
- 不建议心脏病患者或易受惊吓者游玩

## License

MIT License
