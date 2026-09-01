# MinecraftBotClient v1.0.0 - Build Instructions

Complete guide to build MinecraftBotClient.exe from source code.

## System Requirements

- Windows 7 or higher (for running the EXE)
- Python 3.7+ (for building from source)
- 500MB free disk space (for dependencies and build output)

## Step 1: Clone the Repository

```bash
git clone https://github.com/creaddinscart/MinecraftBotClient.git
cd MinecraftBotClient
```

## Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- requests (HTTP library for version checking)
- pyinstaller (for creating the executable)

## Step 3: Build the Executable

### Option A: Using the Python build script

```bash
python build.py
```

### Option B: Using PyInstaller directly

```bash
pyinstaller --onefile --windowed --name MinecraftBotClient main.py
```

### Option C: Using the shell script (Linux/Mac)

```bash
chmod +x build.sh
./build.sh
```

## Step 4: Locate Your EXE File

After successful build, the executable will be at:

```
dist/MinecraftBotClient.exe
```

## Troubleshooting

### PyInstaller not found
```bash
pip install pyinstaller
```

### Build fails with module not found
```bash
pip install --upgrade -r requirements.txt
```

### Python not recognized
Make sure Python 3.7+ is installed and added to PATH:
```bash
python --version
```

## Running the Application

### From Python (without building)
```bash
python main.py
```

### From the built EXE
Simply double-click `dist/MinecraftBotClient.exe` or run:
```bash
dist/MinecraftBotClient.exe
```

## First Run Configuration

On first launch, the client will prompt you to:

1. **Enter Username** (or press Enter for random generation)
2. **Set Server Address** (default: localhost:25565)
3. **Select Minecraft Version** (1.8 - 26.2)
4. **Set Spam Interval** (in seconds, default: 5)

These settings will be saved in `config.json`

## Features Overview

### Chat Commands
- Type normal messages to send to server chat
- `/spam <message>` - Send message multiple times
- `/stopspam` - Stop spam operation
- `/settings` - View current configuration
- `help` - Show all commands
- `exit` - Disconnect and close

### Version Checking
The client automatically checks: 
```
https://shit.pub/s/developer/minecraft/client/MinecraftBotClient-MBC/verify/verify.txt
```

### Supported Minecraft Versions
- 1.8, 1.8.9
- 1.12, 1.12.2
- 1.16, 1.16.5
- 1.17, 1.18, 1.18.2
- 1.19, 1.19.2
- 1.20, 1.20.1
- 26.2

## File Structure

```
MinecraftBotClient/
├── main.py                           Main entry point
├── build.py                          Build script (Python)
├── build.sh                          Build script (Linux/Mac)
├── requirements.txt                  Python dependencies
├── setup.py                          Package setup
├── config.json                       Configuration file (auto-generated)
├── README.md                         Project overview
├── BUILD_INSTRUCTIONS.md             This file
└── src/
    ├── client/
    │   └── minecraft_bot_client.py   Main client class
    ├── network/
    │   ├── version_checker.py        Version checking
    │   └── connection_manager.py     Server connection
    ├── protocol/
    │   └── protocol_handler.py       Minecraft protocol
    ├── settings/
    │   └── settings_manager.py       Configuration management
    └── ui/
        └── console_ui.py             Console interface
```

## Build Output

After building, the `dist/` folder will contain:
- `MinecraftBotClient.exe` - Standalone executable (~40-60MB)

All dependencies are included in the executable.

## Advanced Build Options

### Single-file executable with console
```bash
pyinstaller --onefile --console --name MinecraftBotClient main.py
```

### With custom icon
```bash
pyinstaller --onefile --windowed --icon=icon.ico --name MinecraftBotClient main.py
```

### Optimized smaller size
```bash
pyinstaller --onefile --windowed -y --clean --name MinecraftBotClient main.py
```

## Version Information

- **Project**: MinecraftBotClient (MBC)
- **Version**: 1.0.0
- **Release Date**: September 1, 2026
- **Python Version**: 3.7+
- **License**: For educational and testing purposes only

## Support

For issues or questions, visit:
- GitHub Repository: https://github.com/creaddinscart/MinecraftBotClient
- Issues: https://github.com/creaddinscart/MinecraftBotClient/issues

## License

This project is provided for educational and testing purposes only.

---

**Ready to build? Follow the steps above and you'll have MinecraftBotClient.exe in minutes!**
