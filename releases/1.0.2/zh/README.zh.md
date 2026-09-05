# Minecraft Bot Client (MBC) v1.0.2 - 中文版

## 文件说明
- `MinecraftBotClient-zh.exe` - 中文客户端，双击运行
- `config.zh.json` - 配置文件
- `README.zh.md` - 本说明文件
- `log/` - 日志文件夹（开启日志后自动创建）

## 配置文件 (config.zh.json)
```json
{
  "version": "1.0.2",
  "username": "",
  "server_address": "localhost:25565",
  "minecraft_version": "1.8.9",
  "language": "zh",
  "log_enabled": false,
  "spam_enabled": false,
  "spam_rate": 1.0,
  "spam_messages": ["Hello!", "Anyone there?", "GG"]
}
```
- `username`: 玩家名，留空自动随机生成
- `server_address`: 服务器地址，支持 SRV 域名（直接填域名即可，如 `mc.example.com`）
- `minecraft_version`: 服务器版本，支持 1.8 - 26.2 区间内任意版本
- `language`: 语言（zh/en）
- `log_enabled`: 是否默认开启日志（true/false）
- `spam_enabled`: 是否默认开启自动垃圾邮件（true/false）
- `spam_rate`: 每秒发送条数
- `spam_messages`: 垃圾消息模板列表

## 命令说明
进入服务器后：
- `//help` - 查看 MBC 客户端命令并打开帮助网站
- `//esc` - 离开服务器但不退出客户端
- `//connect` - 连接 / 重新连接服务器
- `//log true` - 开启日志（写入 log 文件夹，每次运行一个 .log 文件，含时间戳）
- `//log false` - 关闭日志
- `//spam on` - 开启自动垃圾邮件
- `//spam off` - 关闭自动垃圾邮件
- `//spam rate <每秒条数>` - 设置发送速率
- `//spam add <消息>` - 添加一条垃圾消息
- `//spam remove <索引>` - 按索引删除一条消息
- `//spam list` - 列出所有垃圾消息
- `//spam clear` - 清空垃圾消息
- `//spam status` - 查看垃圾邮件状态
- `//exit` - 断开并退出客户端
- `/命令` - 发送服务器命令（如 `/list`、`/msg 玩家 内容`）
- 普通文本 - 作为聊天消息发送

## 说明
- 本客户端为离线模式，请在 `online-mode=false`（破解/离线）服务器使用
- 帮助网站: https://shit.pub/s/developer/minecraft/client/MinecraftBotClient-MBC/MBC/
