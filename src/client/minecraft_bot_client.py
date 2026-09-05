import os
import random
import string
import threading
import time
import math
import webbrowser
from src import i18n
from src.logger import SessionLogger, strip_ansi
from src.network.version_checker import VersionChecker
from src.network.connection_manager import ConnectionManager, HumanActions
from src.settings.settings_manager import SettingsManager
from src.ui.console_ui import ConsoleUI
from src.features.spam import SpamManager


class MinecraftBotClient:
    CLIENT_COMMANDS = [
        ".help", ".esc", ".connect", ".exit",
        ".log on", ".log off",
        ".respawn",
        ".config fast_start true", ".config fast_start false",
        ".config log_enabled true", ".config log_enabled false",
        ".config auto_eat true", ".config auto_eat false",
        ".config auto_walk true", ".config auto_walk false",
        ".config stop_walk_on_damage true", ".config stop_walk_on_damage false",
        ".config proximity_alerts true", ".config proximity_alerts false",
        ".config human_actions true", ".config human_actions false",
        ".config command_autocomplete true", ".config command_autocomplete false",
        ".walk start", ".walk stop", ".walk clear", ".walk list", ".walk add 0,64,0",
        ".eat on", ".eat off",
        ".spam on", ".spam off", ".spam rate 1", ".spam add Hello!",
        ".spam list", ".spam clear", ".spam status",
    ]

    CLIENT_PREFIX = "."
    CLIENT_PREFIX_LEGACY = "//"

    SERVER_COMMANDS_HINTS = [
        "/help", "/list", "/msg", "/tell", "/say", "/me",
        "/login", "/register", "/tp", "/home", "/spawn",
        "/warp", "/tpa", "/tphere", "/gamemode", "/give",
        "/kill", "/nick", "/money", "/pay", "/rank",
    ]

    def __init__(self):
        self.settings = SettingsManager()
        i18n.set_language(self.settings.get_language())
        self.ui = ConsoleUI()
        self.version_checker = VersionChecker()
        self.connection_manager = ConnectionManager()
        self.logger = SessionLogger(self.settings.get_base_dir(), enabled=self.settings.get_log_enabled())
        self.spam = None
        self.human = None
        self.walk_thread = None
        self.walk_stop_event = threading.Event()
        self.username = None
        self.connected = False
        self.walk_waypoints = list(self.settings.get("auto_walk_waypoints", []) or [])
        self._proximity_alerted = set()
        self._last_health = 20.0
        self._ac_items = []

    def run(self):
        self.ui.clear_screen()
        fast = self.settings.get_fast_start()
        self.ui.show_loading(fast_start=fast)
        self.ui.print_banner()
        self.logger.log("START", f"MBC {self.settings.get_current_version()} launched, lang={self.settings.get_language()}, fast_start={fast}")

        if not fast:
            self.remote_check()
        self.apply_config()

        while True:
            if not self.connected:
                self.connect_to_server()
            if self.connected:
                action = self.chat_loop()
                if action == 'exit': break
                self.connected = False
            action = self.idle_loop()
            if action == 'exit': break

        self.logger.log("STOP", "MBC exited")
        self.logger.close()
        self.ui.print_success(i18n.t('label_goodbye'))

    def remote_check(self):
        self.ui.print_section(i18n.t('section_verify'))
        raw_ver = ""
        try:
            _, raw_ver = self.version_checker.fetch_version_info()
        except Exception as e:
            self.logger.log("VERSION", f"Version check failed: {e}")
        self._print_remote_text(raw_ver, "VERSION", 'label_verify_none')

        self.ui.print_section(i18n.t('section_announcement'))
        raw_ann = ""
        try:
            self.version_checker.fetch_announcement()
            raw_ann = self.version_checker.raw_announcement_response or ""
        except Exception as e:
            raw_ann = getattr(self.version_checker, 'raw_announcement_response', '') or ""
            self.logger.log("ANNOUNCE", f"Announcement fetch failed: {e}")
        self._print_remote_text(raw_ann, "ANNOUNCE", 'label_announcement_none')

    def _print_remote_text(self, raw, tag, empty_key):
        if raw and raw.strip():
            for line in raw.rstrip().splitlines():
                self.ui.print_raw(line)
                self.logger.log(tag, strip_ansi(line))
        else:
            self.ui.print_info(i18n.t(empty_key))

    def apply_config(self):
        self.username = self.settings.get_username().strip() or self.generate_random_username()
        self.ui.print_section(i18n.t('section_player_info'))
        self._ui_event('print_info', 'CONFIG', i18n.t('label_config_path', path=self.settings.get_config_path()))
        if self.settings.load_error:
            backup = self.settings.corrupt_backup or ""
            self._ui_event('print_error', 'CONFIG', i18n.t('label_config_corrupt', err=self.settings.load_error, backup=backup))
        self._ui_event('print_info', 'CONFIG', f"{i18n.t('label_server')}: {self.settings.get_server_address()}")
        self._ui_event('print_info', 'CONFIG', f"{i18n.t('label_version')}: {self.settings.get_minecraft_version()}")
        self._ui_event('print_info', 'CONFIG', f"{i18n.t('label_username')}: {self.username}")
        self._ui_event('print_info', 'CONFIG', f"{i18n.t('label_fast_start')}: {'ON' if self.settings.get_fast_start() else 'OFF'}")
        log_state = i18n.t('label_log_state_on') if self.logger.enabled else i18n.t('label_log_state_off')
        self._ui_event('print_info', 'CONFIG', log_state)
        self._refresh_autocomplete()

    def _refresh_autocomplete(self):
        if not self.settings.get("command_autocomplete", True):
            self.ui.set_autocomplete_items([])
            return
        pool = list(self.CLIENT_COMMANDS) + list(self.SERVER_COMMANDS_HINTS)
        self.ui.set_autocomplete_items(pool)

    def generate_random_username(self):
        prefixes = ["Bot", "Player", "Client", "Agent", "Miner", "Digger"]
        prefix = random.choice(prefixes)
        suffix = ''.join(random.choices(string.digits, k=4))
        return f"{prefix}{suffix}"

    def connect_to_server(self):
        self.ui.print_section(i18n.t('section_connecting'))
        server_address = self.settings.get_server_address()
        version = self.settings.get_minecraft_version()
        self._ui_event('print_info', 'CONNECT', i18n.t('label_connecting_to', addr=server_address))

        try:
            self.connection_manager.connect(
                server_address=server_address,
                username=self.username,
                protocol_version=version,
                on_chat=self.on_chat_received,
                on_disconnect=self.on_disconnected,
                log_func=self._net_log,
                on_health=self.on_health_changed,
                on_death=self.on_died,
                on_damage=self.on_damage_taken,
                on_player_spawn=self.on_player_spawned,
                on_position=self.on_position_received,
            )
            self.connected = True
            self._ui_event('print_success', 'CONNECT', i18n.t('label_connected'))
            self._ui_event('print_info', 'CONNECT', i18n.t('label_prompt_exit'))

            self.spam = SpamManager(
                self.connection_manager,
                log_func=lambda m: self._ui_event('print_info', 'SPAM', m),
                sent_func=lambda m: self._ui_event('print_sent', 'SPAM', m)
            )
            self.spam.rate = self.settings.get_spam_rate()
            self.spam.messages = self.settings.get_spam_messages()
            if self.settings.get_spam_enabled() and self.spam.messages:
                self.spam.start()

            if self.settings.get("human_actions", True):
                hmin = float(self.settings.get("human_action_interval_min", 2.0))
                hmax = float(self.settings.get("human_action_interval_max", 7.0))
                self.human = HumanActions(self.connection_manager, interval_min=hmin, interval_max=hmax)
                self.connection_manager.human = self.human
                self.human.start()

            if self.settings.get("auto_walk", False):
                self.start_walk()

        except Exception as e:
            self._ui_event('print_error', 'CONNECT', i18n.t('label_connection_failed', err=str(e)))
            self.connected = False

    def _net_log(self, message):
        self.ui.print_info(message)
        self.logger.log("NET", message)

    def _ui_event(self, method, category, message):
        getattr(self.ui, method)(message)
        self.logger.log(category, message)

    def _alert(self, message):
        if not self.settings.get("proximity_alerts", True):
            self.logger.log("ALERT", message)
            return
        self.ui.print_alert(message)
        self.logger.log("ALERT", message)

    def on_chat_received(self, text):
        self.ui.print_chat(i18n.t('label_chat', text=text))
        self.logger.log("CHAT", strip_ansi(text))

    def on_disconnected(self):
        if self.spam and self.spam.enabled: self.spam.stop()
        if self.human: self.human.stop()
        self.stop_walk()
        if self.connected:
            self._ui_event('print_warning', 'DISCONNECT', i18n.t('label_disconnected_by_server'))

    def on_health_changed(self, health, food_val):
        old = self._last_health
        self._last_health = health
        if old > health and self.settings.get("auto_eat", True):
            threshold = float(self.settings.get("auto_eat_health_threshold", 10))
            if 0 < health <= threshold:
                self.logger.log("EAT", f"Low health {health}, triggering eat attempt")
                try:
                    self.connection_manager.send_eat_food()
                except Exception:
                    pass

    def on_died(self):
        self.stop_walk()
        self._alert(i18n.t('label_damage_stopped_walk'))

    def on_damage_taken(self):
        if self.settings.get("stop_walk_on_damage", True):
            self.stop_walk()

    def on_player_spawned(self, puuid, x, y, z):
        if not self.settings.get("proximity_alerts", True):
            return
        key = puuid
        if time.time() - self.connection_manager.players.get(key, (0,0,0,0,0))[4] < 2:
            return
        if key in self._proximity_alerted and (time.time() - self._proximity_alerted.get(key, 0)) < 15:
            return
        self._proximity_alerted.add(key)
        self._proximity_alerted = {k: t for k, t in self._proximity_alerted.items() if time.time() - t < 300}
        self.connection_manager.players[key] = (x, y, z, self.connection_manager.players.get(key, (0,0,0,0,0))[3], time.time())
        px, py, pz = self.connection_manager.last_pos
        dist = math.sqrt((px - x)**2 + (py - y)**2 + (pz - z)**2)
        threshold = float(self.settings.get("proximity_distance", 5.0))
        if dist <= threshold:
            self._alert(i18n.t('label_alert_player_near', name="player_"+key[-6:], dist=dist))

    def on_position_received(self, x, y, z):
        if not self.settings.get("proximity_alerts", True):
            return
        yaw_rad = math.radians(getattr(self.connection_manager, 'human', None).yaw if (getattr(self.connection_manager, 'human', None)) else 0.0)
        dx = math.sin(yaw_rad) * 1.2
        dz = -math.cos(yaw_rad) * 1.2
        ahead = (x + dx, y - 0.5, z + dz)
        px, py, pz = self.connection_manager.last_pos
        if self.human:
            self.human.yaw = (self.human.yaw or 0)
            self.human.pitch = (self.human.pitch or 0)
        if (ahead[1] < y - 1.2):
            state_key = f"void_{int(time.time()//15)}"
            if not hasattr(self, '_void_cache'):
                self._void_cache = set()
            if state_key not in self._void_cache:
                self._void_cache.add(state_key)
                self._alert(i18n.t('label_alert_no_ground'))

    def start_walk(self):
        if self.walk_thread and self.walk_thread.is_alive():
            return
        self.walk_stop_event.clear()
        self.walk_thread = threading.Thread(target=self._walk_loop, daemon=True)
        self.walk_thread.start()
        self.ui.print_info(i18n.t('label_walk_started'))

    def stop_walk(self):
        was_running = bool(self.walk_thread and self.walk_thread.is_alive())
        self.walk_stop_event.set()
        if self.walk_thread:
            self.walk_thread.join(timeout=1)
            self.walk_thread = None
        if was_running:
            self.ui.print_info(i18n.t('label_walk_stopped'))
            self.logger.log("WALK", "Auto-walk stopped")

    def _walk_loop(self):
        waypoints = list(self.walk_waypoints)
        base_pos = self.connection_manager.last_pos or (0, 64, 0)
        if not waypoints:
            self._random_walk()
            return
        wp_idx = 0
        while not self.walk_stop_event.is_set() and self.connected:
            tx, ty, tz = waypoints[wp_idx % len(waypoints)]
            try:
                self._walk_toward(base_pos[0] + float(tx), base_pos[1] + float(ty), base_pos[2] + float(tz))
                wp_idx += 1
            except Exception:
                break
        self.settings.save_spam_config(self.settings.get_spam_enabled(), self.settings.get_spam_rate(), self.settings.get_spam_messages())

    def _random_walk(self):
        bx, by, bz = self.connection_manager.last_pos or (0, 64, 0)
        while not self.walk_stop_event.is_set() and self.connected:
            try:
                angle = random.uniform(0, math.tau)
                dist = random.uniform(1.5, 4.5)
                tx = bx + math.cos(angle) * dist
                tz = bz + math.sin(angle) * dist
                self._walk_toward(tx, by, tz, base_steps_max=22)
                wait = random.uniform(0.5, 2.0)
                if self.walk_stop_event.wait(wait): break
                bx, by, bz = self.connection_manager.last_pos
            except Exception:
                break

    def _walk_toward(self, tx, ty, tz, base_steps_max=36):
        sx, sy, sz = self.connection_manager.last_pos or (0, 64, 0)
        steps = min(base_steps_max, max(6, int(math.hypot(tx - sx, tz - sz) / 0.45)))
        for i in range(steps + 1):
            if self.walk_stop_event.is_set() or not self.connected:
                return
            t = i / steps
            ease = t * t * (3 - 2 * t)
            jx = math.sin(i * 0.6) * random.uniform(-0.03, 0.03)
            jz = math.cos(i * 0.7) * random.uniform(-0.03, 0.03)
            x = sx + (tx - sx) * ease + jx
            z = sz + (tz - sz) * ease + jz
            y = sy + (ty - sy) * ease
            try:
                self.connection_manager.send_position(x, y, z, on_ground=True)
            except Exception:
                return
            delay = random.uniform(0.045, 0.075)
            if self.walk_stop_event.wait(delay): return

    def chat_loop(self):
        while self.connected:
            try:
                message = self.ui.get_input(i18n.t('label_prompt_input', user=self.username)).strip()
                if not message: continue

                if message.startswith("//"):
                    action = self.handle_client_command(message, allow_connect=False)
                    if action == 'exit': return 'exit'
                    if action == 'esc': return 'esc'
                    continue

                if message.startswith("/"):
                    self.connection_manager.send_chat(message)
                    self._ui_event('print_sent', 'SERVERCMD', i18n.t('label_sent', text=message))
                else:
                    self.connection_manager.send_chat(message)
                    self._ui_event('print_sent', 'SEND', i18n.t('label_sent', text=message))

            except EOFError:
                self.disconnect()
                return 'exit'
            except KeyboardInterrupt:
                self.disconnect()
                return 'exit'
            except Exception as e:
                self._ui_event('print_error', 'ERROR', i18n.t('label_error', err=str(e)))
                if not self.connection_manager.is_alive():
                    self.connected = False
        return 'esc'

    def idle_loop(self):
        self.ui.print_info(i18n.t('label_not_connected_hint'))
        self.logger.log("IDLE", "Entered idle state")
        while True:
            try:
                message = self.ui.get_input(i18n.t('label_idle_prompt')).strip()
            except (EOFError, KeyboardInterrupt):
                return 'exit'
            if not message: continue
            if message.startswith("//"):
                action = self.handle_client_command(message, allow_connect=True)
                if action == 'exit': return 'exit'
                if action == 'reconnect': return 'reconnect'
            else:
                self.ui.print_info(i18n.t('label_not_connected_hint'))

    def handle_client_command(self, message, allow_connect):
        if message.startswith("//"):
            body = message[2:]
        else:
            body = message[1:]
        parts = body.strip().split()
        cmd = parts[0].lower() if parts else "help"
        args = parts[1:]
        self.logger.log("MBC", f"Client command: {message}")

        if cmd == "help":
            self.show_help()
            return None

        if cmd == "esc":
            if self.connected: self.disconnect()
            self._ui_event('print_warning', 'MBC', i18n.t('label_esc_done'))
            return 'esc'

        if cmd == "exit":
            if self.connected: self.disconnect()
            return 'exit'

        if cmd == "respawn":
            if self.connected:
                self.connection_manager.send_respawn()
            else:
                self.ui.print_info(i18n.t('label_not_connected'))
            return None

        if cmd == "eat":
            return self.handle_eat_command(args)

        if cmd == "walk":
            return self.handle_walk_command(args)

        if cmd == "config":
            return self.handle_config_command(args)

        if cmd == "connect":
            if self.connected:
                self.ui.print_info(i18n.t('label_already_connected'))
                return None
            if allow_connect:
                self.ui.print_info(i18n.t('label_reconnecting'))
                return 'reconnect'
            return None

        if cmd == "log":
            return self.handle_log_command(args)

        if cmd == "spam":
            return self.handle_spam_command(args)

        self._ui_event('print_warning', 'MBC', i18n.t('label_unknown_command'))
        return None

    def handle_log_command(self, args):
        if not args:
            self.ui.print_info(i18n.t('label_log_usage'))
            state = i18n.t('label_log_state_on') if self.logger.enabled else i18n.t('label_log_state_off')
            self.ui.print_info(state)
            return None
        value = args[0].lower()
        if value in ("true", "on", "1", "enable", "enabled"):
            path = self.logger.enable()
            self.settings.set_log_enabled(True)
            if path:
                self._ui_event('print_success', 'LOG', i18n.t('label_log_on', path=path))
            else:
                self.ui.print_error(i18n.t('label_log_usage'))
        elif value in ("false", "off", "0", "disable", "disabled"):
            self.logger.disable()
            self.settings.set_log_enabled(False)
            self._ui_event('print_info', 'LOG', i18n.t('label_log_off'))
        else:
            self.ui.print_info(i18n.t('label_log_usage'))
        return None

    def handle_eat_command(self, args):
        if not args:
            state = self.settings.get("auto_eat", True)
            self.ui.print_info(i18n.t('label_eat_on') if state else i18n.t('label_eat_off'))
            return None
        v = args[0].lower()
        if v in ("on", "true", "1", "enable"):
            self.settings.set("auto_eat", True)
            self.ui.print_info(i18n.t('label_eat_on'))
        elif v in ("off", "false", "0", "disable"):
            self.settings.set("auto_eat", False)
            self.ui.print_info(i18n.t('label_eat_off'))
        else:
            self.ui.print_info(".eat <on|off>")
        return None

    def handle_walk_command(self, args):
        if not args:
            self.ui.print_info(i18n.t('label_walk_usage'))
            return None
        sub = args[0].lower()
        rest = args[1:]
        if sub in ("start", "on"):
            self.settings.set("auto_walk", True)
            if self.connected:
                self.start_walk()
            else:
                self.ui.print_info(i18n.t('label_walk_started'))
        elif sub in ("stop", "off"):
            self.settings.set("auto_walk", False)
            self.stop_walk()
        elif sub == "add":
            if not rest:
                self.ui.print_info(i18n.t('label_walk_add_usage'))
                return None
            coords = " ".join(rest).split(",")
            if len(coords) != 3:
                self.ui.print_info(i18n.t('label_walk_add_usage'))
                return None
            try:
                point = tuple(float(c.strip()) for c in coords)
            except ValueError:
                self.ui.print_info(i18n.t('label_walk_coords_error'))
                return None
            self.walk_waypoints.append(point)
            self.settings.set("auto_walk_waypoints", [list(p) for p in self.walk_waypoints])
            self._ui_event('print_success', 'WALK', i18n.t('label_walk_added', point=str(point)))
        elif sub == "clear":
            self.walk_waypoints.clear()
            self.settings.set("auto_walk_waypoints", [])
            self.ui.print_info(i18n.t('label_walk_cleared'))
        elif sub == "list":
            if not self.walk_waypoints:
                self.ui.print_info(i18n.t('label_walk_empty'))
            else:
                self.ui.print_info(i18n.t('label_walk_list'))
                for i, p in enumerate(self.walk_waypoints):
                    self.ui.print_info(f"  [{i}] {p}")
        else:
            self.ui.print_info(i18n.t('label_walk_usage'))
        return None

    def handle_config_command(self, args):
        if not args:
            for k in sorted(self.settings.config.keys()):
                self.ui.print_info(i18n.t('label_config_show', key=k, val=self.settings.config[k]))
            return None
        key = args[0]
        if len(args) == 1:
            if key in self.settings.config:
                self.ui.print_info(i18n.t('label_config_show', key=key, val=self.settings.config[key]))
            else:
                self.ui.print_info(f"Unknown config key: {key}")
            return None
        raw = " ".join(args[1:])
        if raw.lower() in ("true", "on", "yes"):
            val = True
        elif raw.lower() in ("false", "off", "no"):
            val = False
        else:
            try:
                if ',' in raw:
                    val = [float(x.strip()) for x in raw.split(',')]
                elif '.' in raw:
                    val = float(raw)
                else:
                    val = int(raw)
            except Exception:
                val = raw
        self.settings.set(key, val)
        if key == "command_autocomplete":
            self._refresh_autocomplete()
        self._ui_event('print_success', 'CONFIG', i18n.t('label_config_set', key=key, val=val))
        return None

    def handle_spam_command(self, args):
        if not self.spam:
            self.ui.print_info(i18n.t('label_spam_not_ready'))
            return None
        if not args:
            self.spam.show_status()
            self.settings.save_spam_config(self.spam.enabled, self.spam.rate, self.spam.messages)
            return None
        sub = args[0].lower()
        remaining = args[1:]
        if sub in ("on", "start"): self.spam.start()
        elif sub in ("off", "stop"): self.spam.stop()
        elif sub == "rate":
            if not remaining: self.ui.print_info(f"Rate: {self.spam.rate} msg/s")
            else: self.spam.set_rate(remaining[0])
        elif sub == "add":
            if not remaining: self.ui.print_info(i18n.t('label_spam_usage'))
            else: self.spam.add_message(" ".join(remaining))
        elif sub == "remove":
            if not remaining: self.ui.print_info(i18n.t('label_spam_usage'))
            else: self.spam.remove_message(remaining[0])
        elif sub == "list": self.spam.list_messages()
        elif sub == "clear": self.spam.clear_messages()
        elif sub == "status": self.spam.show_status()
        else: self.ui.print_info(i18n.t('label_spam_usage'))
        self.settings.save_spam_config(self.spam.enabled, self.spam.rate, self.spam.messages)
        return None

    def show_help(self):
        self.ui.print_section(i18n.t('section_help'))
        commands = [
            (i18n.t('label_command_help'), i18n.t('label_command_desc_help')),
            (i18n.t('label_command_esc'), i18n.t('label_command_desc_esc')),
            (i18n.t('label_command_connect'), i18n.t('label_command_desc_connect')),
            (i18n.t('label_command_log'), i18n.t('label_command_desc_log')),
            (i18n.t('label_command_spam'), i18n.t('label_command_desc_spam')),
            (i18n.t('label_command_respawn'), i18n.t('label_command_desc_respawn')),
            (i18n.t('label_command_config'), i18n.t('label_command_desc_config')),
            (i18n.t('label_command_walk'), i18n.t('label_command_desc_walk')),
            (i18n.t('label_command_eat'), i18n.t('label_command_desc_eat')),
            (i18n.t('label_command_exit'), i18n.t('label_command_desc_exit')),
            (i18n.t('label_command_server'), i18n.t('label_command_desc_server')),
            (i18n.t('label_command_chat'), i18n.t('label_command_desc_chat')),
        ]
        for cmd, desc in commands:
            self.ui.print_info(f"{cmd:<28} - {desc}")
        self.ui.print_info("")
        self.ui.print_info(i18n.t('label_website', url=i18n.WEBSITE_URL))
        self.ui.print_info(i18n.t('label_autocomplete_hint'))
        try:
            webbrowser.open(i18n.WEBSITE_URL)
            self.ui.print_info(i18n.t('label_website_opening'))
        except Exception:
            pass

    def disconnect(self):
        if self.spam and self.spam.enabled:
            self.spam.stop()
            self.settings.save_spam_config(self.spam.enabled, self.spam.rate, self.spam.messages)
        if self.human:
            self.human.stop()
            self.human = None
        self.stop_walk()
        try:
            self.connection_manager.disconnect()
        except Exception:
            pass
        self.connected = False
        self.logger.log("DISCONNECT", "Disconnected from server")
        self.ui.print_success(i18n.t('label_disconnected'))
