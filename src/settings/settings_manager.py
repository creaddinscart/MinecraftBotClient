import json
import os

class SettingsManager:
    CONFIG_FILE = "config.json"
    DEFAULT_CONFIG = {
        "version": "1.0.0",
        "server_address": "localhost:25565",
        "minecraft_version": "1.8.9",
        "spam_interval": 5,
        "auto_connect": False
    }
    
    def __init__(self):
        self.config = self.load_config()
    
    def load_config(self):
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except Exception:
                return self.DEFAULT_CONFIG.copy()
        return self.DEFAULT_CONFIG.copy()
    
    def save_config(self):
        try:
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {str(e)}")
    
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
    
    def get_spam_interval(self):
        return self.config.get("spam_interval", 5)
    
    def set_spam_interval(self, interval):
        self.config["spam_interval"] = interval
        self.save_config()
    
    def get_current_version(self):
        return self.config.get("version", "1.0.0")
    
    def is_auto_connect(self):
        return self.config.get("auto_connect", False)
    
    def set_auto_connect(self, enabled):
        self.config["auto_connect"] = enabled
        self.save_config()
