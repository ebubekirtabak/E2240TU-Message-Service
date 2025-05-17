import serial

from collections import defaultdict
from message_pb2 import SensorData
from E22 import E22


class MessageReceiver:

    def __init__(self, lora: E22, header_size, sync_byte):
        self.HEADER_SIZE = header_size
        self.SYNC_BYTE = sync_byte
        self.lora = lora

    def read_exact(self, ser, n):
        buf = b''
        while len(buf) < n:
            chunk = ser.read(n - len(buf))
            if not chunk:
                break 
            buf += chunk
        return buf
    
    def recv_packet(self):
        while True:
            data = self.read_exact(self.lora.ser, 1)
            if data and data[0] == self.SYNC_BYTE:
                header = self.read_exact(self.lora.ser, self.HEADER_SIZE)
                if len(header) == self.HEADER_SIZE:
                    msg_id, packet_id, message_type, total_packets, chunk_len = header
                    chunk_data = self.read_exact(self.lora.ser, chunk_len)
                    return msg_id, packet_id, message_type, total_packets, chunk_data
            
    def receive_message(self):
        messages = defaultdict(dict)
        packet_counts = {}

        while True:
            try:
                packet = self.recv_packet()
                print("Received packet:", packet)
                if packet and len(packet) >= 4:
                    print("Received packet (hex):", packet)
                    msg_id = packet[0]
                    packet_id = packet[1]
                    message_type = packet[2]
                    total_packets = packet[3]
                    chunk_data = packet[4]

                    print(f"[RECV] Packet {packet_id+1}/{total_packets} - chunk_len: {len(chunk_data)}")
                    # Store chunks in a dict for each message_id
                    messages[msg_id][packet_id] = chunk_data
                    packet_counts[msg_id] = total_packets

                    print(f"[Message {msg_id}] Packet {packet_id + 1} / {total_packets} - {len(chunk_data)} bytes Type={message_type}")

                    if (
                        len(messages[msg_id]) == packet_counts[msg_id] and
                        all(i in messages[msg_id] for i in range(packet_counts[msg_id]))
                    ):
                        missing = [i for i in range(packet_counts[msg_id]) if i not in messages[msg_id]]
                        if missing:
                            print(f"[WARN] Missing packets: {missing}")
                        full_data = b''.join(messages[msg_id][i] for i in range(packet_counts[msg_id]))
                        print(f"Reassembled full_data (hex): {full_data.hex()}")  # Debug log
                        print("Reassembled length:", len(full_data))

                        try:
                            message = SensorData()
                            message.ParseFromString(full_data)
                            print("✅ Message received:", message)
                        except Exception as e:
                            print("❌ Protobuf decode error:", e)
                            print("Raw full_data (hex):", full_data.hex())

                        del messages[msg_id]
                        del packet_counts[msg_id]

            except serial.SerialException as e:
                print("Serial error:", e)

    def start_receiving_messages(self):
        print("Starting to receive messages...")
        self.receive_message()
        print("Receiver stopped.")