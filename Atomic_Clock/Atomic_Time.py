import socket
import time

s=socket.socket()
s.connect(("time.nist.gov",37))
d=s.recv(4)
s.close()
nist=int.from_bytes(d)
print("NIST time  :",nist)

def system_seconds_since_1900():

# Number of seconds between 1900-01-01 and 1970-01-01
    seconds_delta = 2208988800
    seconds_since_unix_epoch = int(time.time())
    seconds_since_1900_epoch = seconds_since_unix_epoch + seconds_delta
    return seconds_since_1900_epoch

print("SYSTEM time  :",system_seconds_since_1900())