import os
import json
import uuid
import zlib
import hashlib
import socket
import struct
import threading
from src import i18n

try:
    import dns.resolver
    import dns.name
    _DNS_AVAILABLE = True
except ImportError:
    _DNS_AVAILABLE = False

class ConnectionManager:
    PACKET_IDS = {
        47:  {"sb_chat": 0x01, "sb_keepalive": 0x00, "cb_chat": [0x02],     "cb_keepalive": 0x00, "cb_disconnect": 0x40, "login_uuid": False, "chat_modern": False},
        340: {"sb_chat": 0x02, "sb_keepalive": 0x0B, "cb_chat": [0x0F],     "cb_keepalive": 0x1F, "cb_disconnect": 0x40, "login_uuid": False, "chat_modern": False},
        735: {"sb_chat": 0x03, "sb_keepalive": 0x0F, "cb_chat": [0x0E],     "cb_keepalive": 0x1F, "cb_disconnect": 0x1B, "login_uuid": False, "chat_modern": False},
        754: {"sb_chat": 0x03, "sb_keepalive": 0x0F, "cb_chat": [0x0E],     "cb_keepalive": 0x1F, "cb_disconnect": 0x1B, "login_uuid": False, "chat_modern": False},
        755: {"sb_chat": 0x03, "sb_keepalive": 0x0F, "cb_chat": [0x0F],     "cb_keepalive": 0x1E, "cb_disconnect": 0x19, "login_uuid": False, "chat_modern": False},
        757: {"sb_chat": 0x03, "sb_keepalive": 0x0F, "cb_chat": [0x0F],     "cb_keepalive": 0x1E, "cb_disconnect": 0x19, "login_uuid": False, "chat_modern": False},
        758: {"sb_chat": 0x03, "sb_keepalive": 0x10, "cb_chat": [0x0F],     "cb_keepalive": 0x1E, "cb_disconnect": 0x19, "login_uuid": False, "chat_modern": False},
        759: {"sb_chat": 0x04, "sb_keepalive": 0x11, "cb_chat": [0x30, 0x5F], "cb_keepalive": 0x1E, "cb_disconnect": 0x17, "login_uuid": False, "chat_modern": True},
        760: {"sb_chat": 0x04, "sb_keepalive": 0x11, "cb_chat": [0x30, 0x5F], "cb_keepalive": 0x1E, "cb_disconnect": 0x17, "login_uuid": True,  "chat_modern": True},
        763: {"sb_chat": 0x04, "sb_keepalive": 0x12, "cb_chat": [0x32, 0x64], "cb_keepalive": 0x22, "cb_disconnect": 0x19, "login_uuid": True,  "chat_modern": True},
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
        "1.21": 767, "1.21.1": 767
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
        return protocol_version in self.VERSION_MAP

    def connect(self, server_address, username, protocol_version, auth=None,
                on_chat=None, on_disconnect=None, log_func=print):
        self.server_address = server_address
        self.username = username
        self.protocol_id = self.VERSION_MAP.get(protocol_version, 47)
        self.ids = self.PACKET_IDS.get(self.protocol_id, self.PACKET_IDS[47])
        self.on_chat = on_chat
        self.on_disconnect = on_disconnect
        self._log = log_func
        self.auth = auth

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
        except Exception as e:
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
                return

            elif pid == 0x04:
                msg_id, off2 = self.read_varint(pkt, offset)
                resp = bytearray()
                resp += self.write_varint(0x02)
                resp += self.write_varint(msg_id)
                self.send_packet(resp)

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
            packet += struct.pack('>q', 0)
            packet += struct.pack('>q', 0)
            if self.protocol_id == 759 or self.protocol_id == 760:
                packet += b'\x00'
                packet += b'\x00'
            else:
                packet += self.write_varint(0)
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
                        text = self._flatten_chat(reason)
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
                text = self._flatten_chat(json.loads(raw))
            elif pid == self.ids["cb_chat"][0]:
                offset += 16
                _, offset = self.read_varint(pkt, offset)
                has_sig = pkt[offset]
                offset += 1
                if has_sig:
                    offset += 256
                text, _ = self.read_string(pkt, offset)
            else:
                raw, _ = self.read_string(pkt, offset)
                text = self._flatten_chat(json.loads(raw))
            if text and self.on_chat:
                self.on_chat(text)
        except Exception:
            pass

    @staticmethod
    def _flatten_chat(obj):
        if isinstance(obj, str):
            return obj
        if isinstance(obj, dict):
            text = obj.get("text", "")
            for extra in obj.get("extra", []):
                text += ConnectionManager._flatten_chat(extra)
            if "translate" in obj and not obj.get("extra"):
                args = "".join(ConnectionManager._flatten_chat(a) for a in obj.get("with", []))
                return args if not text else text
            return text
        if isinstance(obj, list):
            return "".join(ConnectionManager._flatten_chat(i) for i in obj)
        return str(obj)

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
