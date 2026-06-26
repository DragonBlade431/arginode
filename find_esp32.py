import serial.tools.list_ports
import sys

def list_com_ports():
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("[ERROR] No serial ports found. Make sure your ESP32 is connected via USB.")
        return []
    
    print("\nAvailable Serial Ports:")
    for i, port in enumerate(ports):
        print(f"  [{i}] {port.device} - {port.description}")
    return ports

def find_esp32():
    ports = serial.tools.list_ports.comports()
    # Common strings in ESP32 driver descriptions
    esp32_keywords = ["CP210", "CH340", "USB-to-Serial", "Silicon Labs", "Arduino"]
    
    for port in ports:
        if any(key in port.description for key in esp32_keywords):
            return port.device
    return None

if __name__ == "__main__":
    # Check if we are just being asked for the port string
    if len(sys.argv) > 1 and sys.argv[1] == "--get-port":
        esp_port = find_esp32()
        if esp_port:
            print(esp_port)
        else:
            ports = serial.tools.list_ports.comports()
            if len(ports) == 1:
                print(ports[0].device)
            else:
                sys.exit(1)
        sys.exit(0)

    # Regular interactive output
    ports = list_com_ports()
    esp_port = find_esp32()
    
    if esp_port:
        print(f"\n[OK] Potential ESP32 detected on: {esp_port}")
    else:
        print("\n[!] Could not automatically identify an ESP32. You might need to select the port manually.")
