import socket
import struct

class ConnectionManager:
    def __init__(self):
        self.socket = None
        self.server_address = None
        self.username = None
        self.protocol_version = None
    
    def connect(self, server_address, username, protocol_version):
        self.server_address = server_address
        self.username = username
        self.protocol_version = protocol_version
        
        host, port = self.parse_address(server_address)
        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, int(port)))
            self.handshake(protocol_version, host, int(port))
            self.login(username)
        except Exception as e:
            if self.socket:
                self.socket.close()
            raise Exception(f"Connection failed: {str(e)}")
    
    def parse_address(self, address):
        if ':' in address:
            host, port = address.rsplit(':', 1)
            return host, port
        return address, "25565"
    
    def handshake(self, protocol_version, host, port):
        version_map = {
            "1.8": 47, "1.8.9": 47,
            "1.12": 315, "1.12.2": 340,
            "1.16": 735, "1.16.5": 754,
            "1.17": 755, "1.18": 757, "1.18.2": 758,
            "1.19": 759, "1.19.2": 760,
            "1.20": 763, "1.20.1": 763,
            "26.2": 763
        }
        
        version_id = version_map.get(protocol_version, 47)
        
        packet = bytearray()
        packet += self.write_varint(0x00)
        packet += self.write_varint(version_id)
        packet += self.write_string(host)
        packet += struct.pack('>H', port)
        packet += self.write_varint(2)
        
        self.send_packet(packet)
    
    def login(self, username):
        packet = bytearray()
        packet += self.write_varint(0x00)
        packet += self.write_string(username)
        
        self.send_packet(packet)
    
    def send_packet(self, data):
        packet = self.write_varint(len(data)) + data
        self.socket.sendall(packet)
    
    def write_varint(self, value):
        result = bytearray()
        while (value & 0xFFFFFF80) != 0:
            result.append((value & 0x7F) | 0x80)
            value >>= 7
        result.append(value & 0x7F)
        return result
    
    def write_string(self, value):
        encoded = value.encode('utf-8')
        return self.write_varint(len(encoded)) + encoded
    
    def get_connection(self):
        return self.socket
    
    def disconnect(self):
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
