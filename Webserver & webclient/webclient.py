import socket
s=socket.socket()
s.connect(("localhost",28333))
text="GET / HTTP/1.1\r\nHost: localhost:28333\r\nConnection: close\r\n\r\n"
b=text.encode("ISO-8859-1")
s.sendall(b)
d=s.recv(4096)
while len(d)!=0:
    print(d.decode("ISO-8859-1"))
    d=s.recv(4096)
s.close()