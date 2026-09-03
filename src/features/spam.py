import threading
import time
import random
import string


class SpamManager:
    def __init__(self, connection_manager, log_func=None, sent_func=None):
        self.connection = connection_manager
        self.log = log_func or print
        self.sent = sent_func or print
        self.enabled = False
        self.rate = 1.0
        self.messages = []
        self._thread = None
        self._stop_event = threading.Event()

    def start(self):
        if self.enabled:
            self.log("Spam is already running")
            return False
        if not self.messages:
            self.log("No spam messages configured")
            return False
        if not self.connection.is_alive():
            self.log("Not connected to server")
            return False
        self.enabled = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._spam_loop, daemon=True)
        self._thread.start()
        self.log(f"Spam started at {self.rate} msg/s with {len(self.messages)} messages")
        return True

    def stop(self):
        if not self.enabled:
            self.log("Spam is not running")
            return False
        self.enabled = False
        self._stop_event.set()
        self.log("Spam stopped")
        return True

    def _spam_loop(self):
        while not self._stop_event.is_set() and self.connection.is_alive():
            msg = random.choice(self.messages)
            try:
                self.connection.send_chat(msg)
                self.sent(msg)
            except Exception:
                break
            interval = 1.0 / self.rate if self.rate > 0 else 1.0
            self._stop_event.wait(interval)

    def set_rate(self, rate):
        try:
            rate = float(rate)
        except (ValueError, TypeError):
            self.log("Invalid rate value")
            return False
        self.rate = max(0.1, min(100.0, rate))
        self.log(f"Spam rate set to {self.rate} msg/s")
        return True

    def add_message(self, msg):
        if not msg:
            return False
        self.messages.append(msg)
        self.log(f"Added message: {msg}")
        return True

    def remove_message(self, index):
        try:
            index = int(index)
            if 0 <= index < len(self.messages):
                removed = self.messages.pop(index)
                self.log(f"Removed message [{index}]: {removed}")
                return True
        except (ValueError, TypeError):
            pass
        self.log("Invalid message index")
        return False

    def clear_messages(self):
        self.messages.clear()
        self.log("Spam messages cleared")
        return True

    def list_messages(self):
        if not self.messages:
            self.log("No spam messages configured")
            return
        self.log(f"Spam messages ({len(self.messages)}):")
        for i, msg in enumerate(self.messages):
            self.log(f"  [{i}] {msg}")

    def show_status(self):
        state = "RUNNING" if self.enabled else "STOPPED"
        self.log(f"Spam: {state} | Rate: {self.rate} msg/s | Messages: {len(self.messages)}")

    def load_config(self, config):
        self.rate = config.get("spam_rate", 1.0)
        self.messages = list(config.get("spam_messages", []))
        if config.get("spam_enabled", False):
            self.start()

    def save_config(self):
        return {
            "spam_enabled": self.enabled,
            "spam_rate": self.rate,
            "spam_messages": list(self.messages),
        }

    @staticmethod
    def generate_random_message(length=16):
        chars = string.ascii_letters + string.digits
        return ''.join(random.choices(chars, k=length))
