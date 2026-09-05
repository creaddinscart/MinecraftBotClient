# Minecraft Bot Client (MBC) v1.3.1 - English

## Files
- `MinecraftBotClient-en.exe` - English client, double-click to run
- `config.en.json` - Configuration file
- `README.en.md` - This readme
- `log/` - Log folder (created automatically when logging is enabled)

## Configuration (config.en.json)
```json
{
  "version": "1.3.1",
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

## Notes
- This client runs in offline mode. Use it on servers with `online-mode=false`
- Version check URL: https://shit.pub/s/developer/minecraft/client/MinecraftBotClient-MBC/verify/txt.txt
- Announcement URL: https://shit.pub/s/developer/minecraft/client/MinecraftBotClient-MBC/announcement.txt
- Help website: https://shit.pub/s/developer/minecraft/client/MinecraftBotClient-MBC/MBC/
