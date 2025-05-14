import serial.tools.list_ports

def find_lora_ports():
    lora_ports = []
    for port in serial.tools.list_ports.comports():
        if "1A86:7523" in port.hwid:  
            print(f"Found LoRa port: {port.device}")
            print(f"Port info: {port}")
            print(f"Port name: {port.name}")
            print(f"Port description: {port.description}")
            lora_ports.append(port.device)

    return lora_ports

def get_lora_port(wait_for_input=False):
    ports = find_lora_ports() 
    if len(ports) == 1 or (len(ports) > 1 and not wait_for_input): 
        lora_port = ports[0]
        print(f"Using LoRa port: {lora_port}")
        return lora_port
    if len(ports) > 1:
        print("Multiple LoRa ports found. Please specify one.")
        for i, port in enumerate(ports):
            print(f"{i}: {port}")
        choice = int(input("Select the port number: "))
        if 0 <= choice < len(ports):
            return ports[choice]
        else:
            print("Invalid choice.")
            return None
    else:
        print("No LoRa port found.")
        return None
