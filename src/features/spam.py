import random
import threading


class SpamManager:
    def __init__(self, connection, log_func=print, sent_func=print):
        self.connection = connection
        self._log = log_func
        self._sent = sent_func
        self.rate = 1.0
        self.messages = []
        self.enabled = False
        self._thread = None
        self._stop_event = threading.Event()

    def start(self):
        if self.enabled:
            return
        if not self.messages:
            self._log("No spam messages configured")
            return
        self.enabled = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        self._log("Spam started at %s msg/s with %s messages" % (self.rate, len(self.messages)))

    def stop(self):
        if not self.enabled:
            return
        self.enabled = False
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=3)
        self._thread = None
        self._log("Spam stopped")

    def _loop(self):
        interval = max(0.1, 1.0 / max(0.01, float(self.rate)))
        while not self._stop_event.is_set():
            try:
                msg = random.choice(list(self.messages))
                self.connection.send_chat(msg)
                self._sent(msg)
            except Exception as e:
                self._log("Spam send error: %s" % e)
                self.enabled = False
                break
            if self._stop_event.wait(interval):
                break

    def set_rate(self, value):
        try:
            r = float(value)
            if r > 0:
                self.rate = r
                self._log("Spam rate set to %s msg/s" % r)
            else:
                self._log("Rate must be greater than 0")
        except (ValueError, TypeError):
            self._log("Invalid rate: %s" % value)

    def add_message(self, message):
        self.messages.append(message)
        self._log("Added message: %s" % message)

    def remove_message(self, index):
        try:
            i = int(index)
            if 0 <= i < len(self.messages):
                removed = self.messages.pop(i)
                self._log("Removed message [%s]: %s" % (i, removed))
            else:
                self._log("Index out of range: %s" % i)
        except (ValueError, TypeError):
            self._log("Invalid index: %s" % index)

    def list_messages(self):
        if not self.messages:
            self._log("No spam messages")
            return
        self._log("Spam messages (%s):" % len(self.messages))
        for i, m in enumerate(self.messages):
            self._log("  [%s] %s" % (i, m))

    def clear_messages(self):
        count = len(self.messages)
        self.messages.clear()
        self._log("Cleared %s spam message(s)" % count)

    def show_status(self):
        state = "RUNNING" if self.enabled else "STOPPED"
        self._log("Spam: %s | Rate: %s msg/s | Messages: %s" % (state, self.rate, len(self.messages)))
