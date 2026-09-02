import json
import os

class SettingsManager:
    CONFIG_FILE = "config.json"
    DEFAULT_CONFIG = {
        "version": "1.0.0",
        "username": "",
        "server_address": "localhost:25565",
        "minecraft_version": "1.8.9"
    }

    def __init__(self):
        self.config = self.load_config()

    def load_config(self):
        config = self.DEFAULT_CONFIG.copy()
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r') as f:
                    loaded = json.load(f)
                # 补全缺失的默认键
                for key, value in self.DEFAULT_CONFIG.items():
                    loaded.setdefault(key, value)
                config = loaded
            except Exception:
                pass
        else:
            # 首次运行自动生成配置文件，方便用户填写服务器信息
            self.config = config
            self.save_config()
        return config

    def save_config(self):
        try:
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {str(e)}")

    def get_username(self):
        return self.config.get("username", "")

    def set_username(self, username):
        self.config["username"] = username
        self.save_config()

    def get_server_address(self):
        return self.config.get("server_address", "localhost:25565")

    def set_server_address(self, address):
        self.config["server_address"] = address
        self.save_config()

    def get_minecraft_version(self):
        return self.config.get("minecraft_version", "1.8.9")

    def set_minecraft_version(self, version):
        self.config["minecraft_version"] = version
        self.save_config()

    def get_current_version(self):
        return self.config.get("version", "1.0.0")
