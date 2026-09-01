import os
import sys
from datetime import datetime

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
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_banner(self):
        banner = f"""
{self.COLOR_CYAN}╔════════════════════════════════════════════════════════╗{self.COLOR_RESET}
{self.COLOR_CYAN}║{self.COLOR_RESET}    Minecraft Bot Client (MBC) v1.0.0              {self.COLOR_CYAN}║{self.COLOR_RESET}
{self.COLOR_CYAN}║{self.COLOR_RESET}    Supporting versions 1.8 - 26.2                  {self.COLOR_CYAN}║{self.COLOR_RESET}
{self.COLOR_CYAN}║{self.COLOR_RESET}    For Testing & Development Purposes Only          {self.COLOR_CYAN}║{self.COLOR_RESET}
{self.COLOR_CYAN}╚════════════════════════════════════════════════════════╝{self.COLOR_RESET}
        """
        print(banner)
    
    def get_timestamp(self):
        if self.timestamp:
            return f"[{datetime.now().strftime('%H:%M:%S')}] "
        return ""
    
    def print_info(self, message):
        print(f"{self.get_timestamp()}{self.COLOR_BLUE}[INFO]{self.COLOR_RESET} {message}")
    
    def print_success(self, message):
        print(f"{self.get_timestamp()}{self.COLOR_GREEN}[SUCCESS]{self.COLOR_RESET} {message}")
    
    def print_warning(self, message):
        print(f"{self.get_timestamp()}{self.COLOR_YELLOW}[WARNING]{self.COLOR_RESET} {message}")
    
    def print_error(self, message):
        print(f"{self.get_timestamp()}{self.COLOR_RED}[ERROR]{self.COLOR_RESET} {message}")
    
    def print_sent(self, message):
        print(f"{self.get_timestamp()}{self.COLOR_GREEN}[SENT]{self.COLOR_RESET} {message}")
    
    def print_received(self, message):
        print(f"{self.get_timestamp()}{self.COLOR_MAGENTA}[RECEIVED]{self.COLOR_RESET} {message}")
    
    def print_section(self, title):
        print(f"\n{self.COLOR_CYAN}{'='*60}{self.COLOR_RESET}")
        print(f"{self.COLOR_CYAN}{title.center(60)}{self.COLOR_RESET}")
        print(f"{self.COLOR_CYAN}{'='*60}{self.COLOR_RESET}\n")
    
    def get_input(self, prompt):
        return input(f"{self.COLOR_CYAN}{prompt}{self.COLOR_RESET}")
