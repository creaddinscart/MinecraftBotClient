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

## Features

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

```bash
pip install -r requirements.txt
python main.py
```

### Build exe

```bash
python build.py
```

Artifacts go into `releases/<version>/` — Chinese and English builds are separate under `zh/` and `en/` subdirectories.

## Configuration

```json
{
  "version": "1.0.2",
  "username": "",
  "server_address": "localhost:25565",
  "minecraft_version": "1.8.9",
  "language": "en",
  "log_enabled": false,
  "spam_enabled": false,
  "spam_rate": 1.0,
  "spam_messages": ["Hello!", "Anyone there?", "GG"]
}
```

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

### Client commands (`//` prefix, not sent to server)

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

