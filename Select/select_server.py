# Example usage:
#
# python select_server.py 3490

import sys
import socket
import select

def run_server(port):
    listener = socket.socket()
    listener.bind(('',port))
    listener.listen()
    sockets={listener}
    while True:
        readable , _ , _ = select.select(sockets,{},{})
        for s in readable:
            if s is listener:
                client, address = s.accept()
                print(f"({address}): connected")
                sockets.add(client)
            else:
                text = s.recv(4096)
                address = s.getpeername()
                if text:
                    length = len(text)
                    print(f"({address}) {length} bytes: {text!r}")
                else:
                    sockets.remove(s)
                    print(f"({address}): disconnected")
                    s.close()

#--------------------------------#
# Do not modify below this line! #
#--------------------------------#

def usage():
    print("usage: select_server.py port", file=sys.stderr)

def main(argv):
    try:
        port = int(argv[1])
    except:
        usage()
        return 1

    run_server(port)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
