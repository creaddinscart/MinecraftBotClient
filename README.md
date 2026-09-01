# MinecraftBotClient (MBC)

Minecraft Bot Client - A lightweight bot client for Minecraft supporting versions 1.8 through 26.2.

## Features

- Support for Minecraft versions 1.8 to 26.2
- Automatic version checking from remote server
- Random username generation or custom username entry
- Server connection management
- Chat message sending
- Spam messaging capabilities with configurable intervals
- Lightweight and fast performance
- Pure text-based interface
- Persistent configuration

## Installation

### Requirements
- Python 3.7 or higher
- pip package manager

### Setup

```bash
git clone https://github.com/creaddinscart/MinecraftBotClient.git
cd MinecraftBotClient
pip install -r requirements.txt
```

## Usage

### Running the Client

```bash
python main.py
```

### Building Executable

```bash
python build.py
```

This will create `MinecraftBotClient.exe` in the `dist/` directory.

## Commands

- `/spam <message>` - Spam a message multiple times
- `/stopspam` - Stop current spam operation
- `/settings` - View current settings
- `exit` - Disconnect and exit
- `help` - Show all available commands

## Configuration

Settings are stored in `config.json`:

```json
{
  "version": "1.0.0",
  "server_address": "localhost:25565",
  "minecraft_version": "1.8.9",
  "spam_interval": 5,
  "auto_connect": false
}
```

## Version Support

Supported Minecraft versions:
- 1.8, 1.8.9
- 1.12, 1.12.2
- 1.16, 1.16.5
- 1.17, 1.18, 1.18.2
- 1.19, 1.19.2
- 1.20, 1.20.1
- 26.2

## License

This project is provided for educational and testing purposes only.

## Author

Creaddinscart
