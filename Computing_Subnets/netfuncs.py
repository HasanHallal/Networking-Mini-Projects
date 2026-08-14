import sys
import json

def ipv4_to_value(ipv4_addr):
    octet=ipv4_addr.split(".")
    octet=tuple(int(x) for x in octet)
    return  (octet[0] << 24) | (octet[1] << 16) | (octet[2] << 8) | octet[3]

def value_to_ipv4(addr):
    octet=addr >> 24 & 0xFF, addr>>16 & 0xFF, addr>>8 & 0xFF, addr & 0xFF
    return f"{octet[0]}.{octet[1]}.{octet[2]}.{octet[3]}"
    

def get_subnet_mask_value(slash):
    subnet=slash.split("/")[1]
    return ((1 << int(subnet))-1) << (32-int(subnet))


def ips_same_subnet(ip1, ip2, slash):
    mask=get_subnet_mask_value(slash)
    value1=ipv4_to_value(ip1)
    value2=ipv4_to_value(ip2)
    if mask & value1 == mask & value2:
        return True
    else:
        return False

def get_network(ip_value, netmask):
    return netmask & ip_value

def find_router_for_ip(routers, ip):
    
    for ip1 in routers:
        if ips_same_subnet(ip1,ip,routers[ip1]["netmask"]):
            return ip1
    return None

def usage():
    print("usage: netfuncs.py infile.json", file=sys.stderr)

def read_routers(file_name):
    with open(file_name) as fp:
        json_data = fp.read()
        
    return json.loads(json_data)

def print_routers(routers):
    print("Routers:")

    routers_list = sorted(routers.keys())

    for router_ip in routers_list:

        # Get the netmask
        slash_mask = routers[router_ip]["netmask"]
        netmask_value = get_subnet_mask_value(slash_mask)
        netmask = value_to_ipv4(netmask_value)

        # Get the network number
        router_ip_value = ipv4_to_value(router_ip)
        network_value = get_network(router_ip_value, netmask_value)
        network_ip = value_to_ipv4(network_value)

        print(f" {router_ip:>15s}: netmask {netmask}: " \
            f"network {network_ip}")

def print_same_subnets(src_dest_pairs):
    print("IP Pairs:")

    src_dest_pairs_list = sorted(src_dest_pairs)

    for src_ip, dest_ip in src_dest_pairs_list:
        print(f" {src_ip:>15s} {dest_ip:>15s}: ", end="")

        if ips_same_subnet(src_ip, dest_ip, "/24"):
            print("same subnet")
        else:
            print("different subnets")

def print_ip_routers(routers, src_dest_pairs):
    print("Routers and corresponding IPs:")

    all_ips = sorted(set([i for pair in src_dest_pairs for i in pair]))

    router_host_map = {}

    for ip in all_ips:
        router = str(find_router_for_ip(routers, ip))
        
        if router not in router_host_map:
            router_host_map[router] = []

        router_host_map[router].append(ip)

    for router_ip in sorted(router_host_map.keys()):
        print(f" {router_ip:>15s}: {router_host_map[router_ip]}")

def main(argv):
    try:
        router_file_name = argv[1]
    except:
        usage()
        return 1

    json_data = read_routers(router_file_name)

    routers = json_data["routers"]
    src_dest_pairs = json_data["src-dest"]

    print_routers(routers)
    print()
    print_same_subnets(src_dest_pairs)
    print()
    print_ip_routers(routers, src_dest_pairs)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
    
