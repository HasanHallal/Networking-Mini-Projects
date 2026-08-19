from chatui import init_windows, read_command, print_message, end_windows
import json
import socket
import sys
import threading


client = socket.socket()
client.connect(("localhost",int(sys.argv[2])))
hello = {
    "type":"hello",
    "nick": sys.argv[1]
}
json_hello = json.dumps(hello)
json_bytes = json_hello.encode("UTF-8")
length = len(json_bytes)
length_bytes = length.to_bytes(2,"big")
json_bytes = length_bytes + json_bytes
client.sendall(json_bytes)

init_windows()

def waiting_for_input():
    while True:
        try:
            command = read_command(f"{sys.argv[1]}> ")
        except:
            break

        text = {
            "type": "chat",
            "message": command
        }

        json_text = json.dumps(text)
        json_bytes = json_text.encode("UTF-8")
        length = len(json_bytes)
        length_bytes = length.to_bytes(2,"big")
        json_bytes = length_bytes + json_bytes
        client.sendall(json_bytes)

t1 = threading.Thread(target=waiting_for_input, daemon=True)
t1.start()

def full_packet(data):
    if len(data) >= 2:
        byte_length = data[:2]
        length = int.from_bytes(byte_length,"big")
        if len(data) < 2 + length:
            return False
        else:
            return True

def extract(data):
    packets = []
    while full_packet(data):
        byte_length = data[:2]
        length = int.from_bytes(byte_length,"big")
        json_load = data[2:2+length]
        string = json_load.decode("UTF-8")
        packet = json.loads(string)
        data = data[2 + length:]
        packets.append(packet)
    return packets, data

while True:
    buffer = b""
    data = client.recv(4096)
    buffer += data
    packets, remaining_data = extract(buffer)
    buffer = remaining_data
    for packet in packets:
        if packet["type"] == "chat":
            print_message(f"{packet["nick"]}: {packet["message"]}")
        elif packet["type"] == "join":
            print_message(f"*** {packet["nick"]} has joined the server")
        elif packet["type"] == "leave":
            print_message(f"*** {packet["nick"]} has left the server")

end_windows()


