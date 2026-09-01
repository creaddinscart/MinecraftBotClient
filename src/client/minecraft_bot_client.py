import os
import sys
import json
import random
import string
import time
import threading
from datetime import datetime
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
        self.spam_thread = None
        self.spam_running = False
        
    def run(self):
        self.ui.clear_screen()
        self.ui.print_banner()
        
        self.ui.print_info("Checking for updates...")
        self.check_version()
        
        self.ui.print_section("Welcome to Minecraft Bot Client")
        self.setup_username()
        self.setup_settings()
        self.connect_to_server()
        self.chat_loop()
    
    def check_version(self):
        try:
            latest_version = self.version_checker.fetch_latest_version()
            current_version = self.settings.get_current_version()
            
            if latest_version and current_version != latest_version:
                self.ui.print_warning(f"New version available: {latest_version}")
                self.ui.print_info(f"Current version: {current_version}")
            else:
                self.ui.print_success(f"Running latest version: {current_version}")
            
            self.current_version = current_version
        except Exception as e:
            self.ui.print_error(f"Version check failed: {str(e)}")
            self.current_version = self.settings.get_current_version()
    
    def setup_username(self):
        self.ui.print_section("Username Setup")
        choice = self.ui.get_input("Enter username or press Enter for random generation: ").strip()
        
        if choice:
            self.username = choice
        else:
            self.username = self.generate_random_username()
        
        self.ui.print_success(f"Username set to: {self.username}")
    
    def generate_random_username(self):
        prefixes = ["Bot", "Player", "Client", "Agent", "Miner", "Digger"]
        prefix = random.choice(prefixes)
        suffix = ''.join(random.choices(string.digits, k=4))
        return f"{prefix}{suffix}"
    
    def setup_settings(self):
        self.ui.print_section("Settings Configuration")
        
        server_address = self.ui.get_input("Enter server address (default: localhost:25565): ").strip()
        if not server_address:
            server_address = "localhost:25565"
        
        version_choice = self.ui.get_input("Enter Minecraft version (1.8-26.2, default: 1.8.9): ").strip()
        if not version_choice:
            version_choice = "1.8.9"
        
        spam_interval = self.ui.get_input("Enter spam message interval in seconds (default: 5): ").strip()
        try:
            spam_interval = float(spam_interval) if spam_interval else 5
        except ValueError:
            spam_interval = 5
        
        self.settings.set_server_address(server_address)
        self.settings.set_minecraft_version(version_choice)
        self.settings.set_spam_interval(spam_interval)
        
        self.ui.print_success("Settings configured successfully")
    
    def connect_to_server(self):
        self.ui.print_section("Connecting to Server")
        
        server_address = self.settings.get_server_address()
        version = self.settings.get_minecraft_version()
        
        self.ui.print_info(f"Connecting to {server_address}...")
        self.ui.print_info(f"Protocol version: {version}")
        self.ui.print_info(f"Username: {self.username}")
        
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
        self.ui.print_info("Type 'help' for commands, 'exit' to quit")
        
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
                elif message.lower().startswith("/spam "):
                    spam_message = message[6:].strip()
                    count = self.ui.get_input("Number of times to spam (default: 10): ").strip()
                    try:
                        count = int(count) if count else 10
                    except ValueError:
                        count = 10
                    self.start_spam(spam_message, count)
                elif message.lower() == "/stopspam":
                    self.stop_spam()
                elif message.lower() == "/settings":
                    self.show_settings()
                else:
                    self.send_message(message)
            
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
    
    def start_spam(self, message, count):
        if self.spam_running:
            self.ui.print_warning("Spam already running")
            return
        
        self.spam_running = True
        interval = self.settings.get_spam_interval()
        
        def spam_worker():
            for i in range(count):
                if not self.spam_running:
                    break
                self.send_message(message)
                time.sleep(interval)
            self.spam_running = False
            self.ui.print_success(f"Spam completed: {count} messages sent")
        
        self.spam_thread = threading.Thread(target=spam_worker, daemon=True)
        self.spam_thread.start()
        self.ui.print_info(f"Spamming '{message}' {count} times with {interval}s interval")
    
    def stop_spam(self):
        if self.spam_running:
            self.spam_running = False
            self.ui.print_success("Spam stopped")
        else:
            self.ui.print_warning("No spam running")
    
    def show_help(self):
        self.ui.print_section("Available Commands")
        commands = [
            ("/spam <message>", "Start spamming a message"),
            ("/stopspam", "Stop current spam"),
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
        self.ui.print_info(f"Spam Interval: {self.settings.get_spam_interval()}s")
    
    def disconnect(self):
        self.ui.print_section("Disconnecting")
        if self.spam_running:
            self.stop_spam()
        
        try:
            self.connection_manager.disconnect()
        except Exception as e:
            self.ui.print_error(f"Disconnect error: {str(e)}")
        
        self.connected = False
        self.ui.print_success("Disconnected from server")
        self.ui.print_info("Goodbye!")
