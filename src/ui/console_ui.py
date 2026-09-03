import os
import sys
import threading
from datetime import datetime
from src import i18n

class ConsoleUI:
    COLOR_RESET = '\033[0m'
    COLOR_RED = '\033[91m'
    COLOR_GREEN = '\033[92m'
    COLOR_YELLOW = '\033[93m'
    COLOR_BLUE = '\033[94m'
    COLOR_MAGENTA = '\033[95m'
    COLOR_CYAN = '\033[96m'
    COLOR_WHITE = '\033[97m'

    def __init__(self):
        self.timestamp = True
        self._input_active = False
        self._input_buffer = ""
        self._input_prompt = ""
        self._print_lock = threading.Lock()
        self._enable_windows_ansi()

    def _enable_windows_ansi(self):
        if os.name != 'nt':
            return
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-11)
            mode = ctypes.c_uint32()
            if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                kernel32.SetConsoleMode(handle, mode.value | 0x0004)
        except Exception:
            pass

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

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
                sys.stdout.write(f'\r{self._input_prompt}{self._input_buffer}')
                sys.stdout.flush()
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

    def print_section(self, title):
        with self._print_lock:
            if self._input_active:
                sys.stdout.write('\r\033[K')
            print(f"\n{self.COLOR_CYAN}{'='*60}{self.COLOR_RESET}")
            print(f"{self.COLOR_CYAN}{title.center(60)}{self.COLOR_RESET}")
            print(f"{self.COLOR_CYAN}{'='*60}{self.COLOR_RESET}\n")
            if self._input_active:
                sys.stdout.write(f'\r{self._input_prompt}{self._input_buffer}')
                sys.stdout.flush()

    def print_raw(self, message):
        self._safe_print(message)

    def get_input(self, prompt):
        if os.name == 'nt':
            return self._get_input_msvcrt(prompt)
        else:
            return self._get_input_standard(prompt)

    def _get_input_msvcrt(self, prompt):
        import msvcrt
        self._input_prompt = prompt
        self._input_buffer = ""
        self._input_active = True

        sys.stdout.write(prompt)
        sys.stdout.flush()

        while True:
            ch = msvcrt.getwch()

            if ch == '\r':
                result = self._input_buffer
                self._input_buffer = ""
                self._input_active = False
                sys.stdout.write('\n')
                sys.stdout.flush()
                return result

            elif ch == '\x08':
                if self._input_buffer:
                    self._input_buffer = self._input_buffer[:-1]
                    sys.stdout.write('\r\033[K')
                    sys.stdout.write(f'{self._input_prompt}{self._input_buffer}')
                    sys.stdout.flush()

            elif ch == '\x03':
                self._input_active = False
                raise KeyboardInterrupt

            elif ch == '\x1a':
                self._input_active = False
                raise EOFError

            elif ch == '\x1b':
                self._input_buffer = ""
                sys.stdout.write('\r\033[K')
                sys.stdout.write(self._input_prompt)
                sys.stdout.flush()

            elif ch == '\x00' or ch == '\xe0':
                msvcrt.getwch()

            elif ch.isprintable():
                self._input_buffer += ch
                sys.stdout.write(ch)
                sys.stdout.flush()

    def _get_input_standard(self, prompt):
        self._input_active = True
        self._input_prompt = prompt
        try:
            result = input(f"{self.COLOR_CYAN}{prompt}{self.COLOR_RESET}")
        finally:
            self._input_active = False
        return result
