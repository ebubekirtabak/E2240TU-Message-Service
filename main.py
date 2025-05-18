import threading
import time
import os

from E22 import E22, Config
from find_lora_port import get_lora_port
from message_pb2 import SensorData, DeviceInfo, UserInfo
from message_receiver import MessageReceiver
from message_sender import MessageSender
from dotenv import load_dotenv


load_dotenv()

MAX_PACKET_SIZE = int(os.getenv("MAX_PACKET_SIZE", 128))
HEADER_SIZE = int(os.getenv("HEADER_SIZE", 5))
SYNC_BYTE = int(os.getenv("SYNC_BYTE", 0xAA))
PAYLOAD_SIZE = MAX_PACKET_SIZE - HEADER_SIZE


def toggle_software_mode_switching(lora: E22, enable: bool):
    if enable is True:
        lora.software_mode_switch('configuration')
    else:
        lora.software_mode_switch('transmission')

def set_configs(lora: E22) -> bool:
    try: 
        cfg = Config()
        config = lora.config_get()
        channel = config[4]
        print(f"Current channel: {channel} (0x{channel:02X} = {410 + channel}MHz)")
        print('Configuring LoRa module...', config.hex())
        cfg.set(config)
        cfg.set_address(0xFFFF)
        cfg.set_channel(0x04)
        cfg.set_serial_baud(9600)
        cfg.set_transmitting_power(3)
        lora.config_set(cfg.get())
        return True
    except Exception as e:
        print("Error setting configuration:", e)
        return False


if __name__ == '__main__':
    lora_port = get_lora_port(True)
    print(f"Using LoRa port: {lora_port}")
    if lora_port is None:
        print("No LoRa port found. Exiting.")
        exit(1)
    time.sleep(1)
    lora = E22(lora_port, timeout=1)
    toggle_software_mode_switching(lora, enable=True)
    time.sleep(1)
    # config
    set_configs(lora)
    time.sleep(1)
    toggle_software_mode_switching(lora, enable=False)
    time.sleep(2)

    def send_loop():
        while True:
            deviceInfo = DeviceInfo()
            deviceInfo.lat = 37.7749
            deviceInfo.log = -122.4194
            deviceInfo.device_id = "12345"
            userInfo = UserInfo()
            userInfo.user_id = "67890"
            userInfo.user_name = "John Doe"
            data = SensorData()
            data.device_info.CopyFrom(deviceInfo)
            data.user_info.CopyFrom(userInfo)
            data.id = 1
            data.temperature = 22.5
            data.humidity = 65.2
            data.timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            data.text = """Karen Saxby is the author of the Storyfun series, published by Cambridge University Press. She also co-wrote the Fun For series, and is an experienced Cambridge English consultant. In this article, she explores how stories can be used to make young people's language learning meaningful and memorable.
As a child, I loved sitting on my grandfather's lap while he read me stories. I remember most of them even though I am now a grandparent, too! As a child, I was blissfully unaware that, as I listened to the stories, I was also learning new words and ways in which those new words combined to communicate ideas and life lessons.
A good story encourages us to turn the next page and read more. We want to find out what happens next and what the main characters do and what they say to each other. We may feel excited, sad, afraid, angry or really happy. This is because the experience of reading or listening to a story is much more likely to make us 'feel' that we are part of the story, too. Just like in our 'real' lives, we might love or hate different characters in the story. Perhaps we recognise ourselves or others in some of them. Perhaps we have similar problems.
Because of this natural empathy with the characters, our brains process the reading of stories differently from the way we read factual information. Our brains don't always recognise the difference between an imagined situation and a real one so the characters become 'alive' to us. What they say and do is therefore more meaningful. This is why the words and structures that relate a story's events, descriptions and conversations are processed in this deeper way.
"""
            data_bytes = data.SerializeToString()
            MessageSender(lora, sync_byte=SYNC_BYTE, payload_size=PAYLOAD_SIZE).send(data_bytes=data_bytes)
            time.sleep(30)
    threading.Thread(target=send_loop, daemon=True).start()


    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Closing LoRa...")
        lora.close()