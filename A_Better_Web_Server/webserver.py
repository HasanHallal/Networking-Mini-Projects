import socket
import sys
import os

def get_content_type(s):
    types={ ".txt":"text/plain",
           ".html":"text/html",
           ".pdf":"application/pdf",
           ".jpeg":"image/jpeg",
           ".gif":"image/gif"
    }

    file_name=os.path.splitext(s)[-1]
    if file_name in types:
        return types[file_name]
    else:
        return "application/octet-stream"



s=socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
if len(sys.argv)==2:
    s.bind(('',int(sys.argv[1])))
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
        if len(d) > 65536:
            break
    server_root=os.path.abspath(".")
    try:
        d=d.decode("ISO-8859-1")
        header=d.split("\r\n")[0]
        parts=header.split(" ")
        if len(parts)!=3:
            text="HTTP/1.1 400 Bad Request\r\nContent-Type: text/plain\r\nContent-Length: 11\r\nConnection: close\r\n\r\nBad Request"
            new_socket.sendall(text.encode("ISO-8859-1"))
            continue
        method,path,protocol=parts
        file_path = os.path.abspath(os.path.join(server_root, path.lstrip("/")))
        try:
            with open(file_path, "rb") as fp:
                data = fp.read() 
        except:
            text="HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\nContent-Length: 13\r\nConnection: close\r\n\r\n404 not found"
            new_socket.sendall(text.encode("ISO-8859-1"))
            continue
        text=f"HTTP/1.1 200 OK\r\nContent-Type: {get_content_type(file_path)}\r\nContent-Length: {len(data)}\r\nConnection: close\r\n\r\n"
        new_socket.sendall(text.encode("ISO-8859-1")+data)
    finally:
        new_socket.close()

        
    