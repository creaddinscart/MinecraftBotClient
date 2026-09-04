import os
import json
import uuid
import zlib
import hashlib
import socket
import struct
import threading
import time
from src import i18n

try:
    import dns.resolver
    import dns.name
    _DNS_AVAILABLE = True
except ImportError:
    _DNS_AVAILABLE = False

MC_COLOR_TO_ANSI = {
    'black': '\033[30m', 'dark_blue': '\033[34m', 'dark_green': '\033[32m',
    'dark_aqua': '\033[36m', 'dark_red': '\033[31m', 'dark_purple': '\033[35m',
    'gold': '\033[33m', 'gray': '\033[37m', 'dark_gray': '\033[90m',
    'blue': '\033[94m', 'green': '\033[92m', 'aqua': '\033[96m',
    'red': '\033[91m', 'light_purple': '\033[95m', 'yellow': '\033[93m',
    'white': '\033[97m',
}

SECTION_CODE_TO_ANSI = {
    '0': '\033[30m', '1': '\033[34m', '2': '\033[32m', '3': '\033[36m',
    '4': '\033[31m', '5': '\033[35m', '6': '\033[33m', '7': '\033[37m',
    '8': '\033[90m', '9': '\033[94m', 'a': '\033[92m', 'b': '\033[96m',
    'c': '\033[91m', 'd': '\033[95m', 'e': '\033[93m', 'f': '\033[97m',
    'l': '\033[1m', 'm': '\033[9m', 'n': '\033[4m', 'o': '\033[3m',
    'k': '', 'r': '\033[0m',
}

ANSI_RESET = '\033[0m'


def hex_to_ansi(hex_color):
    try:
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        if r == g == b:
            if r < 48:
                return '\033[30m'
            elif r < 115:
                return '\033[90m'
            elif r < 180:
                return '\033[37m'
            else:
                return '\033[97m'
        if r > 127 and g > 127 and b > 127:
            return '\033[97m'
        if r > g and r > b:
            if r > 180:
                return '\033[91m'
            return '\033[31m'
        if g > r and g > b:
            if g > 180:
                return '\033[92m'
            return '\033[32m'
        if b > r and b > g:
            if b > 180:
                return '\033[94m'
            return '\033[34m'
        if r > 127 and g > 127:
            return '\033[93m'
        if r > 127 and b > 127:
            return '\033[95m'
        if g > 127 and b > 127:
            return '\033[96m'
        return '\033[97m'
    except Exception:
        return ''


def apply_section_codes(text, base_color=None):
    result = ''
    i = 0
    current_ansi = ''
    if base_color:
        if base_color.startswith('#'):
            current_ansi = hex_to_ansi(base_color)
        else:
            current_ansi = MC_COLOR_TO_ANSI.get(base_color, '')
        result += current_ansi
    while i < len(text):
        if text[i] == '\u00a7' and i + 1 < len(text):
            code = text[i + 1].lower()
            if code in SECTION_CODE_TO_ANSI:
                ansi = SECTION_CODE_TO_ANSI[code]
                if code == 'r':
                    result += ANSI_RESET
                    current_ansi = ''
                else:
                    if code in ('l', 'm', 'n', 'o'):
                        result += ansi
                    else:
                        current_ansi = ansi
                        result += ANSI_RESET + ansi
                i += 2
                continue
        result += text[i]
        i += 1
    if current_ansi:
        result += ANSI_RESET
    return result


def flatten_chat_colored(obj, color=None, fmt=None):
    if fmt is None:
        fmt = {}
    if isinstance(obj, str):
        return apply_section_codes(obj, color)
    if isinstance(obj, dict):
        text = obj.get('text', '')
        new_color = obj.get('color', color)
        new_fmt = dict(fmt)
        for key in ('bold', 'italic', 'underline', 'strikethrough', 'obfuscated'):
            if key in obj:
                new_fmt[key] = obj[key]
        prefix = ''
        if new_color:
            if new_color.startswith('#'):
                prefix += hex_to_ansi(new_color)
            else:
                prefix += MC_COLOR_TO_ANSI.get(new_color, '')
        if new_fmt.get('bold'):
            prefix += '\033[1m'
        if new_fmt.get('italic'):
            prefix += '\033[3m'
        if new_fmt.get('underline'):
            prefix += '\033[4m'
        if new_fmt.get('strikethrough'):
            prefix += '\033[9m'
        result = prefix + apply_section_codes(text, new_color)
        for extra in obj.get('extra', []):
            result += flatten_chat_colored(extra, new_color, new_fmt)
            result += ANSI_RESET + prefix
        if 'translate' in obj and not obj.get('extra'):
            parts = [flatten_chat_colored(a, new_color, new_fmt) for a in obj.get('with', [])]
            translated = ''.join(parts)
            if text:
                return result
            return prefix + translated + (ANSI_RESET if prefix else '')
        if 'score' in obj:
            score = obj['score']
            result = prefix + score.get('value', score.get('name', '')) + (ANSI_RESET if prefix else '')
        if prefix:
            result += ANSI_RESET
        return result
    if isinstance(obj, list):
        return ''.join(flatten_chat_colored(i, color, fmt) for i in obj)
    return str(obj)


class ConnectionManager:
    PACKET_IDS = {
        47:  {"sb_chat": 0x01, "sb_keepalive": 0x00, "cb_chat": [0x02],     "cb_keepalive": 0x00, "cb_disconnect": 0x40, "login_uuid": False, "chat_modern": False, "has_config": False},
        340: {"sb_chat": 0x02, "sb_keepalive": 0x0B, "cb_chat": [0x0F],     "cb_keepalive": 0x1F, "cb_disconnect": 0x40, "login_uuid": False, "chat_modern": False, "has_config": False},
        735: {"sb_chat": 0x03, "sb_keepalive": 0x0F, "cb_chat": [0x0E],     "cb_keepalive": 0x1F, "cb_disconnect": 0x1B, "login_uuid": False, "chat_modern": False, "has_config": False},
        754: {"sb_chat": 0x03, "sb_keepalive": 0x0F, "cb_chat": [0x0E],     "cb_keepalive": 0x1F, "cb_disconnect": 0x1B, "login_uuid": False, "chat_modern": False, "has_config": False},
        755: {"sb_chat": 0x03, "sb_keepalive": 0x0F, "cb_chat": [0x0F],     "cb_keepalive": 0x1E, "cb_disconnect": 0x19, "login_uuid": False, "chat_modern": False, "has_config": False},
        757: {"sb_chat": 0x03, "sb_keepalive": 0x0F, "cb_chat": [0x0F],     "cb_keepalive": 0x1E, "cb_disconnect": 0x19, "login_uuid": False, "chat_modern": False, "has_config": False},
        758: {"sb_chat": 0x03, "sb_keepalive": 0x10, "cb_chat": [0x0F],     "cb_keepalive": 0x1E, "cb_disconnect": 0x19, "login_uuid": False, "chat_modern": False, "has_config": False},
        759: {"sb_chat": 0x04, "sb_keepalive": 0x11, "cb_chat": [0x30, 0x5F], "cb_keepalive": 0x1E, "cb_disconnect": 0x17, "login_uuid": False, "chat_modern": True,  "has_config": False},
        760: {"sb_chat": 0x04, "sb_keepalive": 0x11, "cb_chat": [0x30, 0x5F], "cb_keepalive": 0x1E, "cb_disconnect": 0x17, "login_uuid": True,  "chat_modern": True,  "has_config": False},
        763: {"sb_chat": 0x04, "sb_keepalive": 0x12, "cb_chat": [0x32, 0x64], "cb_keepalive": 0x22, "cb_disconnect": 0x19, "login_uuid": True,  "chat_modern": True,  "has_config": False},
        764: {"sb_chat": 0x01, "sb_keepalive": 0x12, "cb_chat": [0x30, 0x69], "cb_keepalive": 0x24, "cb_disconnect": 0x1D, "login_uuid": True,  "chat_modern": True,  "has_config": True,
              "cfg_cb_disconnect": 0x02, "cfg_cb_keepalive": 0x06, "cfg_cb_ping": 0x04, "cfg_cb_registry": 0x07, "cfg_cb_finish": 0x0B, "cfg_cb_known_packs": 0x0E,
              "cfg_sb_client_info": 0x00, "cfg_sb_plugin_msg": 0x01, "cfg_sb_keepalive": 0x04, "cfg_sb_ping": 0x05, "cfg_sb_ack": 0x0C},
        765: {"sb_chat": 0x01, "sb_keepalive": 0x12, "cb_chat": [0x31, 0x6A], "cb_keepalive": 0x25, "cb_disconnect": 0x1D, "login_uuid": True,  "chat_modern": True,  "has_config": True,
              "cfg_cb_disconnect": 0x02, "cfg_cb_keepalive": 0x06, "cfg_cb_ping": 0x04, "cfg_cb_registry": 0x07, "cfg_cb_finish": 0x0B, "cfg_cb_known_packs": 0x0E,
              "cfg_sb_client_info": 0x00, "cfg_sb_plugin_msg": 0x01, "cfg_sb_keepalive": 0x04, "cfg_sb_ping": 0x05, "cfg_sb_ack": 0x0C},
        766: {"sb_chat": 0x01, "sb_keepalive": 0x18, "cb_chat": [0x33, 0x6C], "cb_keepalive": 0x27, "cb_disconnect": 0x1E, "login_uuid": True,  "chat_modern": True,  "has_config": True,
              "cfg_cb_disconnect": 0x02, "cfg_cb_keepalive": 0x06, "cfg_cb_ping": 0x04, "cfg_cb_registry": 0x07, "cfg_cb_finish": 0x0B, "cfg_cb_known_packs": 0x0E,
              "cfg_sb_client_info": 0x00, "cfg_sb_plugin_msg": 0x01, "cfg_sb_keepalive": 0x04, "cfg_sb_ping": 0x05, "cfg_sb_ack": 0x0C},
        767: {"sb_chat": 0x01, "sb_keepalive": 0x1A, "cb_chat": [0x34, 0x6E], "cb_keepalive": 0x28, "cb_disconnect": 0x1E, "login_uuid": True,  "chat_modern": True,  "has_config": True,
              "cfg_cb_disconnect": 0x02, "cfg_cb_keepalive": 0x06, "cfg_cb_ping": 0x04, "cfg_cb_registry": 0x07, "cfg_cb_finish": 0x0B, "cfg_cb_known_packs": 0x0E,
              "cfg_sb_client_info": 0x00, "cfg_sb_plugin_msg": 0x01, "cfg_sb_keepalive": 0x04, "cfg_sb_ping": 0x05, "cfg_sb_ack": 0x0C},
        768: {"sb_chat": 0x01, "sb_keepalive": 0x1B, "cb_chat": [0x6F],      "cb_keepalive": 0x29, "cb_disconnect": 0x1E, "login_uuid": True,  "chat_modern": True,  "has_config": True,
              "cfg_cb_disconnect": 0x02, "cfg_cb_keepalive": 0x06, "cfg_cb_ping": 0x04, "cfg_cb_registry": 0x07, "cfg_cb_finish": 0x0B, "cfg_cb_known_packs": 0x0E,
              "cfg_sb_client_info": 0x00, "cfg_sb_plugin_msg": 0x01, "cfg_sb_keepalive": 0x04, "cfg_sb_ping": 0x05, "cfg_sb_ack": 0x0C},
        769: {"sb_chat": 0x01, "sb_keepalive": 0x1C, "cb_chat": [0x70],      "cb_keepalive": 0x2A, "cb_disconnect": 0x1F, "login_uuid": True,  "chat_modern": True,  "has_config": True,
              "cfg_cb_disconnect": 0x02, "cfg_cb_keepalive": 0x06, "cfg_cb_ping": 0x04, "cfg_cb_registry": 0x07, "cfg_cb_finish": 0x0B, "cfg_cb_known_packs": 0x0E,
              "cfg_sb_client_info": 0x00, "cfg_sb_plugin_msg": 0x01, "cfg_sb_keepalive": 0x04, "cfg_sb_ping": 0x05, "cfg_sb_ack": 0x0C},
        770: {"sb_chat": 0x01, "sb_keepalive": 0x1C, "cb_chat": [0x70],      "cb_keepalive": 0x2A, "cb_disconnect": 0x1F, "login_uuid": True,  "chat_modern": True,  "has_config": True,
              "cfg_cb_disconnect": 0x02, "cfg_cb_keepalive": 0x06, "cfg_cb_ping": 0x04, "cfg_cb_registry": 0x07, "cfg_cb_finish": 0x0B, "cfg_cb_known_packs": 0x0E,
              "cfg_sb_client_info": 0x00, "cfg_sb_plugin_msg": 0x01, "cfg_sb_keepalive": 0x04, "cfg_sb_ping": 0x05, "cfg_sb_ack": 0x0C},
        771: {"sb_chat": 0x02, "sb_keepalive": 0x1D, "cb_chat": [0x71],      "cb_keepalive": 0x2B, "cb_disconnect": 0x1F, "login_uuid": True,  "chat_modern": True,  "has_config": True,
              "cfg_cb_disconnect": 0x02, "cfg_cb_keepalive": 0x06, "cfg_cb_ping": 0x04, "cfg_cb_registry": 0x07, "cfg_cb_finish": 0x0B, "cfg_cb_known_packs": 0x0E,
              "cfg_sb_client_info": 0x00, "cfg_sb_plugin_msg": 0x01, "cfg_sb_keepalive": 0x04, "cfg_sb_ping": 0x05, "cfg_sb_ack": 0x0C},
        772: {"sb_chat": 0x02, "sb_keepalive": 0x1D, "cb_chat": [0x71],      "cb_keepalive": 0x2B, "cb_disconnect": 0x1F, "login_uuid": True,  "chat_modern": True,  "has_config": True,
              "cfg_cb_disconnect": 0x02, "cfg_cb_keepalive": 0x06, "cfg_cb_ping": 0x04, "cfg_cb_registry": 0x07, "cfg_cb_finish": 0x0B, "cfg_cb_known_packs": 0x0E,
              "cfg_sb_client_info": 0x00, "cfg_sb_plugin_msg": 0x01, "cfg_sb_keepalive": 0x04, "cfg_sb_ping": 0x05, "cfg_sb_ack": 0x0C},
        773: {"sb_chat": 0x02, "sb_keepalive": 0x1E, "cb_chat": [0x72],      "cb_keepalive": 0x2C, "cb_disconnect": 0x20, "login_uuid": True,  "chat_modern": True,  "has_config": True,
              "cfg_cb_disconnect": 0x02, "cfg_cb_keepalive": 0x06, "cfg_cb_ping": 0x04, "cfg_cb_registry": 0x07, "cfg_cb_finish": 0x0B, "cfg_cb_known_packs": 0x0E,
              "cfg_sb_client_info": 0x00, "cfg_sb_plugin_msg": 0x01, "cfg_sb_keepalive": 0x04, "cfg_sb_ping": 0x05, "cfg_sb_ack": 0x0C},
        774: {"sb_chat": 0x02, "sb_keepalive": 0x1E, "cb_chat": [0x72],      "cb_keepalive": 0x2C, "cb_disconnect": 0x20, "login_uuid": True,  "chat_modern": True,  "has_config": True,
              "cfg_cb_disconnect": 0x02, "cfg_cb_keepalive": 0x06, "cfg_cb_ping": 0x04, "cfg_cb_registry": 0x07, "cfg_cb_finish": 0x0B, "cfg_cb_known_packs": 0x0E,
              "cfg_sb_client_info": 0x00, "cfg_sb_plugin_msg": 0x01, "cfg_sb_keepalive": 0x04, "cfg_sb_ping": 0x05, "cfg_sb_ack": 0x0C},
        775: {"sb_chat": 0x02, "sb_keepalive": 0x1E, "cb_chat": [0x73],      "cb_keepalive": 0x2C, "cb_disconnect": 0x20, "login_uuid": True,  "chat_modern": True,  "has_config": True,
              "cfg_cb_disconnect": 0x02, "cfg_cb_keepalive": 0x06, "cfg_cb_ping": 0x04, "cfg_cb_registry": 0x07, "cfg_cb_finish": 0x0B, "cfg_cb_known_packs": 0x0E,
              "cfg_sb_client_info": 0x00, "cfg_sb_plugin_msg": 0x01, "cfg_sb_keepalive": 0x04, "cfg_sb_ping": 0x05, "cfg_sb_ack": 0x0C},
        776: {"sb_chat": 0x02, "sb_keepalive": 0x1F, "cb_chat": [0x74],      "cb_keepalive": 0x2D, "cb_disconnect": 0x20, "login_uuid": True,  "chat_modern": True,  "has_config": True,
              "cfg_cb_disconnect": 0x02, "cfg_cb_keepalive": 0x06, "cfg_cb_ping": 0x04, "cfg_cb_registry": 0x07, "cfg_cb_finish": 0x0B, "cfg_cb_known_packs": 0x0E,
              "cfg_sb_client_info": 0x00, "cfg_sb_plugin_msg": 0x01, "cfg_sb_keepalive": 0x04, "cfg_sb_ping": 0x05, "cfg_sb_ack": 0x0C},
        777: {"sb_chat": 0x02, "sb_keepalive": 0x1F, "cb_chat": [0x74],      "cb_keepalive": 0x2D, "cb_disconnect": 0x20, "login_uuid": True,  "chat_modern": True,  "has_config": True,
              "cfg_cb_disconnect": 0x02, "cfg_cb_keepalive": 0x06, "cfg_cb_ping": 0x04, "cfg_cb_registry": 0x07, "cfg_cb_finish": 0x0B, "cfg_cb_known_packs": 0x0E,
              "cfg_sb_client_info": 0x00, "cfg_sb_plugin_msg": 0x01, "cfg_sb_keepalive": 0x04, "cfg_sb_ping": 0x05, "cfg_sb_ack": 0x0C},
    }

    VERSION_MAP = {
        "1.8": 47, "1.8.9": 47,
        "1.12": 315, "1.12.2": 340,
        "1.16": 735, "1.16.5": 754,
        "1.17": 755,
        "1.18": 757, "1.18.2": 758,
        "1.19": 759, "1.19.2": 760,
        "1.20": 763, "1.20.1": 763,
        "1.20.2": 764, "1.20.3": 765, "1.20.4": 765,
        "1.20.5": 766, "1.20.6": 766,
        "1.21": 767, "1.21.1": 767,
        "1.21.2": 768, "1.21.3": 769,
        "1.21.4": 770,
        "1.21.5": 771,
        "1.21.6": 772, "1.21.7": 772,
        "1.21.8": 773,
        "25.1": 774, "25.2": 774,
        "25.3": 775, "25.4": 775, "25.5": 775,
        "25.6": 776,
        "26.1": 776, "26.2": 777,
    }

    def __init__(self):
        self.socket = None
        self.server_address = None
        self.username = None
        self.protocol_id = None
        self.ids = None
        self.encryptor = None
        self.decryptor = None
        self.compression_threshold = -1
        self.online_mode = False
        self._recv_thread = None
        self._running = False
        self.on_chat = None
        self.on_disconnect = None

    def is_version_supported(self, protocol_version):
        ver_tuple = self._parse_version_tuple(protocol_version)
        if ver_tuple is None:
            return False
        known = sorted(self._version_entries(), key=lambda x: x[0])
        low = known[0][0]
        high = known[-1][0]
        return low <= ver_tuple <= high

    @staticmethod
    def _parse_version_tuple(version_str):
        try:
            parts = tuple(int(p) for p in str(version_str).strip().split('.'))
        except (ValueError, AttributeError):
            return None
        if not parts:
            return None
        parts = parts[:3]
        return parts + (0,) * (3 - len(parts))

    @classmethod
    def _version_entries(cls):
        entries = []
        for name, pid in cls.VERSION_MAP.items():
            t = cls._parse_version_tuple(name)
            if t:
                entries.append((t, pid))
        return entries

    @classmethod
    def resolve_protocol(cls, version_str):
        if version_str in cls.VERSION_MAP:
            return cls.VERSION_MAP[version_str], True
        target = cls._parse_version_tuple(version_str)
        if target is None:
            return cls.VERSION_MAP.get("1.8.9", 47), False
        entries = sorted(cls._version_entries(), key=lambda x: x[0])
        chosen = entries[0][1]
        for ver_tuple, pid in entries:
            if ver_tuple <= target:
                chosen = pid
            else:
                break
        return chosen, False

    @classmethod
    def _packet_ids_for(cls, protocol_id):
        if protocol_id in cls.PACKET_IDS:
            return cls.PACKET_IDS[protocol_id]
        keys = sorted(cls.PACKET_IDS.keys())
        chosen = cls.PACKET_IDS[keys[0]]
        for key in keys:
            if key <= protocol_id:
                chosen = cls.PACKET_IDS[key]
        return chosen

    def connect(self, server_address, username, protocol_version, auth=None,
                on_chat=None, on_disconnect=None, log_func=print):
        self.server_address = server_address
        self.username = username
        self.protocol_id, _ = self.resolve_protocol(protocol_version)
        self.ids = self._packet_ids_for(self.protocol_id)
        self.on_chat = on_chat
        self.on_disconnect = on_disconnect
        self._log = log_func
        self.auth = auth
        self.compression_threshold = -1
        self.online_mode = False

        host, port, srv_host = self.resolve_address(server_address)
        if srv_host:
            self._log(i18n.t('label_srv_resolved', host=server_address, target=f"{srv_host}:{port}"))

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(15)
            self.socket.connect((host, int(port)))
            self.handshake(host, int(port))
            self.login_start()
            self._login_loop()
        except Exception:
            self.disconnect()
            raise

        self._running = True
        self.socket.settimeout(1)
        self._recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
        self._recv_thread.start()

    def handshake(self, host, port):
        packet = bytearray()
        packet += self.write_varint(0x00)
        packet += self.write_varint(self.protocol_id)
        packet += self.write_string(host)
        packet += struct.pack('>H', port)
        packet += self.write_varint(2)
        self.send_packet(packet)

    def login_start(self):
        packet = bytearray()
        packet += self.write_varint(0x00)
        packet += self.write_string(self.username)
        if self.ids["login_uuid"]:
            if self.auth and self.auth.cache.get("uuid"):
                player_uuid = uuid.UUID(self.auth.cache["uuid"])
            else:
                player_uuid = uuid.uuid3(uuid.NAMESPACE_DNS, "OfflinePlayer:" + self.username)
            packet += player_uuid.bytes
        if self.protocol_id == 759:
            packet += b'\x00'
        self.send_packet(packet)

    def _login_loop(self):
        while True:
            pkt = self.read_packet()
            pid, offset = self.read_varint(pkt)

            if pid == 0x00:
                try:
                    reason = json.loads(self.read_string(pkt, offset)[0])
                    text = reason.get("text", str(reason))
                except Exception:
                    text = i18n.t('label_unknown')
                raise Exception(i18n.t('label_auth_failed', reason=text))

            elif pid == 0x01:
                self._handle_encryption_request(pkt, offset)

            elif pid == 0x03:
                threshold, _ = self.read_varint(pkt, offset)
                self.compression_threshold = threshold

            elif pid == 0x02:
                if self.ids.get("has_config"):
                    ack = bytearray()
                    ack += self.write_varint(0x03)
                    self.send_packet(ack)
                    self._config_loop()
                return

            elif pid == 0x04:
                msg_id, off2 = self.read_varint(pkt, offset)
                resp = bytearray()
                resp += self.write_varint(0x02)
                resp += self.write_varint(msg_id)
                self.send_packet(resp)

    def _config_loop(self):
        self._send_client_info()
        self._send_brand()

        deadline = time.time() + 30
        while time.time() < deadline:
            try:
                pkt = self.read_packet()
            except socket.timeout:
                continue
            except Exception:
                break

            pid, offset = self.read_varint(pkt)

            if pid == self.ids.get("cfg_cb_keepalive", -1):
                resp = bytearray()
                resp += self.write_varint(self.ids["cfg_sb_keepalive"])
                resp += pkt[offset:]
                self.send_packet(resp)

            elif pid == self.ids.get("cfg_cb_ping", -1):
                resp = bytearray()
                resp += self.write_varint(self.ids["cfg_sb_ping"])
                resp += pkt[offset:]
                self.send_packet(resp)

            elif pid == self.ids.get("cfg_cb_disconnect", -1):
                try:
                    raw, _ = self.read_string(pkt, offset)
                    reason = json.loads(raw)
                    text = flatten_chat_colored(reason)
                except Exception:
                    text = i18n.t('label_unknown')
                self._log(i18n.t('label_server_disconnected', reason=text))
                raise Exception("Config disconnect")

            elif pid == self.ids.get("cfg_cb_registry", -1):
                ack = bytearray()
                ack += self.write_varint(self.ids["cfg_sb_ack"])
                self.send_packet(ack)

            elif pid == self.ids.get("cfg_cb_known_packs", -1):
                resp = bytearray()
                resp += self.write_varint(self.ids.get("cfg_sb_ack", 0x0C))
                resp += self.write_varint(0)
                self.send_packet(resp)

            elif pid == self.ids.get("cfg_cb_finish", -1):
                ack = bytearray()
                ack += self.write_varint(self.ids["cfg_sb_ack"])
                self.send_packet(ack)
                return

            else:
                ack = bytearray()
                ack += self.write_varint(self.ids.get("cfg_sb_ack", 0x0C))
                self.send_packet(ack)

    def _send_client_info(self):
        packet = bytearray()
        packet += self.write_varint(self.ids["cfg_sb_client_info"])
        packet += self.write_string("en_US")
        packet += struct.pack('B', 10)
        packet += struct.pack('B', 0)
        packet += struct.pack('B', 1)
        packet += struct.pack('B', 0x7F)
        packet += struct.pack('B', 0)
        if self.protocol_id >= 766:
            packet += struct.pack('B', 1)
        if self.protocol_id >= 768:
            packet += struct.pack('B', 0)
        self.send_packet(packet)

    def _send_brand(self):
        packet = bytearray()
        packet += self.write_varint(self.ids["cfg_sb_plugin_msg"])
        packet += self.write_string("minecraft:brand")
        brand = b"MBC"
        packet += self.write_varint(len(brand))
        packet += brand
        self.send_packet(packet)

    def _handle_encryption_request(self, pkt, offset):
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.primitives.asymmetric import padding
        from cryptography.hazmat.primitives.serialization import load_der_public_key

        server_id, offset = self.read_string(pkt, offset)
        pub_len, offset = self.read_varint(pkt, offset)
        public_key = pkt[offset:offset + pub_len]
        offset += pub_len
        vt_len, offset = self.read_varint(pkt, offset)
        verify_token = pkt[offset:offset + vt_len]

        self.online_mode = True

        if not self.auth:
            raise Exception(i18n.t('label_online_mode_required'))

        shared_secret = os.urandom(16)

        server_hash = self._server_id_hash(server_id.encode(), shared_secret, public_key)
        self._log(i18n.t('label_auth_verifying'))
        self.auth.join_server(server_hash)

        rsa_key = load_der_public_key(public_key)
        enc_ss = rsa_key.encrypt(shared_secret, padding.PKCS1v15())
        enc_vt = rsa_key.encrypt(verify_token, padding.PKCS1v15())

        packet = bytearray()
        packet += self.write_varint(0x01)
        packet += self.write_byte_array(enc_ss)
        packet += self.write_byte_array(enc_vt)
        self.send_packet(packet)

        cipher_enc = Cipher(algorithms.AES(shared_secret), modes.CFB8(b'\x00' * 8))
        cipher_dec = Cipher(algorithms.AES(shared_secret), modes.CFB8(b'\x00' * 8))
        self.encryptor = cipher_enc.encryptor()
        self.decryptor = cipher_dec.decryptor()

    @staticmethod
    def _server_id_hash(server_id_bytes, shared_secret, public_key):
        digest = hashlib.sha1(server_id_bytes + shared_secret + public_key).digest()
        value = int.from_bytes(digest, 'big')
        if value >= 2 ** 127:
            value -= 2 ** 128
        return format(value, 'x')

    def send_chat(self, message):
        packet = bytearray()
        packet += self.write_varint(self.ids["sb_chat"])
        packet += self.write_string(message)
        if self.ids["chat_modern"]:
            packet += struct.pack('>q', int(time.time() * 1000))
            packet += struct.pack('>q', 0)
            if self.protocol_id == 759 or self.protocol_id == 760:
                packet += b'\x00'
                packet += b'\x00'
            elif self.protocol_id == 763:
                packet += b'\x00'
            else:
                packet += self.write_varint(0)
        self.send_packet(packet)

    def _recv_loop(self):
        while self._running:
            try:
                pkt = self.read_packet()
                if pkt is None:
                    break
                pid, offset = self.read_varint(pkt)

                if pid == self.ids["cb_keepalive"]:
                    resp = bytearray()
                    resp += self.write_varint(self.ids["sb_keepalive"])
                    resp += pkt[offset:]
                    self.send_packet(resp)

                elif pid in self.ids["cb_chat"]:
                    self._handle_chat_packet(pkt, offset, pid)

                elif pid == self.ids["cb_disconnect"]:
                    try:
                        reason = json.loads(self.read_string(pkt, offset)[0])
                        text = flatten_chat_colored(reason)
                    except Exception:
                        text = i18n.t('label_unknown')
                    self._log(i18n.t('label_server_disconnected', reason=text))
                    break

            except socket.timeout:
                continue
            except Exception:
                break

        self._running = False
        if self.on_disconnect:
            self.on_disconnect()

    def _handle_chat_packet(self, pkt, offset, pid):
        try:
            text = ""
            if len(self.ids["cb_chat"]) == 1:
                raw, _ = self.read_string(pkt, offset)
                try:
                    text = flatten_chat_colored(json.loads(raw))
                except Exception:
                    text = apply_section_codes(raw)
            elif pid == self.ids["cb_chat"][0]:
                if self.protocol_id >= 764:
                    offset += 16
                    _, offset = self.read_varint(pkt, offset)
                    has_sig = pkt[offset]
                    offset += 1
                    if has_sig:
                        offset += 256
                    text_raw, _ = self.read_string(pkt, offset)
                    try:
                        text = flatten_chat_colored(json.loads(text_raw))
                    except Exception:
                        text = apply_section_codes(text_raw)
                else:
                    offset += 16
                    _, offset = self.read_varint(pkt, offset)
                    has_sig = pkt[offset]
                    offset += 1
                    if has_sig:
                        offset += 256
                    text_raw, _ = self.read_string(pkt, offset)
                    try:
                        text = flatten_chat_colored(json.loads(text_raw))
                    except Exception:
                        text = apply_section_codes(text_raw)
            else:
                raw, _ = self.read_string(pkt, offset)
                try:
                    text = flatten_chat_colored(json.loads(raw))
                except Exception:
                    text = apply_section_codes(raw)
            if text and self.on_chat:
                self.on_chat(text)
        except Exception:
            pass

    def send_packet(self, payload):
        body = bytes(payload)
        if self.compression_threshold >= 0:
            if len(body) >= self.compression_threshold:
                data_len = len(body)
                body = self.write_varint(data_len) + zlib.compress(body)
            else:
                body = self.write_varint(0) + body
        frame = self.write_varint(len(body)) + body
        if self.encryptor:
            frame = self.encryptor.update(frame)
        self.socket.sendall(frame)

    def read_packet(self):
        length = self._read_varint_stream()
        if length <= 0 or length > 2**22:
            raise ConnectionError(i18n.t('label_invalid_packet'))
        raw = self._read_exact(length)
        if self.compression_threshold >= 0:
            data_len, offset = self.read_varint(raw)
            if data_len == 0:
                return raw[offset:]
            return zlib.decompress(raw[offset:])
        return raw

    def _read_exact(self, n):
        data = b''
        while len(data) < n:
            chunk = self.socket.recv(min(4096, n - len(data)))
            if not chunk:
                raise ConnectionError(i18n.t('label_connection_closed'))
            if self.decryptor:
                chunk = self.decryptor.update(chunk)
            data += chunk
        return data

    def _read_varint_stream(self):
        num = 0
        shift = 0
        while True:
            b = self._read_exact(1)[0]
            num |= (b & 0x7F) << shift
            if not b & 0x80:
                break
            shift += 7
        return num

    def write_varint(self, value):
        result = bytearray()
        while (value & 0xFFFFFF80) != 0:
            result.append((value & 0x7F) | 0x80)
            value >>= 7
        result.append(value & 0x7F)
        return bytes(result)

    def read_varint(self, data, offset=0):
        result = 0
        shift = 0
        i = offset
        while True:
            byte = data[i]
            result |= (byte & 0x7F) << shift
            if (byte & 0x80) == 0:
                break
            shift += 7
            i += 1
        return result, i + 1

    def write_string(self, value):
        encoded = value.encode('utf-8')
        return self.write_varint(len(encoded)) + encoded

    def read_string(self, data, offset=0):
        length, offset = self.read_varint(data, offset)
        return data[offset:offset + length].decode('utf-8', errors='replace'), offset + length

    def write_byte_array(self, value):
        return self.write_varint(len(value)) + value

    def resolve_address(self, address):
        if ':' in address:
            host, port = address.rsplit(':', 1)
            try:
                port = int(port)
            except ValueError:
                host = address
                port = 25565
            return host, port, None

        host = address
        port = 25565
        srv_host = None

        if _DNS_AVAILABLE:
            try:
                srv_name = dns.name.from_text('_minecraft._tcp.' + host)
                answers = dns.resolver.resolve(srv_name, 'SRV')
                records = [(r.priority, r.weight, str(r.target).rstrip('.'), r.port) for r in answers]
                records.sort(key=lambda x: (x[0], -x[1]))
                if records:
                    _, _, target, srv_port = records[0]
                    host = target
                    port = srv_port
                    srv_host = target
            except Exception:
                pass

        return host, port, srv_host

    def parse_address(self, address):
        host, port, _ = self.resolve_address(address)
        return host, port

    def is_alive(self):
        return self._running

    def disconnect(self):
        self._running = False
        if self.socket:
            try:
                self.socket.close()
            except Exception:
                pass
            self.socket = None
        self.encryptor = None
        self.decryptor = None
