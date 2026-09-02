import sys
import traceback

def main():
    from src.client.minecraft_bot_client import MinecraftBotClient
    client = MinecraftBotClient()
    client.run()
    # 连接失败时也会走到这里，暂停让用户看到提示信息，避免窗口直接关闭
    if not client.connected:
        print("\n未能连接到服务器，程序已退出。")
        try:
            input("按 Enter 键关闭窗口...")
        except Exception:
            pass

def pause_on_error():
    try:
        input("按 Enter 键关闭窗口...")
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
        # 捕获所有未处理异常，打印详细信息并暂停，防止窗口闪退看不到错误
        print("\n" + "=" * 60)
        print("程序发生错误，详细信息如下：")
        print("=" * 60)
        traceback.print_exc()
        pause_on_error()
