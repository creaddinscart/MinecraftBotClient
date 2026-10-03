import os
import sys
import time
import json
import shutil
import hashlib
import zipfile
import subprocess

VERSION = "2.1.0"
WEBSITE_URL = "https://shit.pub/s/developer/minecraft/client/MinecraftBotClient-MBC/MBC/"

if os.name == 'nt':
    PLATFORM = "windows"
elif sys.platform == 'darwin':
    PLATFORM = "macos"
else:
    PLATFORM = "linux"

BINARY_EXT = ".exe" if PLATFORM == "windows" else ""
PLATFORM_LABEL = {"windows": "Windows", "macos": "macOS", "linux": "Linux"}[PLATFORM]

RUN_HINTS = {
    "zh": {
        "windows": "双击 `{binary}` 运行",
        "macos": "首次运行前执行 `chmod +x {binary}`，然后运行 `./{binary}`",
        "linux": "首次运行前执行 `chmod +x {binary}`，然后运行 `./{binary}`",
    },
    "en": {
        "windows": "Double-click `{binary}`",
        "macos": "Run `chmod +x {binary}` once, then `./{binary}`",
        "linux": "Run `chmod +x {binary}` once, then `./{binary}`",
    },
}

PLATFORM_NOTES = {
    "zh": {
        "windows": "本版本为 Windows 单文件客户端，无需安装 Python。",
        "macos": "本版本为 macOS 单文件客户端，无需安装 Python。若被 Gatekeeper 拦截，请右键选择“打开”，或执行 `xattr -d com.apple.quarantine {binary}` 后重试。",
        "linux": "本版本为 Linux 单文件客户端，无需安装 Python。",
    },
    "en": {
        "windows": "This is the Windows single-file client. No Python installation is required.",
        "macos": "This is the macOS single-file client. No Python installation is required. If Gatekeeper blocks it, right-click and choose Open, or run `xattr -d com.apple.quarantine {binary}` before launching.",
        "linux": "This is the Linux single-file client. No Python installation is required.",
    },
}

README_ZH = """# Minecraft Bot Client (MBC) v{version} - 中文版

## 文件说明
- `{binary}` - 中文客户端，{run}
- `config.zh.json` - 配置文件
- `README.zh.md` - 本说明文件
- `log/` - 日志文件夹（开启日志后自动创建）

{note}

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
- `multi_bot_enabled` / `bot_count`: 多机器人开关与数量（可填 20、100 等），随机用户名批量进服
- `bot_name_prefix` / `bot_name_digits`: 随机用户名前缀与随机数字位数
- `bot_join_delay`: 机器人之间的连接间隔秒数（避免瞬间大量连接）
- `bot_auth_enabled` / `bot_auth_mode`: 自动登录开关与模式（`register`、`login` 或 `both`）
- `bot_auth_password`: 自动登录指令中使用的密码
- `bot_auth_delay`: 进服后等待多少秒再发送登录指令
- `bot_auth_register_command` / `bot_auth_login_command`: 指令模板，`{{password}}` 会替换为你的密码

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

## 多机器人模式
将 `multi_bot_enabled` 设为 `true` 并设置 `bot_count`。每个机器人使用随机用户名进服；开启 `bot_auth_enabled` 后，会在进服后自动发送 `/register` 或 `/login`（使用 `bot_auth_password`）。控制台指令：
- `.status` - 查看当前已连接的机器人数量
- `.say <文本>` - 让所有机器人同时发送一条聊天消息
- `.exit` - 断开所有机器人并退出

## 说明
- 本客户端为离线模式，请在 `online-mode=false`（破解/离线）服务器使用
- 版本查验地址: https://shit.pub/s/developer/minecraft/client/MinecraftBotClient-MBC/verify/txt.txt
- 公告栏地址: https://shit.pub/s/developer/minecraft/client/MinecraftBotClient-MBC/announcement.txt
- 帮助网站: {website}
"""

README_EN = """# Minecraft Bot Client (MBC) v{version} - English

## Files
- `{binary}` - English client, {run}
- `config.en.json` - Configuration file
- `README.en.md` - This readme
- `log/` - Log folder (created automatically when logging is enabled)

{note}

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
- `multi_bot_enabled` / `bot_count`: launch multiple bots at once (e.g. 20, 100) with random usernames
- `bot_name_prefix` / `bot_name_digits`: random username prefix and how many random digits it gets
- `bot_join_delay`: seconds between bot connections (keeps the join rate gentle)
- `bot_auth_enabled` / `bot_auth_mode`: auto-login switch and mode (`register`, `login` or `both`)
- `bot_auth_password`: password inserted into the auth commands
- `bot_auth_delay`: seconds to wait after joining before sending the auth command
- `bot_auth_register_command` / `bot_auth_login_command`: command templates, `{{password}}` is replaced with your password

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

## Multi-bot mode
Set `multi_bot_enabled` to `true` and choose `bot_count`. Every bot connects with its own random username, and when `bot_auth_enabled` is on it automatically sends `/register` or `/login` with your `bot_auth_password` right after joining. The console then controls the whole group:
- `.status` - show how many bots are connected
- `.say <text>` - broadcast a chat message from every connected bot
- `.exit` - disconnect all bots and quit

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


def pick_icon():
    if PLATFORM == "windows":
        candidates = ["src/assets/icon.ico"]
    elif PLATFORM == "macos":
        candidates = ["src/assets/icon.icns"]
    else:
        candidates = ["src/assets/icon.png"]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def file_digest(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def print_artifact(path):
    if not os.path.exists(path):
        return
    print(f"  {os.path.basename(path)}  {os.path.getsize(path)} bytes  sha256={file_digest(path)}")


def build_readme(language, binary):
    template = README_ZH if language == "zh" else README_EN
    return template.format(
        version=VERSION,
        website=WEBSITE_URL,
        binary=binary,
        run=RUN_HINTS[language][PLATFORM].format(binary=binary),
        note=PLATFORM_NOTES[language][PLATFORM].format(binary=binary),
    )


def build_one(name, language, output_dir, package_dir):
    print(f"\n=== Building {name} ({PLATFORM_LABEL}, language={language}) ===")

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

    icon = pick_icon()
    if icon:
        cmd.insert(4, f"--icon={icon}")

    subprocess.check_call(cmd)

    src_bin = os.path.join("dist", name + BINARY_EXT)
    if not os.path.exists(src_bin):
        print(f"FAIL: {name}")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)
    dst_bin = os.path.join(output_dir, name + BINARY_EXT)
    shutil.copy2(src_bin, dst_bin)
    if PLATFORM != "windows":
        os.chmod(dst_bin, 0o755)
    print(f"OK: {dst_bin}")

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
        "multi_bot_enabled": False,
        "bot_count": 10,
        "bot_name_prefix": "Bot",
        "bot_name_digits": 4,
        "bot_join_delay": 0.5,
        "bot_auth_enabled": False,
        "bot_auth_mode": "register",
        "bot_auth_password": "",
        "bot_auth_delay": 1.5,
        "bot_auth_register_command": "/register {password} {password}",
        "bot_auth_login_command": "/login {password}",
    }
    config_path = os.path.join(output_dir, f"config.{language}.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print(f"OK: {config_path}")

    readme_path = os.path.join(output_dir, f"README.{language}.md")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(build_readme(language, name + BINARY_EXT))
    print(f"OK: {readme_path}")

    os.makedirs(package_dir, exist_ok=True)
    zip_path = os.path.join(package_dir, f"{language}.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.write(dst_bin, f"{language}/{os.path.basename(dst_bin)}")
        z.write(config_path, f"{language}/{os.path.basename(config_path)}")
        z.write(readme_path, f"{language}/{os.path.basename(readme_path)}")

    print("--- artifacts ---")
    print_artifact(dst_bin)
    print_artifact(zip_path)


def main():
    try:
        import PyInstaller
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    remove_dir("build")
    remove_dir("dist")

    version_root = os.path.join("releases", VERSION, PLATFORM)

    build_one("MinecraftBotClient-zh", "zh", os.path.join(version_root, "zh"), version_root)
    build_one("MinecraftBotClient-en", "en", os.path.join(version_root, "en"), version_root)

    print(f"\n=== Done: releases/{VERSION}/{PLATFORM}/ ===")
    print(f"  zh/  MinecraftBotClient-zh{BINARY_EXT} + config.zh.json + README.zh.md")
    print(f"  en/  MinecraftBotClient-en{BINARY_EXT} + config.en.json + README.en.md")
    print(f"  zh.zip / en.zip packages in the same folder")
    print(f"  Builds are per-platform: run this script once on Windows, macOS and Linux.")


if __name__ == "__main__":
    main()
