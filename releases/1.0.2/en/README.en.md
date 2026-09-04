# Minecraft Bot Client (MBC) v1.0.2 - English

## Files
- `MinecraftBotClient-en.exe` - English client, double-click to run
- `config.en.json` - Configuration file
- `README.en.md` - This readme
- `log/` - Log folder (created automatically when logging is enabled)

## Configuration (config.en.json)
```json
{
  "version": "1.0.2",
  "username": "",
  "server_address": "localhost:25565",
  "minecraft_version": "1.8.9",
  "language": "en",
  "log_enabled": false,
  "spam_enabled": false,
  "spam_rate": 1.0,
  "spam_messages": ["Hello!", "Anyone there?", "GG"]
}
```
- `username`: Player name, leave empty for a random one
- `server_address`: Server address, SRV record domains supported (just use the domain, e.g. `mc.example.com`)
- `minecraft_version`: Server version, any version between 1.8 - 26.2 is supported
- `language`: Language (zh/en)
- `log_enabled`: Enable logging by default (true/false)
- `spam_enabled`: Enable auto-spam by default (true/false)
- `spam_rate`: Spam messages per second
- `spam_messages`: List of spam message templates

## Commands
After joining a server:
- `//help` - Show MBC client commands and open the help website
- `//esc` - Leave the server without closing the client
- `//connect` - Connect / reconnect to the server
- `//log true` - Enable logging (written to the log folder, one .log file per session with timestamps)
- `//log false` - Disable logging
- `//spam on` - Enable auto-spam
- `//spam off` - Disable auto-spam
- `//spam rate <n>` - Set spam rate (msg/s)
- `//spam add <msg>` - Add a spam message
- `//spam remove <i>` - Remove a spam message by index
- `//spam list` - List all spam messages
- `//spam clear` - Clear all spam messages
- `//spam status` - Show spam status
- `//exit` - Disconnect and close the client
- `/command` - Send a server command (e.g. `/list`, `/msg player text`)
- Plain text - Send as a chat message

## Notes
- This client runs in offline mode. Use it on servers with `online-mode=false`
- Help website: https://shit.pub/s/developer/minecraft/client/MinecraftBotClient-MBC/MBC/
