import sys
import os
from src.client.minecraft_bot_client import MinecraftBotClient

def main():
    client = MinecraftBotClient()
    client.run()

if __name__ == "__main__":
    main()
