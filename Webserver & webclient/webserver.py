import socket
import sys
s=socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
if len(sys.argv)==2:
    s.bind(('',sys.argv[1]))
else:
    s.bind(('',28333))
s.listen()
while True:
    new_conn=s.accept()
    new_socket=new_conn[0]
    d=b""
    while b"\r\n\r\n" not in d:
        chunk=new_socket.recv(4096)
        if not chunk:
            break
        d+=chunk
    text="HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 6\r\nConnection: close\r\n\r\nHello!"
    b=text.encode("ISO-8859-1")
    new_socket.sendall(b)
    new_socket.close()
        
