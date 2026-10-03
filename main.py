import os
import sys
import time
import signal
import warnings
import traceback

warnings.filterwarnings('ignore', module='urllib3')

from src import i18n
from src.client.minecraft_bot_client import MinecraftBotClient
from src.settings.settings_manager import SettingsManager

def configure_console():
    if os.name == 'nt':
        return
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass

def install_signal_handlers():
    if os.name == 'nt':
        return
    def on_terminate(signum, frame):
        raise SystemExit(0)
    for name in ('SIGTERM', 'SIGHUP'):
        sig = getattr(signal, name, None)
        if sig is None:
            continue
        try:
            signal.signal(sig, on_terminate)
        except Exception:
            pass

def main():
    configure_console()
    install_signal_handlers()
    settings = SettingsManager()
    i18n.set_language(settings.get_language())

    if getattr(sys, 'frozen', False):
        try:
            from src.ui.console_ui import ConsoleUI
            ui = ConsoleUI()
            ui.show_loading(fast_start=settings.get_fast_start())
            ui.print_banner()
        except Exception:
            pass

    try:
        client = MinecraftBotClient()
        client.run()
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception:
        from src.ui.console_ui import ConsoleUI
        ui = ConsoleUI()
        ui.print_section(i18n.t('section_error'))
        traceback.print_exc()
        from src import i18n as i
        try:
            msg = i18n.t('label_not_connected_exit')
            print(msg)
        except Exception:
            pass
        try:
            prompt = i18n.t('label_pause_prompt')
            input(prompt)
        except Exception:
            time.sleep(3)

if __name__ == "__main__":
    main()
