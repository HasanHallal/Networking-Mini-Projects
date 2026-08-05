def transform_IP_into_byte(ip):
    octets = ip.split(".")
    return bytes(int(octet) for octet in octets)

def checksum(pseudo,tcp_data):
    data=pseudo+tcp_data
    total=0
    offset = 0 # byte offset into data
    while offset < len(data):
        # Slice 2 bytes out and get their value:
        word = int.from_bytes(data[offset:offset + 2], "big")
        total+=word
        total = (total & 0xffff) + (total >> 16)
        offset += 2 # Go to the next 2-byte value
    return (~total) & 0xffff

for i in range(10):
    with open(f"tcp_addrs_{i}.txt", "r") as file:
        data=file.read()

    source_ip,dest_ip=data.split()
    source_ip_byte,dest_ip_byte=transform_IP_into_byte(source_ip),transform_IP_into_byte(dest_ip)

    with open(f"tcp_data_{i}.dat", "rb") as fp:
        tcp_data = fp.read()
        tcp_length = len(tcp_data) 

    tcp_checksum=tcp_data[16:18]
    tcp_zero_chksum=tcp_data[:16]+b'\x00\x00'+tcp_data[18:]
    if len(tcp_zero_chksum) % 2 == 1:
        tcp_zero_chksum += b'\x00'
    IP_pseudo_header=source_ip_byte+dest_ip_byte+b'\x00\x06'+tcp_length.to_bytes(2,"big")

    chcksum=checksum(IP_pseudo_header,tcp_zero_chksum)
    chcksum_bytes=chcksum.to_bytes(2,"big")

    if chcksum_bytes==tcp_checksum:
        print("PASS!")
    else:
        print("FAIL!")

        
        

    