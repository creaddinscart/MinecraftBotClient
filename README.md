# MinecraftBotClient MBC Minecraft Client Official website address

- [Github](https://github.com/creaddinscart/MinecraftBotClient/)
- [Discord](https://discord.gg/yY3nDGzSn5)
- [QQ](https://qm.qq.com/q/4nyFIEjn04)
- [Official Website](https://shit.pub)
- [Our Minecraft Servers](https://shit.pub/an/tz/1007/gadd/)
- [Search Official Support Documentation](support/)
- [View all versions](v/)

# Minecraft Bot Client (MBC)

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-1.3.1-green.svg)](#)
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)](#)
[![Status](https://img.shields.io/badge/status-active-brightgreen.svg)](#)

---

MBC (Minecraft Bot Client) is a pure-protocol Minecraft bot client written in Python. No game assets required — it connects to servers, sends chat messages, and runs commands directly. Features include a bilingual UI, SRV record resolution, vanilla-style command autocomplete, auto-spam, session logging, and more.

## Features

- 🔌 **All versions supported** — Auto-detects the server protocol; any Minecraft version between 1.8 and 26.2
- 🌐 **SRV records** — Auto-resolves `_minecraft._tcp.<domain>` SRV records, no need to specify port
- 🗣️ **Bilingual UI** — Chinese / English, picked automatically from the exe suffix (`-zh` / `-en`)
- ⌨️ **Vanilla-style autocomplete** — Type `.` or `/` for a grey inline preview, `Tab` to complete, `↑/↓` or mouse wheel to cycle, `Esc` to clear
- 💬 **Chat & server commands** — Plain text for chat, `/` prefix for server commands
- 🎛️ **`.` client commands** — `.help` `.esc` `.connect` `.respawn` `.log` `.walk` `.eat` `.spam` `.config` `.exit` (legacy `//` prefix still works)
- 🤖 **Human-like actions** — Head turns and arm swings with random delays and Bézier trajectories, mimicking a real mouse to bypass common anti-cheat checks
- 🚶 **Random auto-walk** — Random roaming or custom waypoints; stops automatically on damage/death
- 🍖 **Auto-eat on damage** — Attempts to eat when health drops below a threshold, toggleable
- 🔔 **Proximity & path alerts** — Announces nearby players and missing blocks ahead; invisible to other players
- 📨 **Auto-spam** — Configurable rate and message list, persisted in config
- 📝 **Session logging** — Auto-creates timestamped `.log` files in the `log/` folder when enabled
- 🔔 **Remote version check & announcements** — Shows remote txt content 1:1 on startup; skip with `fast_start`
- ⚡ **Fast start** — Enable `fast_start` in config to skip network checks and reduce resource usage
- 🌙 **Offline mode** — Designed for `online-mode=false` (cracked/offline) servers
- 💻 **Cross-platform** — Windows / Linux / macOS, single-file exe distribution via PyInstaller

## Quick Start

### Use Releases (recommended)

Download `en/MinecraftBotClient-en.exe` from the [releases/](releases/) directory, place it next to `en/config.en.json`, and double-click the exe.

### Run from source

```bash
pip install -r requirements.txt
python main.py
```

### Build exe

```bash
python build.py
```

Artifacts go into `releases/<version>/` — Chinese and English builds are separate under `zh/` and `en/` subdirectories (exe + config + README).

## Configuration

```json
{
  "version": "1.3.1",
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
}
```

| Field | Description |
|-------|-------------|
| `username` | Player name, leave empty for a random one |
| `server_address` | Server address, SRV domains supported (e.g. `mc.example.com`) or explicit port (e.g. `mc.example.com:25565`) |
| `minecraft_version` | Server version, any value between 1.8 and 26.2 |
| `language` | UI language: `zh` / `en` |
| `fast_start` | Skip version/announcement checks on startup |
| `command_autocomplete` | Toggle command autocomplete |
| `auto_eat` / `auto_eat_health_threshold` | Auto-eat on damage toggle and health threshold |
| `auto_walk` / `auto_walk_waypoints` | Auto-walk toggle and custom waypoints (relative coordinates) |
| `stop_walk_on_damage` | Stop walking automatically on damage/death |
| `proximity_alerts` / `proximity_distance` | Nearby player alerts toggle and distance |
| `human_actions` / `human_action_interval_min/max` | Human-like actions toggle and interval seconds |
| `log_enabled` | Enable logging by default (toggle at runtime with `.log on`) |
| `spam_enabled` / `spam_rate` / `spam_messages` | Auto-spam toggle, rate and message templates |

## Commands

### Client commands (`.` prefix, not sent to the server; legacy `//` still works)

| Command | Description |
|---------|-------------|
| `.help` | Show all commands and open the help website |
| `.esc` | Leave the server but keep the client open (standby mode) |
| `.connect` | Reconnect in standby mode |
| `.exit` | Disconnect and close the client |
| `.respawn` | Send a respawn packet after dying |
| `.log on/off` | Toggle logging (written to the `log/` folder with timestamps) |
| `.spam on/off` | Toggle auto-spam |
| `.spam rate <n>` | Set messages per second |
| `.spam add <msg>` / `.spam remove <i>` / `.spam list` / `.spam clear` / `.spam status` | Spam message management |
| `.walk start/stop` | Start/stop random auto-walk |
| `.walk add <x,y,z>` | Add a custom waypoint (relative coordinates, comma separated) |
| `.walk list` / `.walk clear` | List/clear waypoints |
| `.eat on/off` | Toggle auto-eat on damage |
| `.config <key> [val]` | View or modify any config key (ex: `.config fast_start true`) |

### Vanilla-style Autocomplete

- Type `.` or `/` to see a grey inline preview of the command
- `Tab` accepts the preview; press `Tab` repeatedly to cycle suggestions
- `↑` / `↓` arrow keys or the mouse wheel cycle suggestions
- `Enter` sends, `Esc` clears the input, `↑` also browses command history

### Server commands (`/` prefix, sent to server)

Type `/list`, `/msg player hello`, `/tp ...` etc., same as in-game.

### Plain text

Sent as a chat message directly.

## Remote Version & Announcements

On startup the client fetches and displays the txt content 1:1:

- Version check: `https://shit.pub/s/developer/minecraft/client/MinecraftBotClient-MBC/verify/txt.txt`
- Announcements: `https://shit.pub/s/developer/minecraft/client/MinecraftBotClient-MBC/announcement.txt`

Enable `fast_start` to skip these checks.

## Version Folder Structure

Each build is placed in its own folder under `releases/<version>/`:

```
releases/
├── 1.3.1/
│   ├── zh/
│   │   ├── MinecraftBotClient-zh.exe
│   │   ├── config.zh.json
│   │   └── README.zh.md
│   └── en/
│       ├── MinecraftBotClient-en.exe
│       ├── config.en.json
│       └── README.en.md
└── ...
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
│   │   └── minecraft_bot_client.py  # Main client logic (connect/chat/commands/walk/alerts)
│   ├── network/
│   │   ├── connection_manager.py    # Minecraft protocol (handshake/login/chat/keepalive/SRV/human actions)
│   │   └── version_checker.py       # Remote version check + announcements
│   ├── features/
│   │   └── spam.py                  # Auto-spam manager
│   ├── settings/
│   │   └── settings_manager.py      # Config read/write + persistence
│   └── ui/
│       └── console_ui.py            # Console UI (ANSI colors / autocomplete / mouse wheel)
└── releases/                    # Build artifacts (versioned)
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

Any unlisted version within a range is auto-mapped to the nearest known protocol ID; the actual server protocol is probed before login.

## Dependencies

| Library | Purpose |
|---------|---------|
| `requests` | HTTP requests (version check, announcements) |
| `cryptography` | AES/RSA encryption (online-mode login flow, not triggered in offline mode) |
| `dnspython` | SRV record resolution |
| `pyinstaller` | Packaging into exe |

## Notes

- This client runs in offline mode. Use it on servers with `online-mode=false`
- Please note that the official account mode is still under development; please be patient or subscribe to our GitHub repository
- Help website: <https://shit.pub/s/developer/minecraft/client/MinecraftBotClient-MBC/MBC/>
- For testing and development purposes only

## ©copyright

1. [LICENSE](https://raw.githubusercontent.com/creaddinscart/MinecraftBotClient/refs/heads/main/license) View the address on GitHub.
2. [LICENSE](https://p.shit.pub/dld/?view=license%2FTeam%2FCreaddinscart%2FMinecraftBotClient-MBC%2Flicense.txt) Check p.shit.pub for the address.
