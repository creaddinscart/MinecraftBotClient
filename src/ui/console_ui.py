import os
import sys
import time
from datetime import datetime
from src import i18n

if os.name == 'nt':
    import ctypes
    from ctypes import wintypes

    class _COORD(ctypes.Structure):
        _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

    class _KEY_EVENT_RECORD(ctypes.Structure):
        _fields_ = [
            ("bKeyDown", wintypes.BOOL),
            ("wRepeatCount", wintypes.WORD),
            ("wVirtualKeyCode", wintypes.WORD),
            ("wVirtualScanCode", wintypes.WORD),
            ("uChar", wintypes.WCHAR),
            ("dwControlKeyState", wintypes.DWORD),
        ]

    class _MOUSE_EVENT_RECORD(ctypes.Structure):
        _fields_ = [
            ("dwMousePosition", _COORD),
            ("dwButtonState", wintypes.DWORD),
            ("dwControlKeyState", wintypes.DWORD),
            ("dwEventFlags", wintypes.DWORD),
        ]

    class _INPUT_RECORD(ctypes.Structure):
        class _EVENT(ctypes.Union):
            _fields_ = [
                ("KeyEvent", _KEY_EVENT_RECORD),
                ("MouseEvent", _MOUSE_EVENT_RECORD),
            ]
        _anonymous_ = ("Event",)
        _fields_ = [("EventType", wintypes.WORD), ("Event", _EVENT)]

class ConsoleUI:
    COLOR_RESET = '\033[0m'
    COLOR_RED = '\033[91m'
    COLOR_GREEN = '\033[92m'
    COLOR_YELLOW = '\033[93m'
    COLOR_BLUE = '\033[94m'
    COLOR_MAGENTA = '\033[95m'
    COLOR_CYAN = '\033[96m'
    COLOR_WHITE = '\033[97m'
    COLOR_DARK = '\033[90m'

    def __init__(self):
        self.timestamp = True
        self._input_active = False
        self._input_buffer = ""
        self._input_prompt = ""
        self._print_lock = __import__('threading').Lock()
        self._history = []
        self._history_index = -1
        self._ac_enabled = True
        self._ac_items = []
        self._ac_index = -1
        self._ac_pool = None
        self._ac_filter = ""
        self._console_input_handle = None
        self._enable_windows_ansi()

    def _enable_windows_ansi(self):
        if os.name != 'nt':
            return
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-11)
            mode = ctypes.c_uint32()
            if kernel32.GetConsoleMode(handle, __import__('ctypes').byref(mode)):
                kernel32.SetConsoleMode(handle, mode.value | 0x0004)
        except Exception:
            pass

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def show_loading(self, fast_start=False):
        self.clear_screen()
        title = i18n.t('loading_title')
        print(f"\n{self.COLOR_CYAN}{'='*60}{self.COLOR_RESET}")
        print(f"{self.COLOR_CYAN}{title.center(60)}{self.COLOR_RESET}")
        phases = ["[·    ]", "[··   ]", "[···  ]", "[···· ]", "[·····]"]
        if fast_start:
            print(f"{self.COLOR_GREEN}[·····] {i18n.t('loading_done')} (fast start){self.COLOR_RESET}")
            print(f"{self.COLOR_CYAN}{'='*60}{self.COLOR_RESET}\n")
            return
        for p in phases:
            sys.stdout.write(f"\r{self.COLOR_YELLOW}{p}{self.COLOR_RESET} {title}")
            sys.stdout.flush()
            time.sleep(0.25)
        sys.stdout.write(f"\r{self.COLOR_GREEN}[·····] {i18n.t('loading_done')}                    {self.COLOR_RESET}\n")
        print(f"{self.COLOR_CYAN}{'='*60}{self.COLOR_RESET}\n")

    def print_banner(self):
        banner = f"""
{self.COLOR_CYAN}╔════════════════════════════════════════════════════════╗{self.COLOR_RESET}
{self.COLOR_CYAN}║{self.COLOR_RESET}    {i18n.t('banner_title'):<50}{self.COLOR_CYAN}║{self.COLOR_RESET}
{self.COLOR_CYAN}║{self.COLOR_RESET}    {i18n.t('banner_sub1'):<50}{self.COLOR_CYAN}║{self.COLOR_RESET}
{self.COLOR_CYAN}║{self.COLOR_RESET}    {i18n.t('banner_sub2'):<50}{self.COLOR_CYAN}║{self.COLOR_RESET}
{self.COLOR_CYAN}╚════════════════════════════════════════════════════════╝{self.COLOR_RESET}
        """
        print(banner)

    def get_timestamp(self):
        if self.timestamp:
            return f"[{datetime.now().strftime('%H:%M:%S')}] "
        return ""

    def _safe_print(self, message, prefix_color=None, prefix_label=None):
        with self._print_lock:
            if self._input_active:
                sys.stdout.write('\r\033[K')
                if prefix_color and prefix_label:
                    print(f"{self.get_timestamp()}{prefix_color}{prefix_label}{self.COLOR_RESET} {message}")
                else:
                    print(message)
                self._redraw_input()
            else:
                if prefix_color and prefix_label:
                    print(f"{self.get_timestamp()}{prefix_color}{prefix_label}{self.COLOR_RESET} {message}")
                else:
                    print(message)

    def print_info(self, message):
        self._safe_print(message, self.COLOR_BLUE, '[INFO]')

    def print_success(self, message):
        self._safe_print(message, self.COLOR_GREEN, '[SUCCESS]')

    def print_warning(self, message):
        self._safe_print(message, self.COLOR_YELLOW, '[WARNING]')

    def print_error(self, message):
        self._safe_print(message, self.COLOR_RED, '[ERROR]')

    def print_sent(self, message):
        self._safe_print(message, self.COLOR_GREEN, '[SENT]')

    def print_chat(self, message):
        self._safe_print(message, self.COLOR_WHITE, '[CHAT]')

    def print_alert(self, message):
        self._safe_print(message, self.COLOR_MAGENTA, '[ALERT]')

    def print_section(self, title):
        with self._print_lock:
            if self._input_active:
                sys.stdout.write('\r\033[K')
            print(f"\n{self.COLOR_CYAN}{'='*60}{self.COLOR_RESET}")
            print(f"{self.COLOR_CYAN}{title.center(60)}{self.COLOR_RESET}")
            print(f"{self.COLOR_CYAN}{'='*60}{self.COLOR_RESET}\n")
            if self._input_active:
                self._redraw_input()

    def print_raw(self, message):
        self._safe_print(message)

    def set_autocomplete_items(self, items):
        self._ac_items = list(items) if items else []

    def _filtered_ac(self, prefix):
        if not self._ac_items:
            return []
        if not prefix:
            return list(self._ac_items)
        low = prefix.lower()
        return [s for s in self._ac_items if s.lower().startswith(low)]

    def _active_pool(self, use_ac):
        if not use_ac or not self._ac_enabled or not self._ac_items:
            return []
        if self._ac_pool is not None:
            return self._ac_pool
        return self._filtered_ac(self._input_buffer)

    def _current_suggestion(self, use_ac=True):
        pool = self._active_pool(use_ac)
        if not pool or not self._input_buffer:
            return None
        idx = self._ac_index if 0 <= self._ac_index < len(pool) else 0
        item = pool[idx]
        if len(item) > len(self._input_buffer) and item[:len(self._input_buffer)].lower() == self._input_buffer.lower():
            return item
        return None

    def _redraw_input(self, use_ac=True):
        sys.stdout.write('\r\033[K')
        sys.stdout.write(self._input_prompt + self._input_buffer)
        sugg = self._current_suggestion(use_ac)
        if sugg is not None:
            sys.stdout.write(self.COLOR_DARK + sugg[len(self._input_buffer):] + self.COLOR_RESET)
        sys.stdout.flush()

    def _reset_ac(self):
        self._ac_index = -1
        self._ac_pool = None

    def get_input(self, prompt, use_ac=True):
        if os.name == 'nt' and sys.stdin is not None and sys.stdin.isatty():
            return self._get_input_msvcrt(prompt, use_ac)
        else:
            return self._get_input_standard(prompt)

    def _get_console_input_handle(self):
        if self._console_input_handle is not None:
            return self._console_input_handle
        try:
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-10)
            mode = wintypes.DWORD()
            if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                kernel32.SetConsoleMode(handle, mode.value | 0x0010)
            self._console_input_handle = handle
        except Exception:
            self._console_input_handle = False
        return self._console_input_handle

    def _read_console_event(self, handle):
        rec = _INPUT_RECORD()
        read = wintypes.DWORD()
        while True:
            ok = ctypes.windll.kernel32.ReadConsoleInputW(handle, ctypes.byref(rec), 1, ctypes.byref(read))
            if not ok:
                continue
            if rec.EventType == 1:
                ke = rec.KeyEvent
                if not ke.bKeyDown:
                    continue
                return ('key', ke.wVirtualKeyCode, ke.uChar, ke.dwControlKeyState)
            if rec.EventType == 2:
                me = rec.MouseEvent
                if me.dwEventFlags == 0x0004:
                    delta = ctypes.c_short(me.dwButtonState >> 16).value
                    return ('wheel', 1 if delta > 0 else -1, '', 0)

    def _read_event_msvcrt(self):
        import msvcrt
        ch = msvcrt.getwch()
        if ch == '\r': return ('key', 0x0D, '', 0)
        if ch == '\t': return ('key', 0x09, '', 0)
        if ch == '\x08': return ('key', 0x08, '', 0)
        if ch == '\x1b': return ('key', 0x1B, '', 0)
        if ch == '\x03': return ('key', 0x43, '', 0x0008)
        if ch == '\x1a': return ('key', 0x5A, '', 0x0008)
        if ch in ('\xe0', '\x00'):
            ext = msvcrt.getwch()
            if ext == 'H': return ('key', 0x26, '', 0)
            if ext == 'P': return ('key', 0x28, '', 0)
            return (None, 0, '', 0)
        return ('key', 0, ch, 0)

    def _get_input_msvcrt(self, prompt, use_ac):
        handle = self._get_console_input_handle()
        self._input_prompt = prompt
        self._input_buffer = ""
        self._input_active = True
        self._history_index = -1
        self._reset_ac()

        sys.stdout.write(prompt)
        sys.stdout.flush()

        while True:
            kind, vk, ch, ctrl = self._read_console_event(handle) if handle else self._read_event_msvcrt()

            if kind == 'wheel':
                pool = self._active_pool(use_ac)
                if pool and self._input_buffer:
                    if self._ac_index < 0:
                        self._ac_index = 0
                    else:
                        self._ac_index = (self._ac_index - vk) % len(pool)
                    self._redraw_input(use_ac)
                continue

            if vk == 0x0D:
                pool = self._active_pool(use_ac)
                result = pool[self._ac_index] if (0 <= self._ac_index < len(pool)) else self._input_buffer
                self._input_buffer = ""
                self._input_active = False
                self._reset_ac()
                sys.stdout.write('\n')
                sys.stdout.flush()
                if result.strip():
                    self._history.append(result.strip())
                    self._history_index = -1
                return result

            if vk == 0x09:
                pool = self._active_pool(use_ac)
                if not pool:
                    continue
                if self._ac_pool is None:
                    self._ac_pool = pool
                    self._ac_index = 0
                else:
                    self._ac_index = (self._ac_index + 1) % len(pool)
                self._input_buffer = pool[self._ac_index]
                self._history_index = -1
                self._redraw_input(use_ac)
                continue

            if vk == 0x08:
                if self._input_buffer:
                    self._input_buffer = self._input_buffer[:-1]
                    self._history_index = -1
                    self._reset_ac()
                    self._redraw_input(use_ac)
                continue

            if vk == 0x1B:
                self._input_buffer = ""
                self._history_index = -1
                self._reset_ac()
                self._redraw_input(use_ac)
                continue

            if vk in (0x26, 0x28):
                pool = self._active_pool(use_ac)
                if pool and self._input_buffer:
                    if self._ac_index < 0:
                        self._ac_index = 0
                    else:
                        step = -1 if vk == 0x26 else 1
                        self._ac_index = (self._ac_index + step) % len(pool)
                    self._redraw_input(use_ac)
                elif self._history:
                    if vk == 0x26:
                        if self._history_index < 0:
                            self._history_index = len(self._history) - 1
                        elif self._history_index > 0:
                            self._history_index -= 1
                    else:
                        if 0 <= self._history_index < len(self._history) - 1:
                            self._history_index += 1
                        else:
                            self._history_index = -1
                    self._input_buffer = self._history[self._history_index] if self._history_index >= 0 else ""
                    self._reset_ac()
                    self._redraw_input(use_ac)
                continue

            if (ctrl & 0x0007) and vk == 0x43:
                self._input_active = False
                raise KeyboardInterrupt
            if (ctrl & 0x0007) and vk == 0x5A:
                self._input_active = False
                raise EOFError

            if ch and ch.isprintable():
                self._input_buffer += ch
                self._history_index = -1
                self._reset_ac()
                self._redraw_input(use_ac)

    def _get_input_standard(self, prompt):
        self._input_active = True
        self._input_prompt = prompt
        try:
            result = input(f"{self.COLOR_CYAN}{prompt}{self.COLOR_RESET}")
            if result.strip():
                self._history.append(result.strip())
                self._history_index = -1
        finally:
            self._input_active = False
        return result
