import os
import random
import string
import webbrowser
from src import i18n
from src.logger import SessionLogger, strip_ansi
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
        self.logger = SessionLogger(self.settings.get_base_dir(), enabled=self.settings.get_log_enabled())
        self.spam = None
        self.username = None
        self.connected = False

    def run(self):
        self.ui.clear_screen()
        self.ui.print_banner()
        self.logger.log("START", f"MBC {self.settings.get_current_version()} launched, language={self.settings.get_language()}")

        self.remote_check()
        self.apply_config()

        while True:
            if not self.connected:
                self.connect_to_server()
            if self.connected:
                action = self.chat_loop()
                if action == 'exit':
                    break
                self.connected = False
            action = self.idle_loop()
            if action == 'exit':
                break

        self.logger.log("STOP", "MBC exited")
        self.logger.close()
        self.ui.print_success(i18n.t('label_goodbye'))

    def remote_check(self):
        try:
            latest, _ = self.version_checker.fetch_version_info()
            current = self.settings.get_current_version()
            if latest and latest != current:
                self._ui_event('print_warning', 'UPDATE', i18n.t('label_new_version', ver=latest, cur=current))
            else:
                self._ui_event('print_info', 'VERSION', i18n.t('label_version_same', cur=current))
        except Exception:
            self.logger.log("VERSION", "Version check failed (offline?)")

        self.ui.print_section(i18n.t('section_announcement'))
        try:
            announcement = self.version_checker.fetch_announcement()
            if announcement:
                for line in announcement.splitlines():
                    self.ui.print_raw(line)
                    self.logger.log("ANNOUNCE", strip_ansi(line))
            else:
                self.ui.print_info(i18n.t('label_announcement_none'))
        except Exception:
            self.ui.print_info(i18n.t('label_announcement_fail'))
            self.logger.log("ANNOUNCE", "Announcement fetch failed")

    def apply_config(self):
        self.username = self.settings.get_username().strip() or self.generate_random_username()
        self.ui.print_section(i18n.t('section_player_info'))
        self._ui_event('print_info', 'CONFIG', f"{i18n.t('label_server')}: {self.settings.get_server_address()}")
        self._ui_event('print_info', 'CONFIG', f"{i18n.t('label_version')}: {self.settings.get_minecraft_version()}")
        self._ui_event('print_info', 'CONFIG', f"{i18n.t('label_username')}: {self.username}")
        log_state = i18n.t('label_log_state_on') if self.logger.enabled else i18n.t('label_log_state_off')
        self._ui_event('print_info', 'CONFIG', log_state)

    def generate_random_username(self):
        prefixes = ["Bot", "Player", "Client", "Agent", "Miner", "Digger"]
        prefix = random.choice(prefixes)
        suffix = ''.join(random.choices(string.digits, k=4))
        return f"{prefix}{suffix}"

    def connect_to_server(self):
        self.ui.print_section(i18n.t('section_connecting'))

        server_address = self.settings.get_server_address()
        version = self.settings.get_minecraft_version()

        protocol_id, exact = ConnectionManager.resolve_protocol(version)
        if not self.connection_manager.is_version_supported(version):
            self._ui_event('print_warning', 'VERSION', i18n.t('label_unknown_version', ver=version))
        elif not exact:
            self._ui_event('print_info', 'VERSION', i18n.t('label_version_mapped', ver=version, pid=protocol_id))

        self._ui_event('print_info', 'CONNECT', i18n.t('label_connecting_to', addr=server_address))

        try:
            self.connection_manager.connect(
                server_address=server_address,
                username=self.username,
                protocol_version=version,
                on_chat=self.on_chat_received,
                on_disconnect=self.on_disconnected,
                log_func=self._net_log
            )
            self.connected = True
            self._ui_event('print_success', 'CONNECT', i18n.t('label_connected'))
            self._ui_event('print_info', 'CONNECT', i18n.t('label_prompt_exit'))

            self.spam = SpamManager(
                self.connection_manager,
                log_func=lambda m: self._ui_event('print_info', 'SPAM', m),
                sent_func=lambda m: self._ui_event('print_sent', 'SPAM', m)
            )
            self.spam.rate = self.settings.get_spam_rate()
            self.spam.messages = self.settings.get_spam_messages()
            if self.settings.get_spam_enabled() and self.spam.messages:
                self.spam.start()

        except Exception as e:
            self._ui_event('print_error', 'CONNECT', i18n.t('label_connection_failed', err=str(e)))
            self.connected = False

    def _net_log(self, message):
        self.ui.print_info(message)
        self.logger.log("NET", message)

    def _ui_event(self, method, category, message):
        getattr(self.ui, method)(message)
        self.logger.log(category, message)

    def on_chat_received(self, text):
        self.ui.print_chat(i18n.t('label_chat', text=text))
        self.logger.log("CHAT", strip_ansi(text))

    def on_disconnected(self):
        if self.spam and self.spam.enabled:
            self.spam.stop()
        if self.connected:
            self._ui_event('print_warning', 'DISCONNECT', i18n.t('label_disconnected_by_server'))

    def chat_loop(self):
        while self.connected:
            try:
                message = self.ui.get_input(i18n.t('label_prompt_input', user=self.username)).strip()

                if not message:
                    continue

                if message.startswith("//"):
                    action = self.handle_client_command(message, allow_connect=False)
                    if action == 'exit':
                        return 'exit'
                    if action == 'esc':
                        return 'esc'
                    continue

                if message.startswith("/"):
                    self.connection_manager.send_chat(message)
                    self._ui_event('print_sent', 'SERVERCMD', i18n.t('label_sent', text=message))
                else:
                    self.connection_manager.send_chat(message)
                    self._ui_event('print_sent', 'SEND', i18n.t('label_sent', text=message))

            except EOFError:
                self.disconnect()
                return 'exit'
            except KeyboardInterrupt:
                self.disconnect()
                return 'exit'
            except Exception as e:
                self._ui_event('print_error', 'ERROR', i18n.t('label_error', err=str(e)))
                if not self.connection_manager.is_alive():
                    self.connected = False

        return 'esc'

    def idle_loop(self):
        self.ui.print_info(i18n.t('label_not_connected_hint'))
        self.logger.log("IDLE", "Entered idle state")
        while True:
            try:
                message = self.ui.get_input(i18n.t('label_idle_prompt')).strip()
            except (EOFError, KeyboardInterrupt):
                return 'exit'

            if not message:
                continue

            if message.startswith("//"):
                action = self.handle_client_command(message, allow_connect=True)
                if action == 'exit':
                    return 'exit'
                if action == 'reconnect':
                    return 'reconnect'
            else:
                self.ui.print_info(i18n.t('label_not_connected_hint'))

    def handle_client_command(self, message, allow_connect):
        parts = message[2:].strip().split()
        cmd = parts[0].lower() if parts else "help"
        args = parts[1:]
        self.logger.log("MBC", f"Client command: {message}")

        if cmd == "help":
            self.show_help()
            return None

        if cmd == "esc":
            if self.connected:
                self.disconnect()
            self._ui_event('print_warning', 'MBC', i18n.t('label_esc_done'))
            return 'esc'

        if cmd == "exit":
            if self.connected:
                self.disconnect()
            return 'exit'

        if cmd == "connect":
            if self.connected:
                self.ui.print_info(i18n.t('label_already_connected'))
                return None
            if allow_connect:
                self.ui.print_info(i18n.t('label_reconnecting'))
                return 'reconnect'
            return None

        if cmd == "log":
            return self.handle_log_command(args)

        if cmd == "spam":
            return self.handle_spam_command(args)

        self._ui_event('print_warning', 'MBC', i18n.t('label_unknown_command'))
        return None

    def handle_log_command(self, args):
        if not args:
            self.ui.print_info(i18n.t('label_log_usage'))
            state = i18n.t('label_log_state_on') if self.logger.enabled else i18n.t('label_log_state_off')
            self.ui.print_info(state)
            return None

        value = args[0].lower()
        if value in ("true", "on", "1", "enable", "enabled"):
            path = self.logger.enable()
            self.settings.set_log_enabled(True)
            if path:
                self._ui_event('print_success', 'LOG', i18n.t('label_log_on', path=path))
            else:
                self.ui.print_error(i18n.t('label_log_usage'))
        elif value in ("false", "off", "0", "disable", "disabled"):
            self.logger.disable()
            self.settings.set_log_enabled(False)
            self._ui_event('print_info', 'LOG', i18n.t('label_log_off'))
        else:
            self.ui.print_info(i18n.t('label_log_usage'))
        return None

    def handle_spam_command(self, args):
        if not self.spam:
            self.ui.print_info(i18n.t('label_spam_not_ready'))
            return None

        if not args:
            self.spam.show_status()
            self.settings.save_spam_config(self.spam.enabled, self.spam.rate, self.spam.messages)
            return None

        sub = args[0].lower()
        remaining = args[1:]

        if sub in ("on", "start"):
            self.spam.start()
        elif sub in ("off", "stop"):
            self.spam.stop()
        elif sub == "rate":
            if not remaining:
                self.ui.print_info(f"Rate: {self.spam.rate} msg/s")
            else:
                self.spam.set_rate(remaining[0])
        elif sub == "add":
            if not remaining:
                self.ui.print_info(i18n.t('label_spam_usage'))
            else:
                self.spam.add_message(" ".join(remaining))
        elif sub == "remove":
            if not remaining:
                self.ui.print_info(i18n.t('label_spam_usage'))
            else:
                self.spam.remove_message(remaining[0])
        elif sub == "list":
            self.spam.list_messages()
        elif sub == "clear":
            self.spam.clear_messages()
        elif sub == "status":
            self.spam.show_status()
        else:
            self.ui.print_info(i18n.t('label_spam_usage'))

        self.settings.save_spam_config(self.spam.enabled, self.spam.rate, self.spam.messages)
        return None

    def show_help(self):
        self.ui.print_section(i18n.t('section_help'))
        commands = [
            (i18n.t('label_command_help'), i18n.t('label_command_desc_help')),
            (i18n.t('label_command_esc'), i18n.t('label_command_desc_esc')),
            (i18n.t('label_command_connect'), i18n.t('label_command_desc_connect')),
            (i18n.t('label_command_log'), i18n.t('label_command_desc_log')),
            (i18n.t('label_command_spam'), i18n.t('label_command_desc_spam')),
            (i18n.t('label_command_exit'), i18n.t('label_command_desc_exit')),
            (i18n.t('label_command_server'), i18n.t('label_command_desc_server')),
            (i18n.t('label_command_chat'), i18n.t('label_command_desc_chat')),
        ]
        for cmd, desc in commands:
            self.ui.print_info(f"{cmd:<22} - {desc}")
        self.ui.print_info("")
        self.ui.print_info(i18n.t('label_website', url=i18n.WEBSITE_URL))
        try:
            webbrowser.open(i18n.WEBSITE_URL)
            self.ui.print_info(i18n.t('label_website_opening'))
        except Exception:
            pass

    def disconnect(self):
        if self.spam and self.spam.enabled:
            self.spam.stop()
            self.settings.save_spam_config(self.spam.enabled, self.spam.rate, self.spam.messages)
        try:
            self.connection_manager.disconnect()
        except Exception:
            pass
        self.connected = False
        self.logger.log("DISCONNECT", "Disconnected from server")
        self.ui.print_success(i18n.t('label_disconnected'))
