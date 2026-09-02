import sys
import traceback
from src import i18n

def main():
    from src.client.minecraft_bot_client import MinecraftBotClient
    client = MinecraftBotClient()
    client.run()
    if not client.connected:
        print()
        print(i18n.t('label_not_connected_exit'))
        try:
            input(i18n.t('label_pause_on_close'))
        except Exception:
            pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except SystemExit:
        raise
    except Exception:
        print()
        print("=" * 60)
        print(i18n.t('section_error'))
        print("=" * 60)
        traceback.print_exc()
        try:
            input(i18n.t('label_pause_on_close'))
        except Exception:
            pass
