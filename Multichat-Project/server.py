from chatui import init_windows, read_command, print_message, end_windows
import json
import socket
import sys
import select


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

buffer = {}

names = {}

listener = socket.socket()
listener.bind(('',int(sys.argv[1])))
listener.listen()
sockets = {listener}
while True:
    readable, _ , _ = select.select(sockets,{},{})
    for s in readable:
        if s is listener:
            client, address = s.accept()
            sockets.add(client)
            buffer[client] = b""
        else:
            data = s.recv(4960)
            if data:
                buffer[s] += data
                packets, remaining_data = extract(buffer[s])
                buffer[s] = remaining_data
                for packet in packets:
                    if packet["type"] == "hello":
                        names[s] = packet["nick"]
                        join = {
                            "type": "join",
                            "nick": names[s]
                        }
                        json_join = json.dumps(join)
                        json_bytes = json_join.encode("UTF-8")
                        length = len(json_bytes)
                        length_bytes = length.to_bytes(2,"big")
                        json_bytes = length_bytes + json_bytes
                        for so in sockets:
                            if so is listener:
                                continue
                            so.sendall(json_bytes)
            
                    elif packet["type"] == "chat":
                        packet["nick"] = names[s]
                        json_packet = json.dumps(packet)
                        json_bytes = json_packet.encode("UTF-8")
                        length = len(json_bytes)
                        length_bytes = length.to_bytes(2,"big")
                        json_bytes = length_bytes + json_bytes
                        for so in sockets:
                            if so is listener:
                                continue
                            so.sendall(json_bytes)
            else:
                sockets.remove(s)
                buffer.pop(s,None)
                s.close()
                leave = {
                    "type": "leave",
                    "nick": names[s]
                }
                names.pop(s,None)
                json_leave = json.dumps(leave)
                json_bytes = json_leave.encode("UTF-8")
                length = len(json_bytes)
                length_bytes = length.to_bytes(2,"big")
                json_bytes = length_bytes + json_bytes
                for so in sockets:
                    if so is listener:
                        continue
                    so.sendall(json_bytes)
                

