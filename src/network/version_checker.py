import json
import requests

class VersionChecker:
    BASE_URL = "https://shit.pub/s/developer/minecraft/client/MinecraftBotClient-MBC/"
    VERSION_URL = BASE_URL + "verify/txt.txt"
    ANNOUNCEMENT_URL = BASE_URL + "announcement.txt"
    TIMEOUT = 8

    def __init__(self):
        self.latest_version = None

    def _get_text(self, url):
        response = requests.get(url, timeout=self.TIMEOUT)
        response.raise_for_status()
        return response.text.strip()

    def fetch_version_info(self):
        raw = self._get_text(self.VERSION_URL)
        try:
            data = json.loads(raw)
            version = data.get("version", "")
            self.latest_version = version or None
            return self.latest_version, raw
        except (json.JSONDecodeError, ValueError):
            lines = [line.strip() for line in raw.splitlines() if line.strip()]
            self.latest_version = lines[0] if lines else None
            return self.latest_version, raw

    def fetch_announcement(self):
        raw = self._get_text(self.ANNOUNCEMENT_URL)
        lines = [line for line in raw.splitlines() if line.strip()]
        return "\n".join(lines) if lines else None

    def is_update_available(self, current_version):
        if not self.latest_version:
            try:
                self.fetch_version_info()
            except Exception:
                return False
        return bool(self.latest_version) and self.latest_version != current_version
