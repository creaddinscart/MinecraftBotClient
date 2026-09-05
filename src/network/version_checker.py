import json
import requests

class VersionChecker:
    BASE_URL = "https://shit.pub/s/developer/minecraft/client/MinecraftBotClient-MBC/"
    VERSION_URL = BASE_URL + "verify/txt.txt"
    ANNOUNCEMENT_URL = BASE_URL + "announcement.txt"
    TIMEOUT = 12

    def __init__(self):
        self.latest_version = None
        self.raw_version_response = None
        self.raw_announcement_response = None

    def _get_text(self, url):
        response = requests.get(url, timeout=self.TIMEOUT)
        self._last_status = response.status_code
        if response.status_code != 200:
            return ""
        return response.text

    def fetch_version_info(self):
        raw = self._get_text(self.VERSION_URL)
        self.raw_version_response = raw
        parsed = None
        try:
            data = json.loads(raw)
            version = str(data.get("version", "")).strip()
            parsed = version or None
        except Exception:
            lines = [line.strip() for line in raw.splitlines() if line.strip()]
            parsed = lines[0] if lines else None
        self.latest_version = parsed
        return parsed, raw

    def fetch_announcement(self):
        raw = self._get_text(self.ANNOUNCEMENT_URL)
        self.raw_announcement_response = raw
        lines = [line.rstrip() for line in raw.splitlines()]
        return "\n".join(lines) if any(l.strip() for l in lines) else None

    @staticmethod
    def _version_tuple(version_str):
        try:
            s = str(version_str).strip().lstrip('vV')
            parts = []
            for p in s.split('.'):
                digits = ''.join(ch for ch in p if ch.isdigit())
                parts.append(int(digits) if digits else 0)
            while len(parts) < 3:
                parts.append(0)
            return tuple(parts[:3])
        except Exception:
            return None

    def is_update_available(self, current_version):
        if not self.latest_version:
            try:
                self.fetch_version_info()
            except Exception:
                return False
        if not self.latest_version:
            return False
        remote = self._version_tuple(self.latest_version)
        local = self._version_tuple(current_version)
        if remote is None or local is None:
            return self.latest_version.strip().lstrip('vV') != current_version.strip().lstrip('vV')
        return remote > local
