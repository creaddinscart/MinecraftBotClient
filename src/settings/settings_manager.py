import json
import os
import sys

class SettingsManager:
    DEFAULT_CONFIG = {
        "version": "1.0.2",
        "username": "",
        "server_address": "localhost:25565",
        "minecraft_version": "1.8.9",
        "language": "zh",
        "log_enabled": False,
        "spam_enabled": False,
        "spam_rate": 1.0,
        "spam_messages": ["Hello!", "Anyone there?", "GG"]
    }

    def __init__(self):
        self._base_dir = os.getcwd()
        self.CONFIG_FILE = self._resolve_config_path()
        self.config = self.load_config()

    def _resolve_config_path(self):
        exe_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
        if getattr(sys, 'frozen', False):
            self._base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        else:
            self._base_dir = os.getcwd()

        candidates = ["config.json"]
        if exe_name.endswith("-zh"):
            candidates.insert(0, "config.zh.json")
        elif exe_name.endswith("-en"):
            candidates.insert(0, "config.en.json")

        for name in candidates:
            path = os.path.join(self._base_dir, name)
            if os.path.exists(path):
                return path

        return os.path.join(self._base_dir, "config.json")

    def get_base_dir(self):
        return self._base_dir

    def load_config(self):
        config = dict(self.DEFAULT_CONFIG)
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r', encoding='utf-8-sig') as f:
                    loaded = json.load(f)
                for key, value in self.DEFAULT_CONFIG.items():
                    loaded.setdefault(key, value)
                config = loaded
            except Exception:
                pass
        else:
            self.config = config
            self.save_config()
        return config

    def save_config(self):
        try:
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {str(e)}")

    def get_username(self):
        return self.config.get("username", "")

    def get_server_address(self):
        return self.config.get("server_address", "localhost:25565")

    def get_minecraft_version(self):
        return self.config.get("minecraft_version", "1.8.9")

    def get_current_version(self):
        return self.config.get("version", "1.0.2")

    def get_language(self):
        return self.config.get("language", "zh")

    def get_log_enabled(self):
        return bool(self.config.get("log_enabled", False))

    def set_log_enabled(self, enabled):
        self.config["log_enabled"] = bool(enabled)
        self.save_config()

    def get_spam_enabled(self):
        return bool(self.config.get("spam_enabled", False))

    def get_spam_rate(self):
        return self.config.get("spam_rate", 1.0)

    def get_spam_messages(self):
        return list(self.config.get("spam_messages", []))

    def save_spam_config(self, enabled, rate, messages):
        self.config["spam_enabled"] = bool(enabled)
        self.config["spam_rate"] = float(rate)
        self.config["spam_messages"] = list(messages)
        self.save_config()
