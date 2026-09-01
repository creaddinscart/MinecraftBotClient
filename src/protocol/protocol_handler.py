import struct

class ProtocolHandler:
    CHAT_MESSAGE_PACKET_ID = 0x02
    
    def __init__(self):
        self.protocol_version = None
    
    def send_chat_message(self, connection, message):
        if not connection:
            raise Exception("No active connection")
        
        packet = bytearray()
        packet += self.write_varint(self.CHAT_MESSAGE_PACKET_ID)
        packet += self.write_string(message)
        
        self.send_packet(connection, packet)
    
    def send_packet(self, connection, data):
        packet_length = self.write_varint(len(data))
        connection.sendall(packet_length + data)
    
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
    
    def read_string(self, data, offset=0):
        length, offset = self.read_varint(data, offset)
        return data[offset:offset+length].decode('utf-8'), offset + length
