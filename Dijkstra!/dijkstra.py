import sys
import json
import math  # If you want to use math.inf for infinity

def ipv4_to_value(ipv4_addr):
    octet=ipv4_addr.split(".")
    octet=tuple(int(x) for x in octet)
    return  (octet[0] << 24) | (octet[1] << 16) | (octet[2] << 8) | octet[3]

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
    
def find_router_for_ip(routers, ip):
    
    for ip1 in routers:
        if ips_same_subnet(ip1,ip,routers[ip1]["netmask"]):
            return ip1
    return None
    
def dijkstras_shortest_path(routers, src_ip, dest_ip):

    to_visit=set()
    distance={}
    parent={}
    src_router=find_router_for_ip(routers,src_ip)
    dest_router = find_router_for_ip(routers,dest_ip)

    if src_router == dest_router:
        return []

    for node in routers:
        to_visit.add(node)
        distance[node] = math.inf
        parent[node] = None
    distance[src_router] = 0

    while to_visit:

        smallest = math.inf
        current_node = None

        for node in to_visit:
            if distance[node] < smallest:
                smallest = distance[node]
                current_node = node
        if current_node == None:
            break

        to_visit.remove(current_node)
        for neighbor in routers[current_node]["connections"]:
            if neighbor in to_visit:
                distance_neighbor = distance[current_node] + routers[current_node]["connections"][neighbor]["ad"]
                if distance_neighbor < distance[neighbor]:
                    distance[neighbor] = distance_neighbor
                    parent[neighbor] = current_node

    current_node = dest_router
    path=[]
    while current_node != src_router:
        path.append(current_node)
        current_node = parent[current_node]
    path.append(src_router)
    path.reverse()

    return path
 

#------------------------------
# DO NOT MODIFY BELOW THIS LINE
#------------------------------
def read_routers(file_name):
    with open(file_name) as fp:
        data = fp.read()

    return json.loads(data)

def find_routes(routers, src_dest_pairs):
    for src_ip, dest_ip in src_dest_pairs:
        path = dijkstras_shortest_path(routers, src_ip, dest_ip)
        print(f"{src_ip:>15s} -> {dest_ip:<15s}  {repr(path)}")

def usage():
    print("usage: dijkstra.py infile.json", file=sys.stderr)

def main(argv):
    try:
        router_file_name = argv[1]
    except:
        usage()
        return 1

    json_data = read_routers(router_file_name)

    routers = json_data["routers"]
    routes = json_data["src-dest"]

    find_routes(routers, routes)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
    
