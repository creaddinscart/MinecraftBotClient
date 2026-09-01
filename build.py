import os
import sys
import subprocess
import shutil

def build_executable():
    print("Building MinecraftBotClient executable...")
    
    if not shutil.which('pyinstaller'):
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    output_dir = "dist"
    build_dir = "build"
    
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    
    print("Compiling with PyInstaller...")
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=MinecraftBotClient",
        "--add-data=config.json:.",
        "main.py"
    ]
    
    if os.path.exists("assets/icon.ico"):
        cmd.insert(4, "--icon=assets/icon.ico")
    
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
