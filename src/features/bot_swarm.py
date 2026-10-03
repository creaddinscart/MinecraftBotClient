import random
import string
import threading

from src import i18n
from src.network.connection_manager import ConnectionManager


class BotWorker:
    def __init__(self, index, name, address, version, protocol_id, settings, log_func, stop_event):
        self.index = index
        self.name = name
        self.address = address
        self.version = version
        self.protocol_id = protocol_id
        self.settings = settings
        self.log = log_func
        self.stop_event = stop_event
        self.connection = None
        self.connected = False

    def run(self):
        conn = ConnectionManager()
        self.connection = conn
        try:
            conn.connect(
                server_address=self.address,
                username=self.name,
                protocol_version=self.version,
                protocol_id=self.protocol_id,
                log_func=lambda message: None,
                on_disconnect=self._on_disconnect,
            )
        except Exception as e:
            self.log(i18n.t('label_bot_failed', name=self.name, err=str(e)))
            self.connected = False
            return

        self.connected = True
        self.log(i18n.t('label_bot_joined', name=self.name))
        self.authenticate()

        while not self.stop_event.is_set():
            if not conn.is_alive():
                break
            if self.stop_event.wait(0.5):
                break

        self.connected = False
        try:
            conn.disconnect()
        except Exception:
            pass
        self.log(i18n.t('label_bot_left', name=self.name))

    def _on_disconnect(self):
        self.connected = False

    def authenticate(self):
        if not self.settings.get("bot_auth_enabled", False):
            return
        password = str(self.settings.get("bot_auth_password", "") or "")
        if not password:
            self.log(i18n.t('label_bot_auth_no_password', name=self.name))
            return

        delay = float(self.settings.get("bot_auth_delay", 1.5) or 0)
        if delay > 0 and self.stop_event.wait(delay):
            return

        mode = str(self.settings.get("bot_auth_mode", "register") or "register").lower()
        if mode not in ("register", "login", "both"):
            mode = "register"

        if mode in ("register", "both"):
            self.send_auth_command("bot_auth_register_command", "/register {password} {password}", password)
            if mode == "both":
                if self.stop_event.wait(1.0):
                    return
        if mode in ("login", "both"):
            self.send_auth_command("bot_auth_login_command", "/login {password}", password)

    def send_auth_command(self, key, default, password):
        template = str(self.settings.get(key, default) or default)
        command = template.replace("{password}", password)
        if not command.strip() or not self.connection:
            return
        try:
            self.connection.send_chat(command)
            self.log(i18n.t('label_bot_auth_sent', name=self.name, cmd=command))
        except Exception as e:
            self.log(i18n.t('label_bot_failed', name=self.name, err=str(e)))

    def send_chat(self, message):
        if not self.connected or not self.connection:
            return False
        try:
            self.connection.send_chat(message)
            return True
        except Exception:
            return False

    def disconnect(self):
        self.connected = False
        if self.connection:
            try:
                self.connection.disconnect()
            except Exception:
                pass


class BotSwarm:
    def __init__(self, settings, log_func):
        self.settings = settings
        self.log = log_func
        self.stop_event = threading.Event()
        self.workers = []
        self.threads = []
        self.protocol_id = None
        self.address = str(self.settings.get("server_address", "localhost:25565") or "localhost:25565")
        self.version = str(self.settings.get("minecraft_version", "1.8.9") or "1.8.9")

    def start(self):
        count = int(self.settings.get("bot_count", 10) or 10)
        count = max(1, min(count, 500))
        delay = float(self.settings.get("bot_join_delay", 0.5) or 0)

        self.protocol_id = self.detect_protocol()
        names = self.make_names(count)
        self.log(i18n.t('label_swarm_target', count=len(names), addr=self.address))

        for i, name in enumerate(names):
            if self.stop_event.is_set():
                break
            worker = BotWorker(i + 1, name, self.address, self.version, self.protocol_id,
                               self.settings, self.log, self.stop_event)
            thread = threading.Thread(target=worker.run, daemon=True, name=f"mbc-bot-{name}")
            self.workers.append(worker)
            self.threads.append(thread)
            thread.start()
            if delay > 0 and i < len(names) - 1:
                if self.stop_event.wait(delay):
                    break

    def detect_protocol(self):
        probe = ConnectionManager()
        host, port, _ = probe.resolve_address(self.address)
        detected = probe.detect_protocol(host, int(port))
        if detected:
            protocol_id, name = detected
            self.log(i18n.t('label_protocol_detected', name=name or '?', pid=protocol_id))
            return protocol_id
        protocol_id, _ = ConnectionManager.resolve_protocol(self.version)
        self.log(i18n.t('label_protocol_fallback', ver=self.version, pid=protocol_id))
        return protocol_id

    def make_names(self, count):
        prefix = str(self.settings.get("bot_name_prefix", "Bot") or "Bot")
        digits = int(self.settings.get("bot_name_digits", 4) or 4)
        digits = max(2, min(6, digits))
        max_prefix = max(1, 16 - digits)
        prefix = prefix[:max_prefix]

        names = []
        used = set()
        guard = 0
        while len(names) < count and guard < count * 100:
            guard += 1
            name = prefix + ''.join(random.choices(string.digits, k=digits))
            if name in used:
                continue
            used.add(name)
            names.append(name)
        return names

    def stop(self):
        self.stop_event.set()
        for worker in self.workers:
            worker.disconnect()
        for thread in self.threads:
            thread.join(timeout=3)

    def say(self, message):
        sent = 0
        for worker in self.workers:
            if worker.send_chat(message):
                sent += 1
        return sent

    def alive_count(self):
        return sum(1 for worker in self.workers
                   if worker.connected and worker.connection and worker.connection.is_alive())

    def total_count(self):
        return len(self.workers)
