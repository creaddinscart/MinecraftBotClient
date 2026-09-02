import random
import string
from src.network.version_checker import VersionChecker
from src.network.connection_manager import ConnectionManager
from src.protocol.protocol_handler import ProtocolHandler
from src.settings.settings_manager import SettingsManager
from src.ui.console_ui import ConsoleUI

class MinecraftBotClient:
    def __init__(self):
        self.settings = SettingsManager()
        self.ui = ConsoleUI()
        self.version_checker = VersionChecker()
        self.connection_manager = ConnectionManager()
        self.protocol_handler = ProtocolHandler()
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
        # 静默检查更新，不阻塞进入服务器
        try:
            latest_version = self.version_checker.fetch_latest_version()
            current_version = self.settings.get_current_version()
            if latest_version and current_version != latest_version:
                self.ui.print_warning(f"New version available: {latest_version}")
            self.current_version = current_version
        except Exception:
            self.current_version = self.settings.get_current_version()

    def apply_config(self):
        # 从 config.json 读取配置，直接以玩家身份加入服务器，不再交互式询问
        self.username = self.settings.get_username().strip() or self.generate_random_username()
        self.ui.print_section("Player Info")
        self.ui.print_info(f"Server: {self.settings.get_server_address()}")
        self.ui.print_info(f"Version: {self.settings.get_minecraft_version()}")
        self.ui.print_info(f"Username: {self.username}")

    def generate_random_username(self):
        prefixes = ["Bot", "Player", "Client", "Agent", "Miner", "Digger"]
        prefix = random.choice(prefixes)
        suffix = ''.join(random.choices(string.digits, k=4))
        return f"{prefix}{suffix}"

    def connect_to_server(self):
        self.ui.print_section("Connecting to Server")

        server_address = self.settings.get_server_address()
        version = self.settings.get_minecraft_version()

        if not self.connection_manager.is_version_supported(version):
            self.ui.print_warning(f"Unknown version '{version}', falling back to 1.8 protocol")

        self.ui.print_info(f"Connecting to {server_address}...")

        try:
            self.connection_manager.connect(
                server_address=server_address,
                username=self.username,
                protocol_version=version
            )
            self.connected = True
            self.ui.print_success("Connected to server successfully!")
        except Exception as e:
            self.ui.print_error(f"Connection failed: {str(e)}")
            self.connected = False

    def chat_loop(self):
        if not self.connected:
            self.ui.print_error("Not connected to server")
            return

        self.ui.print_section("Chat Mode Active")
        self.ui.print_info("Type message and press Enter to send, 'exit' to quit")

        while self.connected:
            try:
                message = self.ui.get_input(f"[{self.username}]: ").strip()

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
                    self.send_message(message)

            except EOFError:
                # 外部程序通过 stdin 管道输入结束（管道关闭）时自动退出
                self.disconnect()
                break
            except KeyboardInterrupt:
                self.disconnect()
                break
            except Exception as e:
                self.ui.print_error(f"Error: {str(e)}")

    def send_message(self, message):
        try:
            self.protocol_handler.send_chat_message(
                self.connection_manager.get_connection(),
                message
            )
            self.ui.print_sent(message)
        except Exception as e:
            self.ui.print_error(f"Failed to send message: {str(e)}")

    def show_help(self):
        self.ui.print_section("Available Commands")
        commands = [
            ("/settings", "View current settings"),
            ("exit", "Disconnect and exit")
        ]
        for cmd, desc in commands:
            self.ui.print_info(f"{cmd:<20} - {desc}")

    def show_settings(self):
        self.ui.print_section("Current Settings")
        self.ui.print_info(f"Server: {self.settings.get_server_address()}")
        self.ui.print_info(f"Version: {self.settings.get_minecraft_version()}")
        self.ui.print_info(f"Username: {self.username}")

    def disconnect(self):
        try:
            self.connection_manager.disconnect()
        except Exception:
            pass

        self.connected = False
        self.ui.print_success("Disconnected from server")
