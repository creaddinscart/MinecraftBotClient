import os
import sys
import time
import json
import subprocess
import shutil

VERSION = "1.0.2"
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
  "log_enabled": false,
  "spam_enabled": false,
  "spam_rate": 1.0,
  "spam_messages": ["Hello!", "Anyone there?", "GG"]
}}
```
- `username`: 玩家名，留空自动随机生成
- `server_address`: 服务器地址，支持 SRV 域名（直接填域名即可，如 `mc.example.com`）
- `minecraft_version`: 服务器版本，支持 1.8 - 26.2 区间内任意版本
- `language`: 语言（zh/en）
- `log_enabled`: 是否默认开启日志（true/false）
- `spam_enabled`: 是否默认开启自动垃圾邮件（true/false）
- `spam_rate`: 每秒发送条数
- `spam_messages`: 垃圾消息模板列表

## 命令说明
进入服务器后：
- `//help` - 查看 MBC 客户端命令并打开帮助网站
- `//esc` - 离开服务器但不退出客户端
- `//connect` - 连接 / 重新连接服务器
- `//log true` - 开启日志（写入 log 文件夹，每次运行一个 .log 文件，含时间戳）
- `//log false` - 关闭日志
- `//spam on` - 开启自动垃圾邮件
- `//spam off` - 关闭自动垃圾邮件
- `//spam rate <每秒条数>` - 设置发送速率
- `//spam add <消息>` - 添加一条垃圾消息
- `//spam remove <索引>` - 按索引删除一条消息
- `//spam list` - 列出所有垃圾消息
- `//spam clear` - 清空垃圾消息
- `//spam status` - 查看垃圾邮件状态
- `//exit` - 断开并退出客户端
- `/命令` - 发送服务器命令（如 `/list`、`/msg 玩家 内容`）
- 普通文本 - 作为聊天消息发送

## 说明
- 本客户端为离线模式，请在 `online-mode=false`（破解/离线）服务器使用
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
  "log_enabled": false,
  "spam_enabled": false,
  "spam_rate": 1.0,
  "spam_messages": ["Hello!", "Anyone there?", "GG"]
}}
```
- `username`: Player name, leave empty for a random one
- `server_address`: Server address, SRV record domains supported (just use the domain, e.g. `mc.example.com`)
- `minecraft_version`: Server version, any version between 1.8 - 26.2 is supported
- `language`: Language (zh/en)
- `log_enabled`: Enable logging by default (true/false)
- `spam_enabled`: Enable auto-spam by default (true/false)
- `spam_rate`: Spam messages per second
- `spam_messages`: List of spam message templates

## Commands
After joining a server:
- `//help` - Show MBC client commands and open the help website
- `//esc` - Leave the server without closing the client
- `//connect` - Connect / reconnect to the server
- `//log true` - Enable logging (written to the log folder, one .log file per session with timestamps)
- `//log false` - Disable logging
- `//spam on` - Enable auto-spam
- `//spam off` - Disable auto-spam
- `//spam rate <n>` - Set spam rate (msg/s)
- `//spam add <msg>` - Add a spam message
- `//spam remove <i>` - Remove a spam message by index
- `//spam list` - List all spam messages
- `//spam clear` - Clear all spam messages
- `//spam status` - Show spam status
- `//exit` - Disconnect and close the client
- `/command` - Send a server command (e.g. `/list`, `/msg player text`)
- Plain text - Send as a chat message

## Notes
- This client runs in offline mode. Use it on servers with `online-mode=false`
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
        "log_enabled": False,
        "spam_enabled": False,
        "spam_rate": 1.0,
        "spam_messages": ["Hello!", "Anyone there?", "GG"]
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
