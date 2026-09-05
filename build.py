import os
import sys
import time
import json
import subprocess
import shutil

VERSION = "1.3.1"
WEBSITE_URL = "https://shit.pub/s/developer/minecraft/client/MinecraftBotClient-MBC/MBC/"

README_ZH = """# Minecraft Bot Client (MBC) v{version} - 中文版

## 文件说明
- `MinecraftBotClient-zh.exe` - 中文客户端，双击运行
- `config.zh.json` - 配置文件
- `README.zh.md` - 本说明文件
- `log/` - 日志文件夹（开启日志后自动创建）

## 配置文件 (config.zh.json)
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
- `username`: 玩家名，留空自动随机生成
- `server_address`: 服务器地址，支持 SRV 域名（直接填域名即可，如 `mc.example.com`）
- `minecraft_version`: 服务器版本，支持 1.8 - 26.2 区间内任意版本
- `fast_start`: 快速启动，跳过版本查验与公告栏，降低资源占用
- `command_autocomplete`: 指令补全开关（输入 `.` 或 `/` 自动灰色预览）
- `auto_eat` / `auto_eat_health_threshold`: 受伤自动吃食物开关与血量阈值
- `auto_walk` / `auto_walk_waypoints`: 自动不规则走路与自定义路点
- `stop_walk_on_damage`: 受伤/死亡自动停止走路
- `proximity_alerts` / `proximity_distance`: 周围玩家靠近提示与距离
- `human_actions`: 模拟人类转头/出拳（随机延迟与轨迹，绕过常规反作弊）

## 指令说明
进入服务器后，`.` 开头为 MBC 客户端指令（不会发给服务器，旧版 `//` 仍兼容）：
- `.help` - 查看 MBC 客户端命令并打开帮助网站
- `.esc` - 离开服务器但不退出客户端
- `.connect` - 连接 / 重新连接服务器
- `.exit` - 断开并退出客户端
- `.respawn` - 死亡后发送重生包
- `.log on` / `.log off` - 开关日志（写入 log 文件夹，每次运行一个 .log 文件，含时间戳）
- `.spam on` / `.spam off` - 开关自动垃圾邮件
- `.spam rate <每秒条数>` - 设置发送速率
- `.spam add <消息>` / `.spam remove <索引>` / `.spam list` / `.spam clear` / `.spam status`
- `.walk start` / `.walk stop` - 开始/停止自动走路
- `.walk add <x,y,z>` - 添加自定义路点（相对坐标，逗号分隔）
- `.walk list` / `.walk clear` - 查看/清空路点
- `.eat on` / `.eat off` - 受伤自动吃食物开关
- `.config <key> [val]` - 查看/修改任意配置项（例：`.config fast_start true`）
- `/命令` - 发送服务器命令（如 `/list`、`/msg 玩家 内容`）
- 普通文本 - 作为聊天消息发送

## 指令补全（类原版）
- 输入 `.` 或 `/` 后自动以灰色文字预览指令
- `Tab` 补全预览内容，重复按 Tab 循环切换
- `↑` / `↓` 方向键或鼠标滚轮切换建议
- `Enter` 发送，`Esc` 清空当前输入，`↑` 还可回溯历史指令

## 说明
- 本客户端为离线模式，请在 `online-mode=false`（破解/离线）服务器使用
- 版本查验地址: https://shit.pub/s/developer/minecraft/client/MinecraftBotClient-MBC/verify/txt.txt
- 公告栏地址: https://shit.pub/s/developer/minecraft/client/MinecraftBotClient-MBC/announcement.txt
- 帮助网站: {website}
"""

README_EN = """# Minecraft Bot Client (MBC) v{version} - English

## Files
- `MinecraftBotClient-en.exe` - English client, double-click to run
- `config.en.json` - Configuration file
- `README.en.md` - This readme
- `log/` - Log folder (created automatically when logging is enabled)

## Configuration (config.en.json)
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
- `username`: Player name, leave empty for a random one
- `server_address`: Server address, SRV record domains supported (just use the domain, e.g. `mc.example.com`)
- `minecraft_version`: Server version, any version between 1.8 - 26.2 is supported
- `fast_start`: Skip version/announcement checks and reduce resource usage
- `command_autocomplete`: Toggle command autocomplete (grey preview when typing `.` or `/`)
- `auto_eat` / `auto_eat_health_threshold`: Auto-eat on damage toggle and health threshold
- `auto_walk` / `auto_walk_waypoints`: Random auto-walk and custom waypoints
- `stop_walk_on_damage`: Stop walking automatically on damage/death
- `proximity_alerts` / `proximity_distance`: Nearby player alerts and distance
- `human_actions`: Human-like head turning / arm swinging with random delays and trajectories

## Commands
After joining a server, lines starting with `.` are MBC client commands (not sent to the server; legacy `//` still works):
- `.help` - Show MBC client commands and open the help website
- `.esc` - Leave the server without closing the client
- `.connect` - Connect / reconnect to the server
- `.exit` - Disconnect and close the client
- `.respawn` - Send a respawn packet after dying
- `.log on` / `.log off` - Toggle logging (one timestamped .log file per session in the log folder)
- `.spam on` / `.spam off` - Toggle auto-spam
- `.spam rate <n>` - Set spam rate (msg/s)
- `.spam add <msg>` / `.spam remove <i>` / `.spam list` / `.spam clear` / `.spam status`
- `.walk start` / `.walk stop` - Start/stop auto-walk
- `.walk add <x,y,z>` - Add a custom waypoint (relative coordinates, comma separated)
- `.walk list` / `.walk clear` - List/clear waypoints
- `.eat on` / `.eat off` - Toggle auto-eat on damage
- `.config <key> [val]` - View or modify any config key (ex: `.config fast_start true`)
- `/command` - Send a server command (e.g. `/list`, `/msg player text`)
- Plain text - Send as a chat message

## Vanilla-style Autocomplete
- Type `.` or `/` to see a grey inline preview of the command
- `Tab` accepts the preview; press Tab repeatedly to cycle suggestions
- `↑` / `↓` arrow keys or the mouse wheel cycle suggestions
- `Enter` sends, `Esc` clears the input, `↑` also browses command history

## Notes
- This client runs in offline mode. Use it on servers with `online-mode=false`
- Version check URL: https://shit.pub/s/developer/minecraft/client/MinecraftBotClient-MBC/verify/txt.txt
- Announcement URL: https://shit.pub/s/developer/minecraft/client/MinecraftBotClient-MBC/announcement.txt
- Help website: {website}
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


def build_one(name, language, output_dir):
    print(f"\n=== Building {name} (language={language}) ===")

    remove_dir("build")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--console",
        "--clean",
        "-y",
        "--hidden-import=dns.resolver",
        "--hidden-import=dns.name",
        "--hidden-import=dns.rdataclass",
        "--hidden-import=dns.rdatatype",
        "--hidden-import=dns.resolver.answer",
        "--hidden-import=dns.exception",
        "--collect-all=dns",
        f"--name={name}",
        "main.py"
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
    config_path = os.path.join(output_dir, f"config.{language}.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print(f"OK: {config_path}")

    readme_template = README_ZH if language == "zh" else README_EN
    readme_text = readme_template.format(version=VERSION, website=WEBSITE_URL)
    readme_path = os.path.join(output_dir, f"README.{language}.md")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_text)
    print(f"OK: {readme_path}")


def main():
    if not shutil.which('pyinstaller'):
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    remove_dir("build")
    remove_dir("dist")

    version_root = os.path.join("releases", VERSION)
    zh_dir = os.path.join(version_root, "zh")
    en_dir = os.path.join(version_root, "en")

    build_one("MinecraftBotClient-zh", "zh", zh_dir)
    build_one("MinecraftBotClient-en", "en", en_dir)

    print(f"\n=== Done: releases/{VERSION}/ ===")
    print(f"  zh/:  MinecraftBotClient-zh.exe + config.zh.json + README.zh.md")
    print(f"  en/:  MinecraftBotClient-en.exe + config.en.json + README.en.md")


if __name__ == "__main__":
    main()
