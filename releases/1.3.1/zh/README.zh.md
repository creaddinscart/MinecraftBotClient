# Minecraft Bot Client (MBC) v1.3.1 - 中文版

## 文件说明
- `MinecraftBotClient-zh.exe` - 中文客户端，双击运行
- `config.zh.json` - 配置文件
- `README.zh.md` - 本说明文件
- `log/` - 日志文件夹（开启日志后自动创建）

## 配置文件 (config.zh.json)
```json
{
  "version": "1.3.1",
  "username": "",
  "server_address": "localhost:25565",
  "minecraft_version": "1.8.9",
  "language": "zh",
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
- `username`: 玩家名，留空自动随机生成
- `server_address`: 服务器地址，支持 SRV 域名（直接填域名即可，如 `mc.example.com`）
- `minecraft_version`: 服务器版本，支持 1.8 - 26.2 区间内任意版本
- `fast_start`: 快速启动，跳过版本查验与公告栏，降低资源占用
- `command_autocomplete`: 指令补全开关（输入 `.` 或 `/` 自动灰色预览）
- `auto_eat` / `auto_eat_health_threshold`: 受伤自动吃食物开关与血量阈值
- `auto_walk` / `auto_walk_waypoints`: 自动不规则走路与自定义路点
- `stop_walk_on_damage`: 受伤/死亡自动停止走路
- `proximity_alerts` / `proximity_distance`: 周围玩家靠近提示与距离
- `human_actions`: 模拟人类转头/出拳（随机延迟与轨迹，绕过常规反作弊）

## 指令说明
进入服务器后，`.` 开头为 MBC 客户端指令（不会发给服务器，旧版 `//` 仍兼容）：
- `.help` - 查看 MBC 客户端命令并打开帮助网站
- `.esc` - 离开服务器但不退出客户端
- `.connect` - 连接 / 重新连接服务器
- `.exit` - 断开并退出客户端
- `.respawn` - 死亡后发送重生包
- `.log on` / `.log off` - 开关日志（写入 log 文件夹，每次运行一个 .log 文件，含时间戳）
- `.spam on` / `.spam off` - 开关自动垃圾邮件
- `.spam rate <每秒条数>` - 设置发送速率
- `.spam add <消息>` / `.spam remove <索引>` / `.spam list` / `.spam clear` / `.spam status`
- `.walk start` / `.walk stop` - 开始/停止自动走路
- `.walk add <x,y,z>` - 添加自定义路点（相对坐标，逗号分隔）
- `.walk list` / `.walk clear` - 查看/清空路点
- `.eat on` / `.eat off` - 受伤自动吃食物开关
- `.config <key> [val]` - 查看/修改任意配置项（例：`.config fast_start true`）
- `/命令` - 发送服务器命令（如 `/list`、`/msg 玩家 内容`）
- 普通文本 - 作为聊天消息发送

## 指令补全（类原版）
- 输入 `.` 或 `/` 后自动以灰色文字预览指令
- `Tab` 补全预览内容，重复按 Tab 循环切换
- `↑` / `↓` 方向键或鼠标滚轮切换建议
- `Enter` 发送，`Esc` 清空当前输入，`↑` 还可回溯历史指令

## 说明
- 本客户端为离线模式，请在 `online-mode=false`（破解/离线）服务器使用
- 版本查验地址: https://shit.pub/s/developer/minecraft/client/MinecraftBotClient-MBC/verify/txt.txt
- 公告栏地址: https://shit.pub/s/developer/minecraft/client/MinecraftBotClient-MBC/announcement.txt
- 帮助网站: https://shit.pub/s/developer/minecraft/client/MinecraftBotClient-MBC/MBC/
