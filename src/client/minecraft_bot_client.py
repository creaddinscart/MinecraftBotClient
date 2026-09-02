import os
import random
import string
from src import i18n
from src.network.version_checker import VersionChecker
from src.network.connection_manager import ConnectionManager
from src.settings.settings_manager import SettingsManager
from src.ui.console_ui import ConsoleUI

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
        except Exception as e:
            self.ui.print_error(i18n.t('label_connection_failed', err=str(e)))
            self.connected = False

    def on_chat_received(self, text):
        self.ui.print_info(i18n.t('label_chat', text=text))

    def on_disconnected(self):
        if self.connected:
            self.ui.print_warning(i18n.t('label_disconnected_by_server'))

    def chat_loop(self):
        if not self.connected:
            self.ui.print_error(i18n.t('label_not_connected'))
            return

        while self.connected:
            try:
                message = self.ui.get_input(i18n.t('label_prompt_input', user=self.username)).strip()

                if not message:
                    continue

                if message.lower() == "exit":
                    self.disconnect()
                    break
                elif message.lower() == "help":
                    self.show_help()
                elif message.lower() == "/settings":
                    self.show_settings()
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

    def show_help(self):
        self.ui.print_section(i18n.t('section_help'))
        commands = [
            (i18n.t('label_command_settings'), i18n.t('label_command_desc_settings')),
            (i18n.t('label_command_exit'), i18n.t('label_command_desc_exit'))
        ]
        for cmd, desc in commands:
            self.ui.print_info(f"{cmd:<20} - {desc}")

    def show_settings(self):
        self.ui.print_section(i18n.t('section_settings'))
        self.ui.print_info(f"{i18n.t('label_server')}: {self.settings.get_server_address()}")
        self.ui.print_info(f"{i18n.t('label_version')}: {self.settings.get_minecraft_version()}")
        self.ui.print_info(f"{i18n.t('label_username')}: {self.username}")

    def disconnect(self):
        try:
            self.connection_manager.disconnect()
        except Exception:
            pass

        self.connected = False
        self.ui.print_success(i18n.t('label_disconnected'))
