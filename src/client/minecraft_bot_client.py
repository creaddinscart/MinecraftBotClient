import os
import random
import string
from src import i18n
from src.network.version_checker import VersionChecker
from src.network.connection_manager import ConnectionManager
from src.settings.settings_manager import SettingsManager
from src.ui.console_ui import ConsoleUI
from src.features.spam import SpamManager

class MinecraftBotClient:
    def __init__(self):
        self.settings = SettingsManager()
        i18n.set_language(self.settings.get_language())
        self.ui = ConsoleUI()
        self.version_checker = VersionChecker()
        self.connection_manager = ConnectionManager()
        self.username = None
        self.current_version = None
        self.connected = False
        self.spam_manager = None

    def run(self):
        self.ui.clear_screen()
        self.ui.print_banner()

        self.check_version()
        self.apply_config()
        self.connect_to_server()
        self.chat_loop()

    def check_version(self):
        try:
            latest_version = self.version_checker.fetch_latest_version()
            current_version = self.settings.get_current_version()
            if latest_version and current_version != latest_version:
                self.ui.print_warning(i18n.t('label_new_version', ver=latest_version))
            self.current_version = current_version
        except Exception:
            self.current_version = self.settings.get_current_version()

    def apply_config(self):
        self.username = self.settings.get_username().strip() or self.generate_random_username()
        self.ui.print_section(i18n.t('section_player_info'))
        self.ui.print_info(f"{i18n.t('label_server')}: {self.settings.get_server_address()}")
        self.ui.print_info(f"{i18n.t('label_version')}: {self.settings.get_minecraft_version()}")
        self.ui.print_info(f"{i18n.t('label_username')}: {self.username}")

    def generate_random_username(self):
        prefixes = ["Bot", "Player", "Client", "Agent", "Miner", "Digger"]
        prefix = random.choice(prefixes)
        suffix = ''.join(random.choices(string.digits, k=4))
        return f"{prefix}{suffix}"

    def connect_to_server(self):
        self.ui.print_section(i18n.t('section_connecting'))

        server_address = self.settings.get_server_address()
        version = self.settings.get_minecraft_version()

        if not self.connection_manager.is_version_supported(version):
            self.ui.print_warning(i18n.t('label_unknown_version', ver=version))

        self.ui.print_info(i18n.t('label_connecting_to', addr=server_address))

        try:
            self.connection_manager.connect(
                server_address=server_address,
                username=self.username,
                protocol_version=version,
                on_chat=self.on_chat_received,
                on_disconnect=self.on_disconnected,
                log_func=self.ui.print_info
            )
            self.connected = True
            self.ui.print_success(i18n.t('label_connected'))
            self.ui.print_info(i18n.t('label_prompt_exit'))

            self.spam_manager = SpamManager(
                self.connection_manager,
                log_func=self.ui.print_info,
                sent_func=lambda msg: self.ui.print_sent(i18n.t('label_sent', text=msg))
            )
            self.spam_manager.rate = self.settings.get_spam_rate()
            self.spam_manager.messages = list(self.settings.get_spam_messages())
            if self.settings.get_spam_enabled() and self.spam_manager.messages:
                self.spam_manager.start()

        except Exception as e:
            self.ui.print_error(i18n.t('label_connection_failed', err=str(e)))
            self.connected = False

    def on_chat_received(self, text):
        self.ui.print_chat(text)

    def on_disconnected(self):
        if self.connected:
            self.ui.print_warning(i18n.t('label_disconnected_by_server'))
        if self.spam_manager:
            self.spam_manager.stop()

    def chat_loop(self):
        if not self.connected:
            self.ui.print_error(i18n.t('label_not_connected'))
            return

        while self.connected:
            try:
                message = self.ui.get_input(i18n.t('label_prompt_input', user=self.username)).strip()

                if not message:
                    continue

                lower = message.lower()

                if lower == "exit":
                    self.disconnect()
                    break
                elif lower == "help" or lower == "/help":
                    self.show_help()
                elif lower == "/settings":
                    self.show_settings()
                elif lower.startswith("/spam"):
                    self.handle_spam_command(message)
                elif message.startswith("/"):
                    self.connection_manager.send_chat(message)
                    self.ui.print_sent(i18n.t('label_sent', text=message))
                else:
                    self.connection_manager.send_chat(message)
                    self.ui.print_sent(i18n.t('label_sent', text=message))

            except EOFError:
                self.disconnect()
                break
            except KeyboardInterrupt:
                self.disconnect()
                break
            except Exception as e:
                self.ui.print_error(i18n.t('label_error', err=str(e)))
                if not self.connection_manager.is_alive():
                    self.connected = False

    def handle_spam_command(self, command):
        parts = command.split(maxsplit=2)
        if len(parts) < 2:
            self.ui.print_info(i18n.t('label_spam_usage'))
            return

        sub = parts[1].lower()

        if sub == "on":
            self.spam_manager.start()
        elif sub == "off":
            self.spam_manager.stop()
        elif sub == "rate":
            if len(parts) < 3:
                self.ui.print_info(f"Current rate: {self.spam_manager.rate} msg/s")
            else:
                self.spam_manager.set_rate(parts[2])
                self._save_spam_config()
        elif sub == "add":
            if len(parts) < 3:
                self.ui.print_info("Usage: /spam add <message>")
            else:
                self.spam_manager.add_message(parts[2])
                self._save_spam_config()
        elif sub == "remove":
            if len(parts) < 3:
                self.ui.print_info("Usage: /spam remove <index>")
            else:
                self.spam_manager.remove_message(parts[2])
                self._save_spam_config()
        elif sub == "list":
            self.spam_manager.list_messages()
        elif sub == "clear":
            self.spam_manager.clear_messages()
            self._save_spam_config()
        elif sub == "status":
            self.spam_manager.show_status()
        else:
            self.ui.print_info(i18n.t('label_spam_usage'))

    def _save_spam_config(self):
        if self.spam_manager:
            self.settings.update_spam_config(
                self.spam_manager.enabled,
                self.spam_manager.rate,
                self.spam_manager.messages
            )

    def show_help(self):
        self.ui.print_section(i18n.t('section_help'))
        commands = [
            (i18n.t('label_command_help'), i18n.t('label_command_desc_help')),
            (i18n.t('label_command_settings'), i18n.t('label_command_desc_settings')),
            (i18n.t('label_command_spam'), i18n.t('label_command_desc_spam')),
            (i18n.t('label_command_exit'), i18n.t('label_command_desc_exit')),
        ]
        for cmd, desc in commands:
            self.ui.print_info(f"{cmd:<20} - {desc}")
        self.ui.print_info("")
        self.ui.print_info("Any message starting with / will be sent as a server command")
        self.ui.print_info("Any other text will be sent as chat")

    def show_settings(self):
        self.ui.print_section(i18n.t('section_settings'))
        self.ui.print_info(f"{i18n.t('label_server')}: {self.settings.get_server_address()}")
        self.ui.print_info(f"{i18n.t('label_version')}: {self.settings.get_minecraft_version()}")
        self.ui.print_info(f"{i18n.t('label_username')}: {self.username}")
        if self.spam_manager:
            self.spam_manager.show_status()

    def disconnect(self):
        if self.spam_manager:
            self.spam_manager.stop()
            self._save_spam_config()

        try:
            self.connection_manager.disconnect()
        except Exception:
            pass

        self.connected = False
        self.ui.print_success(i18n.t('label_disconnected'))
