# Minecraft Bot Client (MBC) v2.1.0 - English

## Files
- `MinecraftBotClient-en` - English client, Run `chmod +x MinecraftBotClient-en` once, then `./MinecraftBotClient-en`
- `config.en.json` - Configuration file
- `README.en.md` - This readme
- `log/` - Log folder (created automatically when logging is enabled)

This is the macOS single-file client. No Python installation is required. If Gatekeeper blocks it, right-click and choose Open, or run `xattr -d com.apple.quarantine MinecraftBotClient-en` before launching.

## Configuration (config.en.json)
```json
{
  "version": "2.1.0",
  "username": "",
  "server_address": "localhost:25565",
  "minecraft_version": "1.8.9",
  "language": "en",
  "fast_start": false,
  "log_enabled": false,
  "spam_enabled": false,
  "spam_rate": 1.0,
  "spam_messages": ["Hello!", "Anyone there?", "GG"],
  "command_autocomplete": true,
  "auto_eat": true,
  "auto_eat_health_threshold": 10,
  "auto_walk": false,
  "auto_walk_waypoints": [],
  "stop_walk_on_damage": true,
  "proximity_alerts": true,
  "proximity_distance": 5.0,
  "human_actions": true,
  "human_action_interval_min": 2.0,
  "human_action_interval_max": 7.0
}
```
- `username`: Player name, leave empty for a random one
- `server_address`: Server address, SRV record domains supported (just use the domain, e.g. `mc.example.com`)
- `minecraft_version`: Server version, any version between 1.8 - 26.2 is supported
- `fast_start`: Skip version/announcement checks and reduce resource usage
- `command_autocomplete`: Toggle command autocomplete (grey preview when typing `.` or `/`)
- `auto_eat` / `auto_eat_health_threshold`: Auto-eat on damage toggle and health threshold
- `auto_walk` / `auto_walk_waypoints`: Random auto-walk and custom waypoints
- `stop_walk_on_damage`: Stop walking automatically on damage/death
- `proximity_alerts` / `proximity_distance`: Nearby player alerts and distance
- `human_actions`: Human-like head turning / arm swinging with random delays and trajectories
- `multi_bot_enabled` / `bot_count`: launch multiple bots at once (e.g. 20, 100) with random usernames
- `bot_name_prefix` / `bot_name_digits`: random username prefix and how many random digits it gets
- `bot_join_delay`: seconds between bot connections (keeps the join rate gentle)
- `bot_auth_enabled` / `bot_auth_mode`: auto-login switch and mode (`register`, `login` or `both`)
- `bot_auth_password`: password inserted into the auth commands
- `bot_auth_delay`: seconds to wait after joining before sending the auth command
- `bot_auth_register_command` / `bot_auth_login_command`: command templates, `{password}` is replaced with your password

## Commands
After joining a server, lines starting with `.` are MBC client commands (not sent to the server; legacy `//` still works):
- `.help` - Show MBC client commands and open the help website
- `.esc` - Leave the server without closing the client
- `.connect` - Connect / reconnect to the server
- `.exit` - Disconnect and close the client
- `.respawn` - Send a respawn packet after dying
- `.log on` / `.log off` - Toggle logging (one timestamped .log file per session in the log folder)
- `.spam on` / `.spam off` - Toggle auto-spam
- `.spam rate <n>` - Set spam rate (msg/s)
- `.spam add <msg>` / `.spam remove <i>` / `.spam list` / `.spam clear` / `.spam status`
- `.walk start` / `.walk stop` - Start/stop auto-walk
- `.walk add <x,y,z>` - Add a custom waypoint (relative coordinates, comma separated)
- `.walk list` / `.walk clear` - List/clear waypoints
- `.eat on` / `.eat off` - Toggle auto-eat on damage
- `.config <key> [val]` - View or modify any config key (ex: `.config fast_start true`)
- `/command` - Send a server command (e.g. `/list`, `/msg player text`)
- Plain text - Send as a chat message

## Vanilla-style Autocomplete
- Type `.` or `/` to see a grey inline preview of the command
- `Tab` accepts the preview; press Tab repeatedly to cycle suggestions
- `↑` / `↓` arrow keys or the mouse wheel cycle suggestions
- `Enter` sends, `Esc` clears the input, `↑` also browses command history

## Multi-bot mode
Set `multi_bot_enabled` to `true` and choose `bot_count`. Every bot connects with its own random username, and when `bot_auth_enabled` is on it automatically sends `/register` or `/login` with your `bot_auth_password` right after joining. The console then controls the whole group:
- `.status` - show how many bots are connected
- `.say <text>` - broadcast a chat message from every connected bot
- `.exit` - disconnect all bots and quit

## Notes
- This client runs in offline mode. Use it on servers with `online-mode=false`
- Version check URL: https://shit.pub/s/developer/minecraft/client/MinecraftBotClient-MBC/verify/txt.txt
- Announcement URL: https://shit.pub/s/developer/minecraft/client/MinecraftBotClient-MBC/announcement.txt
- Help website: https://shit.pub/s/developer/minecraft/client/MinecraftBotClient-MBC/MBC/
