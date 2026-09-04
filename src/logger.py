import os
import re
import threading
from datetime import datetime

_ANSI_RE = re.compile(r'\033\[[0-9;]*[A-Za-z]')


def strip_ansi(text):
    return _ANSI_RE.sub('', str(text))


class SessionLogger:
    def __init__(self, base_dir, enabled=False):
        self.log_dir = os.path.join(base_dir, "log")
        self.enabled = False
        self._file = None
        self._path = None
        self._lock = threading.Lock()
        if enabled:
            self.enable()

    def enable(self):
        with self._lock:
            if self.enabled:
                return self._path
            try:
                os.makedirs(self.log_dir, exist_ok=True)
                fname = "MBC-" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".log"
                self._path = os.path.join(self.log_dir, fname)
                self._file = open(self._path, 'a', encoding='utf-8')
                self.enabled = True
                self._write("LOG", "Session log started")
                return self._path
            except Exception:
                self.enabled = False
                return None

    def disable(self):
        with self._lock:
            if not self.enabled:
                return
            self._write("LOG", "Session log stopped")
            try:
                self._file.close()
            except Exception:
                pass
            self._file = None
            self.enabled = False

    def log(self, category, message):
        if not self.enabled:
            return
        with self._lock:
            self._write(category, message)

    def _write(self, category, message):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        clean = strip_ansi(message).replace('\r', ' ').replace('\n', ' ')
        try:
            self._file.write(f"[{ts}] [{category}] {clean}\n")
            self._file.flush()
        except Exception:
            pass

    def close(self):
        self.disable()
