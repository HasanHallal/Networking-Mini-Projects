import sys
import socket

# How many bytes is the word length?
WORD_LEN_SIZE = 2

def usage():
    print("usage: wordclient.py server port", file=sys.stderr)

packet_buffer = b''

def get_next_word_packet(s):
    global packet_buffer
    while True:
        if len(packet_buffer)>2:
            byte_length=packet_buffer[:2]
            length=int.from_bytes(byte_length,"big")
            if len(packet_buffer) < 2+length:
                data=s.recv(4096)
                packet_buffer+=data
                continue
            word_packet=packet_buffer[:2+length]
            packet_buffer=packet_buffer[2+length:]
            return word_packet
        data=s.recv(4096)
        if len(data)==0:
            return None
        packet_buffer+=data




def extract_word(word_packet):
    byte_word=word_packet[2:]
    word=byte_word.decode("UTF-8")
    return word


# Do not modify:

def main(argv):
    try:
        host = argv[1]
        port = int(argv[2])
    except:
        usage()
        return 1

    s = socket.socket()
    s.connect((host, port))

    print("Getting words:")

    while True:
        word_packet = get_next_word_packet(s)

        if word_packet is None:
            break

        word = extract_word(word_packet)

        print(f"    {word}")

    s.close()

if __name__ == "__main__":
    sys.exit(main(sys.argv))