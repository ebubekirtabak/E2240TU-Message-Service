import random
import time

from math import ceil
from E22 import E22
from short_uuid import get_short_uuid


class MessageSender:
    def __init__(self, lora: E22, sync_byte: int = 0xAA, payload_size: int = 64):
        self.sync_byte = sync_byte
        self.payload_size = payload_size
        self.lora = lora

def send(self, data_bytes: bytes, message_type: int = 0):
    message_id = get_short_uuid()
    msg_id_int = random.randint(0, 255) 
    print("Serialized data (hex):", data_bytes.hex(), "length:", len(data_bytes))
    total_packets = ceil(len(data_bytes) / self.payload_size)
    print(f"Sending message {message_id} (id={msg_id_int}) in {total_packets} packets for {len(data_bytes)} bytes")
    for i in range(total_packets):
        chunk = data_bytes[i * self.payload_size : (i + 1) * self.payload_size]
        chunk_len = len(chunk)
        print(f"[SEND] Packet {i+1}/{total_packets} - chunk_len: {chunk_len}")
        header = bytes([msg_id_int, i, message_type, total_packets, chunk_len])
        packet = bytes([self.sync_byte]) + header + chunk
        print(f"Sending packet {message_id} - {i+1}/{total_packets} - {chunk_len} bytes")
        print("Packet data (hex):", packet)
        self.lora.send(packet)
        self.lora.ser.flush()
        time.sleep(1)  