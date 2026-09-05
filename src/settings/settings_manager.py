import json
import os
import sys

class SettingsManager:
    DEFAULT_CONFIG = {
        "version": "1.3.1",
        "username": "",
        "server_address": "localhost:25565",
        "minecraft_version": "1.8.9",
        "language": "zh",
        "fast_start": False,
        "log_enabled": False,
        "spam_enabled": False,
        "spam_rate": 1.0,
        "spam_messages": ["Hello!", "Anyone there?", "GG"],
        "command_autocomplete": True,
        "auto_eat": True,
        "auto_eat_health_threshold": 10,
        "auto_walk": False,
        "auto_walk_waypoints": [],
        "stop_walk_on_damage": True,
        "proximity_alerts": True,
        "proximity_distance": 5.0,
        "human_actions": True,
        "human_action_interval_min": 2.0,
        "human_action_interval_max": 7.0,
    }

    def __init__(self):
        self._base_dir = os.getcwd()
        self.load_error = None
        self.corrupt_backup = None
        self.CONFIG_FILE = self._resolve_config_path()
        self.config = self.load_config()

    def _resolve_config_path(self):
        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
        else:
            exe_path = sys.argv[0]
        exe_name = os.path.splitext(os.path.basename(exe_path))[0]
        exe_dir = os.path.dirname(os.path.abspath(exe_path))

        candidates = ["config.json"]
        if exe_name.endswith("-zh"):
            candidates.insert(0, "config.zh.json")
        elif exe_name.endswith("-en"):
            candidates.insert(0, "config.en.json")

        search_dirs = [exe_dir]
        cwd = os.getcwd()
        if os.path.abspath(cwd) != os.path.abspath(exe_dir):
            search_dirs.append(cwd)

        for directory in search_dirs:
            for name in candidates:
                path = os.path.join(directory, name)
                if os.path.exists(path):
                    self._base_dir = directory
                    return path

        self._base_dir = exe_dir
        return os.path.join(exe_dir, candidates[0])

    def get_config_path(self):
        return self.CONFIG_FILE

    def get_base_dir(self):
        return self._base_dir

    def load_config(self):
        config = {k: (list(v) if isinstance(v, list) else v) for k, v in self.DEFAULT_CONFIG.items()}
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r', encoding='utf-8-sig') as f:
                    loaded = json.load(f)
                if not isinstance(loaded, dict):
                    raise ValueError("config root is not a JSON object")
                for key, value in self.DEFAULT_CONFIG.items():
                    loaded.setdefault(key, list(value) if isinstance(value, list) else value)
                config = loaded
            except Exception as e:
                self.load_error = str(e)
                try:
                    bad = self.CONFIG_FILE + ".corrupt"
                    if os.path.exists(bad):
                        os.remove(bad)
                    os.rename(self.CONFIG_FILE, bad)
                    self.corrupt_backup = bad
                except Exception:
                    self.corrupt_backup = None
                self.config = config
                self.save_config()
        else:
            self.config = config
            self.save_config()
        return config

    def save_config(self):
        try:
            os.makedirs(os.path.dirname(self.CONFIG_FILE) or '.', exist_ok=True)
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def get_current_version(self):
        return self.config.get("version", "1.3.1")

    def get_username(self):
        return self.config.get("username", "")

    def get_server_address(self):
        return self.config.get("server_address", "localhost:25565")

    def get_minecraft_version(self):
        return self.config.get("minecraft_version", "1.8.9")

    def get_language(self):
        return self.config.get("language", "zh")

    def get_fast_start(self):
        return bool(self.config.get("fast_start", False))

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

    def set(self, key, value):
        self.config[key] = value
        self.save_config()

    def get(self, key, default=None):
        return self.config.get(key, default)
