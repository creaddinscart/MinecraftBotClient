# Minecraft Bot Client (MBC)

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-1.0.2-green.svg)](#)
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)](#)
[![Status](https://img.shields.io/badge/status-active-brightgreen.svg)](#)
=======
# MinecraftBotClient MBC Minecraft Client Official website address
- [Github](https://github.com/creaddinscart/MinecraftBotClient/)
- [Discord](https://discord.gg/yY3nDGzSn5)
- [QQ](https://qm.qq.com/q/4nyFIEjn04)
- [Official Website](https://shit.pub)
- [Our Minecraft Servers](https://shit.pub/an/tz/1007/gadd/)
- [Search Official Support Documentation](support/)
- [View all versions](v/)

# Minecraft Bot Client (MBC)

---

MBC (Minecraft Bot Client) is a pure-protocol Minecraft bot client written in Python. No game assets required — it connects to servers, sends chat messages, and runs commands directly. Features include bilingual UI, SRV record resolution, auto-spam, session logging, and more.
>>>>>>> cb38cfabbf392b3fc06a4790424e08080e6564a2

**[English](README.en.md)** | 中文

<<<<<<< HEAD
---

MBC (Minecraft Bot Client) 是一个纯协议级的 Minecraft 机器人客户端，用 Python 实现，无需下载游戏资源即可连接服务器、发送聊天、执行命令。支持中英文双语界面、SRV 记录解析、自动垃圾邮件、会话日志等功能。

## 功能特性

- 🔌 **全版本支持** — 自动推断协议版本，支持 Minecraft 1.8 ~ 26.2 区间内任意版本
- 🌐 **SRV 记录** — 自动解析 `_minecraft._tcp.<domain>` SRV 记录，无需手动填端口
- 🗣️ **双语界面** — 中文 / 英文，config 一键切换
- 💬 **聊天 & 服务器命令** — 直接输入文字聊天，`/` 开头为服务器命令
- 🎛️ **// 客户端指令** — `//help` `//esc` `//connect` `//log` `//spam` `//exit`
- 📨 **自动垃圾邮件** — 可配置速率、消息列表，config 持久化
- 📝 **会话日志** — 开启后在 `log/` 目录自动生成带时间戳的 `.log` 文件
- 🔔 **远程版本查验 & 公告栏** — 启动时访问远端 txt 文件获取最新版本和公告
- 🌙 **离线模式** — 专为 `online-mode=false`（破解/离线）服务器设计
- 💻 **跨平台** — Windows / Linux / macOS，单文件 exe 分发（PyInstaller）

## 快速开始

### 直接使用 Release（推荐）

从 [releases/](releases/) 目录下载对应版本的 `zh/MinecraftBotClient-zh.exe`，与 `zh/config.zh.json` 放在同一目录，双击 exe 即可。

### 从源码运行
=======
- 🔌 **All versions supported** — Auto protocol inference for any Minecraft version between 1.8 and 26.2
- 🌐 **SRV records** — Auto-resolves `_minecraft._tcp.<domain>` SRV records, no need to specify port
- 🗣️ **Bilingual UI** — Chinese / English, switchable via config
- 💬 **Chat & server commands** — Plain text for chat, `/` prefix for server commands
- 🎛️ **// Client commands** — `//help` `//esc` `//connect` `//log` `//spam` `//exit`
- 📨 **Auto-spam** — Configurable rate and message list, persisted to config
- 📝 **Session logging** — Auto-creates timestamped `.log` files in `log/` folder when enabled
- 🔔 **Remote version check & announcements** — Fetches latest version and announcements from remote txt on startup
- 🌙 **Offline mode** — Designed for `online-mode=false` servers
- 💻 **Cross-platform** — Windows / Linux / macOS, single-file exe distribution via PyInstaller

## Quick Start

### Use Releases (recommended)

Download `en/MinecraftBotClient-en.exe` from the [releases/](releases/) directory, place it next to `en/config.en.json`, and double-click the exe.

### Run from source
>>>>>>> cb38cfabbf392b3fc06a4790424e08080e6564a2

```bash
pip install -r requirements.txt
python main.py
```

<<<<<<< HEAD
### 构建 exe
=======
### Build exe
>>>>>>> cb38cfabbf392b3fc06a4790424e08080e6564a2

```bash
python build.py
```

<<<<<<< HEAD
构建产物按版本号输出到 `releases/<version>/`，中英文各自独立在 `zh/` 和 `en/` 子目录下。

## 配置文件
=======
Artifacts go into `releases/<version>/` — Chinese and English builds are separate under `zh/` and `en/` subdirectories.

## Configuration
>>>>>>> cb38cfabbf392b3fc06a4790424e08080e6564a2

```json
{
  "version": "1.0.2",
  "username": "",
  "server_address": "localhost:25565",
  "minecraft_version": "1.8.9",
<<<<<<< HEAD
  "language": "zh",
=======
  "language": "en",
>>>>>>> cb38cfabbf392b3fc06a4790424e08080e6564a2
  "log_enabled": false,
  "spam_enabled": false,
  "spam_rate": 1.0,
  "spam_messages": ["Hello!", "Anyone there?", "GG"]
}
```

<<<<<<< HEAD
| 字段 | 说明 |
|------|------|
| `username` | 玩家名，留空自动随机生成 |
| `server_address` | 服务器地址，支持 SRV 域名（如 `mc.example.com`）或显式端口（如 `mc.example.com:25565`） |
| `minecraft_version` | 服务器版本，1.8 ~ 26.2 区间内任意值 |
| `language` | 界面语言：`zh` / `en` |
| `log_enabled` | 是否默认开启日志（运行时也可通过 `//log` 命令切换） |
| `spam_enabled` | 是否默认开启自动垃圾邮件 |
| `spam_rate` | 每秒发送条数 |
| `spam_messages` | 垃圾消息模板列表，每条随机选取 |

## 命令参考

### 客户端命令（`//` 前缀，不发给服务器）

| 命令 | 说明 |
|------|------|
| `//help` | 显示全部命令并打开帮助网站 |
| `//esc` | 离开服务器但不退出客户端，进入待命 |
| `//connect` | 待命状态下重新连接服务器 |
| `//log true/false` | 开关日志（写入 `log/` 文件夹，含时间戳） |
| `//spam on/off` | 开关自动垃圾邮件 |
| `//spam rate <n>` | 设置每秒发送条数 |
| `//spam add <msg>` | 添加一条垃圾消息 |
| `//spam remove <i>` | 按索引删除一条消息 |
| `//spam list` | 列出全部垃圾消息 |
| `//spam clear` | 清空垃圾消息 |
| `//spam status` | 查看垃圾邮件状态 |
| `//exit` | 断开并退出客户端 |

### 服务器命令（`/` 前缀，发给服务器）

直接输入 `/list` `/msg player hello` `/tp ...` 等，与在游戏内一样。

### 普通文本

直接输入即作为聊天消息发送。

## 远程版本 & 公告

启动时自动访问以下地址：

- 版本查验：`https://shit.pub/s/developer/minecraft/client/MinecraftBotClient-MBC/verify/txt.txt`
  - 支持纯文本（第一行即版本号）或 JSON（`{"version": "1.0.2"}`）
  - 当前版本与服务端不一致时提示更新
- 公告栏：`https://shit.pub/s/developer/minecraft/client/MinecraftBotClient-MBC/announcement.txt`
  - 纯文本，每行一条公告，启动时显示在独立区块

## 版本文件夹结构

每次构建生成的独立版本放在 `releases/<version>/` 下：

```
releases/
├── 1.0.2/
│   ├── zh/
│   │   ├── MinecraftBotClient-zh.exe
│   │   ├── config.zh.json
│   │   └── README.zh.md
│   └── en/
│       ├── MinecraftBotClient-en.exe
│       ├── config.en.json
│       └── README.en.md
├── 1.0.1/
│   └── ...
```

## 项目结构

```
MinecraftBotClient/
├── main.py                      # 入口
├── build.py                     # 构建脚本（按版本号输出，中英文独立）
├── requirements.txt             # Python 依赖
├── README.md                    # 中文文档
├── README.en.md                 # English documentation
├── src/
│   ├── i18n.py                  # 中英文本字典 + t() 翻译函数
│   ├── logger.py                # 会话日志（SessionLogger）
│   ├── client/
│   │   └── minecraft_bot_client.py  # 主客户端逻辑（连接/聊天/命令循环）
│   ├── network/
│   │   ├── connection_manager.py     # Minecraft 协议实现（握手/登录/聊天/心跳/SRV）
│   │   └── version_checker.py        # 远程版本查验 + 公告栏
│   ├── features/
│   │   └── spam.py                   # 自动垃圾邮件管理器
│   ├── settings/
│   │   └── settings_manager.py       # 配置文件读写 + 持久化
│   ├── ui/
│   │   └── console_ui.py             # 控制台界面（ANSI 颜色/Windows VT）
│   ├── auth/
│   │   └── microsoft_auth.py         # 微软正版登录（保留，默认离线模式不触发）
│   └── protocol/
│       └── protocol_handler.py       # 协议辅助工具
├── releases/                    # 构建产物（按版本号）
└── .github/workflows/build.yml  # CI 自动构建
```

## 协议支持范围

| 区间 | 版本示例 | 协议号 |
|------|----------|--------|
| 1.8 | 1.8, 1.8.9 | 47 |
| 1.9 - 1.12 | 1.9, 1.10.2, 1.11, 1.12.2 | 47 - 340 |
| 1.13 - 1.16 | 1.13.2, 1.14.4, 1.15.2, 1.16.5 | 340 - 754 |
| 1.17 - 1.18 | 1.17, 1.18.2 | 755 - 758 |
| 1.19 | 1.19, 1.19.2, 1.19.4 | 759 - 760 |
| 1.20 | 1.20 - 1.20.6 | 763 - 766 |
| 1.21 | 1.21 - 1.21.8 | 767 - 773 |
| 25.x - 26.x | 25.1 - 26.2 | 774 - 777 |

区间内任意未显式列出的版本号自动向上兼容到最近的协议号。

## 依赖

| 库 | 用途 |
|----|------|
| `requests` | HTTP 请求（版本查验、公告栏） |
| `cryptography` | AES/RSA 加密（正版服务器登录流程，离线模式不触发） |
| `dnspython` | SRV 记录解析 |
| `pyinstaller` | 打包 exe |

## 说明

- 本客户端为离线模式，仅限 `online-mode=false`（破解/离线）服务器使用
- 帮助网站：<https://shit.pub/s/developer/minecraft/client/MinecraftBotClient-MBC/MBC/>
- 仅用于测试与开发用途
=======
| Field | Description |
|-------|-------------|
| `username` | Player name, leave empty for a random one |
| `server_address` | Server address, SRV domains supported (e.g. `mc.example.com`) or explicit port (e.g. `mc.example.com:25565`) |
| `minecraft_version` | Server version, any value between 1.8 and 26.2 |
| `language` | UI language: `zh` / `en` |
| `log_enabled` | Enable logging by default (toggle at runtime with `//log`) |
| `spam_enabled` | Enable auto-spam by default |
| `spam_rate` | Messages per second |
| `spam_messages` | List of spam message templates, each picked randomly |

## Commands
>>>>>>> cb38cfabbf392b3fc06a4790424e08080e6564a2

### Client commands (`//` prefix, not sent to server)

<<<<<<< HEAD
MIT
=======
| Command | Description |
|---------|-------------|
| `//help` | Show all commands and open the help website |
| `//esc` | Leave the server but keep the client open (standby mode) |
| `//connect` | Reconnect in standby mode |
| `//log true/false` | Toggle logging (written to `log/` folder with timestamps) |
| `//spam on/off` | Toggle auto-spam |
| `//spam rate <n>` | Set messages per second |
| `//spam add <msg>` | Add a spam message |
| `//spam remove <i>` | Remove a spam message by index |
| `//spam list` | List all spam messages |
| `//spam clear` | Clear all spam messages |
| `//spam status` | Show spam status |
| `//exit` | Disconnect and close the client |

### Server commands (`/` prefix, sent to server)

Type `/list` `/msg player hello` `/tp ...` etc., same as in-game.

### Plain text

Sent as a chat message directly.

### Remote Version & Announcements

On startup the client fetches:

- Version check: `https://shit.pub/s/developer/minecraft/client/MinecraftBotClient-MBC/verify/txt.txt`
  - Supports plain text (first line = version) or JSON (`{"version": "1.0.2"}`)
  - Prompts to update if local version differs
- Announcements: `https://shit.pub/s/developer/minecraft/client/MinecraftBotClient-MBC/announcement.txt`
  - Plain text, one announcement per line, shown in a dedicated section on startup

## Version Folder Structure

Each build is placed in its own folder under `releases/<version>/`:

```
releases/
├── 1.0.2/
│   ├── zh/
│   │   ├── MinecraftBotClient-zh.exe
│   │   ├── config.zh.json
│   │   └── README.zh.md
│   └── en/
│       ├── MinecraftBotClient-en.exe
│       ├── config.en.json
│       └── README.en.md
├── 1.0.1/
│   └── ...
```

## Project Structure

```
MinecraftBotClient/
├── main.py                      # Entry point
├── build.py                     # Build script (versioned output, bilingual)
├── requirements.txt             # Python dependencies
├── README.md                    # 中文文档
├── README.en.md                 # This file
├── src/
│   ├── i18n.py                  # Bilingual dictionary + t() translation function
│   ├── logger.py                # SessionLogger for per-session log files
│   ├── client/
│   │   └── minecraft_bot_client.py  # Main client logic (connect/chat/command loop)
│   ├── network/
│   │   ├── connection_manager.py     # Minecraft protocol (handshake/login/chat/keepalive/SRV)
│   │   └── version_checker.py        # Remote version check + announcements
│   ├── features/
│   │   └── spam.py                   # Auto-spam manager
│   ├── settings/
│   │   └── settings_manager.py       # Config read/write + persistence
│   ├── ui/
│   │   └── console_ui.py             # Console UI (ANSI colors / Windows VT)
│   ├── auth/
│   │   └── microsoft_auth.py         # Microsoft auth (kept for reference, not used in offline mode)
│   └── protocol/
│       └── protocol_handler.py       # Protocol helpers
├── releases/                    # Build artifacts (versioned)
└── .github/workflows/build.yml  # CI auto-build
```

## Protocol Support

| Range | Examples | Protocol ID |
|-------|----------|-------------|
| 1.8 | 1.8, 1.8.9 | 47 |
| 1.9 - 1.12 | 1.9, 1.10.2, 1.11, 1.12.2 | 47 - 340 |
| 1.13 - 1.16 | 1.13.2, 1.14.4, 1.15.2, 1.16.5 | 340 - 754 |
| 1.17 - 1.18 | 1.17, 1.18.2 | 755 - 758 |
| 1.19 | 1.19, 1.19.2, 1.19.4 | 759 - 760 |
| 1.20 | 1.20 - 1.20.6 | 763 - 766 |
| 1.21 | 1.21 - 1.21.8 | 767 - 773 |
| 25.x - 26.x | 25.1 - 26.2 | 774 - 777 |

Any unlisted version within a range is auto-mapped to the nearest known protocol ID.

## Dependencies

| Library | Purpose |
|---------|---------|
| `requests` | HTTP requests (version check, announcements) |
| `cryptography` | AES/RSA encryption (online-mode login flow, not triggered in offline mode) |
| `dnspython` | SRV record resolution |
| `pyinstaller` | Packaging into exe |

## Notes

- This client runs in offline mode. Use it on servers with `online-mode=false`
- Help website: <https://shit.pub/s/developer/minecraft/client/MinecraftBotClient-MBC/MBC/>
- For testing and development purposes only


## ©copyright
1. [LICENSE](https://raw.githubusercontent.com/creaddinscart/MinecraftBotClient/refs/heads/main/license)View the address on GitHub.
2. [LICENSE](https://p.shit.pub/dld/?view=license%2FTeam%2FCreaddinscart%2FMinecraftBotClient-MBC%2Flicense.txt)Check p.shit.pub for the address.

