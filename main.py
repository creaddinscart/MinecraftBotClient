import os
import sys
import time
import traceback
from src import i18n
from src.client.minecraft_bot_client import MinecraftBotClient
from src.settings.settings_manager import SettingsManager

def main():
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
