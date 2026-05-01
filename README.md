# 贪吃蛇游戏 (Snake Game)

A classic Snake game built with Python and Pygame, with cross-platform packaging support.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Pygame](https://img.shields.io/badge/Pygame-2.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 游戏操作

- **W / ↑** — 上
- **S / ↓** — 下
- **A / ←** — 左
- **D / →** — 右
- **P** — 暂停/继续
- **ESC** — 退出

## 本地运行

```bash
pip install -r requirements.txt
python snake.py
```

## 下载预编译版本

前往 [Releases](https://github.com/dearc/snake-game/releases) 页面下载：

- 🪟 Windows (.exe)
- 🍎 macOS (.app)
- 🐧 Linux (.AppImage)

## 构建

### Windows
```bash
pyinstaller --onefile --windowed snake.py
```

### macOS / Linux
```bash
pyinstaller --onefile snake.py
```

## 项目结构

```
snake_game/
├── snake.py          # 主游戏代码
├── requirements.txt  # 依赖
└── .github/
    └── workflows/
        └── build.yml # 跨平台构建
```
