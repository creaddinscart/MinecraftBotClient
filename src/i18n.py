import os

_translations = {
    "zh": {
        "banner_title": "Minecraft Bot Client (MBC) v1.0.1",
        "banner_sub1": "支持版本 1.8 - 26.2",
        "banner_sub2": "仅供测试与开发用途",
        "section_player_info": "玩家信息",
        "section_connecting": "正在连接服务器",
        "section_help": "可用命令",
        "section_settings": "当前设置",
        "section_error": "程序发生错误，详细信息如下",
        "label_server": "服务器",
        "label_version": "版本",
        "label_username": "用户名",
        "label_new_version": "发现新版本: {ver}",
        "label_unknown_version": "未知版本 '{ver}'，回退到 1.8 协议",
        "label_connecting_to": "正在连接 {addr}...",
        "label_connected": "已成功连接到服务器！",
        "label_disconnected_by_server": "已被服务器断开",
        "label_disconnected": "已从服务器断开",
        "label_not_connected": "未连接到服务器",
        "label_auth_failed": "服务器拒绝登录: {reason}",
        "label_online_mode_required": "该服务器为正版验证服务器，请在 config.json 中将 auth 设为 microsoft 并登录微软账号",
        "label_server_disconnected": "[服务器] 已被断开: {reason}",
        "label_connection_failed": "连接失败: {err}",
        "label_error": "错误: {err}",
        "label_chat": "[聊天] {text}",
        "label_sent": "{text}",
        "label_prompt_exit": "输入消息后按 Enter 发送，'exit' 退出，输入 /help 查看命令",
        "label_prompt_input": "[{user}]: ",
        "label_command_exit": "exit",
        "label_command_help": "help | /help",
        "label_command_settings": "/settings",
        "label_command_spam": "/spam",
        "label_command_desc_exit": "断开并退出",
        "label_command_desc_help": "查看可用命令",
        "label_command_desc_settings": "查看当前设置",
        "label_command_desc_spam": "垃圾邮件控制 (on/off/rate/add/list/clear/status)",
        "label_auth_verifying": "[授权] 正在通过 Mojang 会话服务器验证...",
        "label_pause_on_close": "按 Enter 键关闭窗口...",
        "label_not_connected_exit": "未能连接到服务器，程序已退出。",
        "label_invalid_packet": "无效数据包长度",
        "label_connection_closed": "连接已关闭",
        "label_unknown": "未知",
        "label_srv_resolved": "DNS SRV: {host} -> {target}",
        "label_spam_usage": "用法: /spam <on|off|rate <n>|add <msg>|remove <i>|list|clear|status>",
    },
    "en": {
        "banner_title": "Minecraft Bot Client (MBC) v1.0.1",
        "banner_sub1": "Supporting versions 1.8 - 26.2",
        "banner_sub2": "For Testing & Development Purposes Only",
        "section_player_info": "Player Info",
        "section_connecting": "Connecting to Server",
        "section_help": "Available Commands",
        "section_settings": "Current Settings",
        "section_error": "Program Error - Details Below",
        "label_server": "Server",
        "label_version": "Version",
        "label_username": "Username",
        "label_new_version": "New version available: {ver}",
        "label_unknown_version": "Unknown version '{ver}', falling back to 1.8 protocol",
        "label_connecting_to": "Connecting to {addr}...",
        "label_connected": "Connected to server successfully!",
        "label_disconnected_by_server": "Disconnected by server",
        "label_disconnected": "Disconnected from server",
        "label_not_connected": "Not connected to server",
        "label_auth_failed": "Login rejected by server: {reason}",
        "label_online_mode_required": "This server requires Microsoft authentication. Set auth to 'microsoft' in config.json and log in.",
        "label_server_disconnected": "[SERVER] Disconnected: {reason}",
        "label_connection_failed": "Connection failed: {err}",
        "label_error": "Error: {err}",
        "label_chat": "[CHAT] {text}",
        "label_sent": "{text}",
        "label_prompt_exit": "Type message and press Enter to send, 'exit' to quit, /help for commands",
        "label_prompt_input": "[{user}]: ",
        "label_command_exit": "exit",
        "label_command_help": "help | /help",
        "label_command_settings": "/settings",
        "label_command_spam": "/spam",
        "label_command_desc_exit": "Disconnect and exit",
        "label_command_desc_help": "Show available commands",
        "label_command_desc_settings": "View current settings",
        "label_command_desc_spam": "Spam control (on/off/rate/add/remove/list/clear/status)",
        "label_auth_verifying": "[AUTH] Verifying via Mojang session server...",
        "label_pause_on_close": "Press Enter to close...",
        "label_not_connected_exit": "Could not connect to server. Program exited.",
        "label_invalid_packet": "Invalid packet length",
        "label_connection_closed": "Connection closed",
        "label_unknown": "unknown",
        "label_srv_resolved": "DNS SRV: {host} -> {target}",
        "label_spam_usage": "Usage: /spam <on|off|rate <n>|add <msg>|remove <i>|list|clear|status>",
    }
}

_current_lang = "zh"

def set_language(lang):
    global _current_lang
    if lang in _translations:
        _current_lang = lang

def t(key, **kwargs):
    strings = _translations.get(_current_lang, _translations["en"])
    text = strings.get(key, _translations["en"].get(key, key))
    if kwargs:
        return text.format(**kwargs)
    return text
