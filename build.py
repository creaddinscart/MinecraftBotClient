import os
import sys
import time
import json
import subprocess
import shutil

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

def build_one(name, language):
    print(f"\n=== Building {name} (language={language}) ===")

    remove_dir("build")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--console",
        "--clean",
        "-y",
        f"--name={name}",
        "main.py"
    ]

    if os.path.exists("src/assets/icon.ico"):
        cmd.insert(4, "--icon=src/assets/icon.ico")

    subprocess.check_call(cmd)

    exe_path = os.path.join("dist", f"{name}.exe")
    if os.path.exists(exe_path):
        print(f"OK: {exe_path}")
    else:
        print(f"FAIL: {name}")
        sys.exit(1)

    config_path = os.path.join("dist", f"config.{language}.json")
    config = {
        "version": "1.0.0",
        "username": "",
        "server_address": "localhost:25565",
        "minecraft_version": "1.8.9",
        "language": language
    }
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

def main():
    if not shutil.which('pyinstaller'):
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    remove_dir("dist")
    remove_dir("build")

    build_one("MinecraftBotClient-zh", "zh")

    build_one("MinecraftBotClient-en", "en")

    print("\n=== Done ===")
    print("dist/MinecraftBotClient-zh.exe  +  dist/config.zh.json")
    print("dist/MinecraftBotClient-en.exe  +  dist/config.en.json")

if __name__ == "__main__":
    main()
