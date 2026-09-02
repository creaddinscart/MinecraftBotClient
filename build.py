import os
import sys
import time
import subprocess
import shutil

def build_executable():
    print("Building MinecraftBotClient executable...")

    if not shutil.which('pyinstaller'):
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    output_dir = "dist"
    build_dir = "build"

    def remove_dir(path):
        if not os.path.exists(path):
            return
        # Windows 下文件可能被占用（杀毒扫描/资源管理器），加重试
        for attempt in range(5):
            try:
                shutil.rmtree(path)
                return
            except OSError:
                time.sleep(1)
        shutil.rmtree(path, ignore_errors=True)

    remove_dir(output_dir)
    remove_dir(build_dir)

    print("Compiling with PyInstaller...")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--console",
        "--clean",
        "-y",
        "--name=MinecraftBotClient",
        "main.py"
    ]
    
    if os.path.exists("src/assets/icon.ico"):
        cmd.insert(4, "--icon=src/assets/icon.ico")
    
    subprocess.check_call(cmd)
    
    exe_path = os.path.join(output_dir, "MinecraftBotClient.exe")
    if os.path.exists(exe_path):
        print(f"Successfully built: {exe_path}")
        return exe_path
    else:
        print("Build failed")
        return None

if __name__ == "__main__":
    build_executable()
