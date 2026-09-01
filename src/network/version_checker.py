import requests
import json

class VersionChecker:
    VERSION_URL = "https://shit.pub/s/developer/minecraft/client/MinecraftBotClient-MBC/verify/verify.txt"
    TIMEOUT = 10
    
    def __init__(self):
        self.latest_version = None
    
    def fetch_latest_version(self):
        try:
            response = requests.get(self.VERSION_URL, timeout=self.TIMEOUT)
            if response.status_code == 200:
                content = response.text.strip()
                version_info = json.loads(content)
                self.latest_version = version_info.get("version", None)
                return self.latest_version
            else:
                raise Exception(f"HTTP Error: {response.status_code}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error: {str(e)}")
        except json.JSONDecodeError:
            raise Exception("Invalid JSON response from version server")
    
    def is_update_available(self, current_version):
        if not self.latest_version:
            self.fetch_latest_version()
        return self.latest_version and self.latest_version != current_version
