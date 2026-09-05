#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build script for GUI version"""

import os
import sys
import time
import json
import subprocess
import shutil

VERSION = "1.3.1"
WEBSITE_URL = "https://shit.pub/s/developer/minecraft/client/MinecraftBotClient-MBC/MBC/"

README_GUI_ZH = """# Minecraft Bot Client (MBC) v{version} - GUI 版本

## 文件说明
- `MinecraftBotClient-gui.exe` - GUI 客户端，双击运行
- `config.json` - 配置文件
- `README.gui.zh.md` - 本说明文件
- `log/` - 日志文件夹（开启日志后自动创建）

## GUI 版本特点

✨ **主要优点：**
- 🖥️ 直观的图形界面
- ⚙️ 实时配置调整
- 📊 彩色输出控制台
- 💬 内置聊天和命令输入
- 🔘 一键连接/断开
- 📝 自动消息列表管理

## 快速开始

1. 双击 `MinecraftBotClient-gui.exe` 启动
2. 填写服务器地址和版本
3. 点击 "Connect" 按钮连接
4. 在聊天框中输入消息
5. 使用各个功能按钮

## 配置说明

```json
{{
  "version": "{version}",
  "username": "",
  "server_address": "localhost:25565",
  "minecraft_version": "1.8.9",
  "language": "zh",
  "fast_start": false,
  "log_enabled": false,
  "spam_enabled": false,
  "spam_rate": 1.0,
  "spam_messages": ["Hello!", "Anyone there?", "GG"],
  "command_autocomplete": true,
  "auto_eat": true,
  "auto_eat_health_threshold": 10,
  "auto_walk": false,
  "auto_walk_waypoints": [],
  "stop_walk_on_damage": true,
  "proximity_alerts": true,
  "proximity_distance": 5.0,
  "human_actions": true,
  "human_action_interval_min": 2.0,
  "human_action_interval_max": 7.0
}}
```

### 配置项说明

| 配置项 | 说明 |
|--------|------|
| username | 玩家名，留空自动随机生成 |
| server_address | 服务器地址，支持 SRV 域名 |
| minecraft_version | 服务器版本 (1.8 - 1.21) |
| fast_start | 快速启动，跳过版本验证 |
| log_enabled | 启用日志记录 |
| spam_enabled | 启用自动发送消息 |
| spam_rate | 消息发送速率 (消息/秒) |
| spam_messages | 要发送的消息列表 |
| auto_eat | 受伤自动吃食物 |
| auto_walk | 自动走路 |
| proximity_alerts | 周围玩家提示 |
| human_actions | 模拟人类动作 |

## 命令说明

### 客户端命令 (`.` 前缀，不发送给服务器)

- `.help` - 显示帮助
- `.esc` - 离开服务器
- `.exit` - 退出客户端
- `.connect` - 重新连接
- `.respawn` - 重生
- `.log on/off` - 开关日志
- `.spam on/off` - 开关自动发送
- `.spam add <消息>` - 添加消息
- `.spam list` - 列出消息
- `.walk on/off` - 开关自动走路
- `.walk add <x,y,z>` - 添加路点
- `.eat on/off` - 开关自动吃食物
- `.config <key> <value>` - 修改配置

### 服务器命令 (`/` 前缀)

- `/list` - 列出玩家
- `/msg <玩家> <内容>` - 发送私信
- 其他服务器原生命令

### 普通文本

直接作为聊天消息发送

## 支持的版本

任意 1.8 - 1.21 版本

## 重要说明

- 本客户端为离线模式，请在 `online-mode=false` (破解/离线) 服务器使用
- 版本验证地址: https://shit.pub/s/developer/minecraft/client/MinecraftBotClient-MBC/verify/txt.txt
- 公告栏地址: https://shit.pub/s/developer/minecraft/client/MinecraftBotClient-MBC/announcement.txt
- 帮助网站: {website}

## 故障排除

### 无法连接到服务器
- 检查服务器地址是否正确
- 检查服务器是否在线
- 确保 `online-mode=false`
- 查看日志文件获取更多信息

### GUI 无法启动
- 确保已安装 PyQt5
- 尝试删除 config.json 让程序重新生成
- 检查 Python 版本 (需要 3.8+)

## 许可证

GPL-3.0 License
"""

README_GUI_EN = """# Minecraft Bot Client (MBC) v{version} - GUI Version

## Files
- `MinecraftBotClient-gui.exe` - GUI Client, double-click to run
- `config.json` - Configuration file
- `README.gui.en.md` - This readme
- `log/` - Log folder (created automatically when logging is enabled)

## GUI Version Features

✨ **Main Advantages:**
- 🖥️ Intuitive graphical interface
- ⚙️ Real-time configuration adjustments
- 📊 Colored output console
- 💬 Built-in chat and command input
- 🔘 One-click connect/disconnect
- 📝 Automatic spam message management

## Quick Start

1. Double-click `MinecraftBotClient-gui.exe` to launch
2. Fill in the server address and version
3. Click the "Connect" button
4. Type messages in the chat box
5. Use the feature buttons

## Configuration

```json
{{
  "version": "{version}",
  "username": "",
  "server_address": "localhost:25565",
  "minecraft_version": "1.8.9",
  "language": "en",
  "fast_start": false,
  "log_enabled": false,
  "spam_enabled": false,
  "spam_rate": 1.0,
  "spam_messages": ["Hello!", "Anyone there?", "GG"],
  "command_autocomplete": true,
  "auto_eat": true,
  "auto_eat_health_threshold": 10,
  "auto_walk": false,
  "auto_walk_waypoints": [],
  "stop_walk_on_damage": true,
  "proximity_alerts": true,
  "proximity_distance": 5.0,
  "human_actions": true,
  "human_action_interval_min": 2.0,
  "human_action_interval_max": 7.0
}}
```

### Configuration Options

| Option | Description |
|--------|-------------|
| username | Player name, leave empty for random |
| server_address | Server address, supports SRV domains |
| minecraft_version | Server version (1.8 - 1.21) |
| fast_start | Skip version verification |
| log_enabled | Enable logging |
| spam_enabled | Enable auto-spam |
| spam_rate | Message send rate (msg/s) |
| spam_messages | List of spam messages |
| auto_eat | Auto-eat when damaged |
| auto_walk | Enable auto-walk |
| proximity_alerts | Notify when players are nearby |
| human_actions | Simulate human-like actions |

## Commands

### Client Commands (`.` prefix, not sent to server)

- `.help` - Show help
- `.esc` - Leave server
- `.exit` - Exit client
- `.connect` - Reconnect
- `.respawn` - Respawn
- `.log on/off` - Toggle logging
- `.spam on/off` - Toggle auto-spam
- `.spam add <message>` - Add message
- `.spam list` - List messages
- `.walk on/off` - Toggle auto-walk
- `.walk add <x,y,z>` - Add waypoint
- `.eat on/off` - Toggle auto-eat
- `.config <key> <value>` - Modify config

### Server Commands (`/` prefix)

- `/list` - List players
- `/msg <player> <text>` - Send private message
- Other native server commands

### Plain Text

Sent as a chat message directly

## Supported Versions

Any version between 1.8 and 1.21

## Important Notes

- This client runs in offline mode. Use it on servers with `online-mode=false`
- Version check URL: https://shit.pub/s/developer/minecraft/client/MinecraftBotClient-MBC/verify/txt.txt
- Announcement URL: https://shit.pub/s/developer/minecraft/client/MinecraftBotClient-MBC/announcement.txt
- Help website: {website}

## Troubleshooting

### Cannot connect to server
- Check if the server address is correct
- Verify the server is online
- Ensure `online-mode=false`
- Check the log folder for details

### GUI won't start
- Make sure PyQt5 is installed
- Try deleting config.json to regenerate it
- Check Python version (requires 3.8+)

## License

GPL-3.0 License
"""


def remove_dir(path):
    if not os.path.exists(path):
        return
    for attempt in range(5):
        try:
            shutil.rmtree(path)
            return
        except OSError:
            time.sleep(1)
    shutil.rmtree(path, ignore_errors=True)


def build_gui(name, language, output_dir):
    print(f"\n=== Building {name} (language={language}) ===")

    remove_dir("build")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--clean",
        "-y",
        "--hidden-import=dns.resolver",
        "--hidden-import=dns.name",
        "--hidden-import=dns.rdataclass",
        "--hidden-import=dns.rdatatype",
        "--hidden-import=dns.resolver.answer",
        "--hidden-import=dns.exception",
        "--hidden-import=PyQt5.QtCore",
        "--hidden-import=PyQt5.QtGui",
        "--hidden-import=PyQt5.QtWidgets",
        "--collect-all=dns",
        f"--name={name}",
        "main_gui.py"
    ]

    if os.path.exists("src/assets/icon.ico"):
        cmd.insert(4, "--icon=src/assets/icon.ico")

    subprocess.check_call(cmd)

    src_exe = os.path.join("dist", f"{name}.exe")
    if not os.path.exists(src_exe):
        print(f"FAIL: {name}")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)
    dst_exe = os.path.join(output_dir, f"{name}.exe")
    shutil.copy2(src_exe, dst_exe)
    print(f"OK: {dst_exe}")

    config = {
        "version": VERSION,
        "username": "",
        "server_address": "localhost:25565",
        "minecraft_version": "1.8.9",
        "language": language,
        "fast_start": False,
        "log_enabled": False,
        "spam_enabled": False,
        "spam_rate": 1.0,
        "spam_messages": ["Hello!", "Anyone there?", "GG"],
        "command_autocomplete": True,
        "auto_eat": True,
        "auto_eat_health_threshold": 10,
        "auto_walk": False,
        "auto_walk_waypoints": [],
        "stop_walk_on_damage": True,
        "proximity_alerts": True,
        "proximity_distance": 5.0,
        "human_actions": True,
        "human_action_interval_min": 2.0,
        "human_action_interval_max": 7.0,
    }
    config_path = os.path.join(output_dir, "config.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print(f"OK: {config_path}")

    readme_template = README_GUI_ZH if language == "zh" else README_GUI_EN
    readme_text = readme_template.format(version=VERSION, website=WEBSITE_URL)
    readme_path = os.path.join(output_dir, f"README.gui.{language}.md")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_text)
    print(f"OK: {readme_path}")


def main():
    print("Installing PyInstaller if needed...")
    if not shutil.which('pyinstaller'):
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    print("Installing PyQt5 if needed...")
    if shutil.which('pip'):
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt5>=5.15.7"])

    remove_dir("build")
    remove_dir("dist")

    version_root = os.path.join("releases", VERSION)
    gui_dir = os.path.join(version_root, "gui")

    build_gui("MinecraftBotClient-gui", "zh", gui_dir)

    print(f"\n=== Done: releases/{VERSION}/gui/ ===")
    print(f"  MinecraftBotClient-gui.exe")
    print(f"  config.json")
    print(f"  README.gui.zh.md")


if __name__ == "__main__":
    main()
