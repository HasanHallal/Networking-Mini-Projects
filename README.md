# Networking Mini-Projects

A collection of hands-on Python networking projects built while studying
[Beej's Guide to Network Concepts](https://beej.us/guide/bgnet/). The repository
progresses from socket fundamentals to application-layer protocols, packet
validation, routing algorithms, I/O multiplexing, and multi-client systems.

These projects are intentionally small and focused. Each one isolates a core
networking concept so the protocol behavior remains easy to inspect, run, and
experiment with.

## Skills demonstrated

| Project | Concepts demonstrated |
| --- | --- |
| [Basic web server and client](#basic-web-server-and-client) | TCP sockets, HTTP request/response structure, byte encoding, connection lifecycle |
| [File-serving web server](#file-serving-web-server) | HTTP parsing, status codes, MIME types, binary file transfer |
| [Atomic clock client](#atomic-clock-client) | RFC 868 time protocol, binary integers, epoch conversion |
| [Word protocol](#word-protocol) | Application-layer protocol design, length-prefixed messages, TCP stream framing |
| [TCP checksum validation](#tcp-checksum-validation) | TCP pseudo-header construction, one's-complement checksums, packet integrity |
| [IPv4 subnet computation](#ipv4-subnet-computation) | IPv4 integer representation, CIDR masks, network identification, router mapping |
| [Dijkstra routing](#dijkstra-routing) | Weighted graphs, shortest-path routing, administrative distance |
| [Packet Tracer topology](#packet-tracer-topology) | Multi-router network design and end-to-end connectivity |
| [`select()` server](#select-server) | I/O multiplexing, concurrent connections, socket readiness |
| [Multi-client chat](#multi-client-chat) | Length-prefixed JSON, per-client buffers, event broadcasting, concurrent terminal I/O |

## Requirements

- Python 3.12 or newer
- No third-party Python packages for the primary project implementations
- Cisco Packet Tracer only for `final_test.pkt`
- Local TCP ports available for the client/server exercises

Clone the repository and enter its directory:

```bash
git clone https://github.com/HasanHallal/Networking-Mini-projects.git
cd Networking-Mini-projects
```

Run each command from the project directory shown below. Open separate terminal
windows when a server and one or more clients need to run at the same time.

> [!NOTE]
> The servers are educational implementations, not production services. Run
> them on a trusted local network and stop them with `Ctrl+C` when finished.
> They focus on protocol mechanics and intentionally omit safeguards such as
> TLS, authentication, comprehensive input validation, and access controls.

## Projects

### Basic web server and client

**Directory:** [`Webserver & webclient`](./Webserver%20%26%20webclient/)

Introduces the complete lifecycle of a TCP connection. The client sends a
minimal HTTP/1.1 request, the server reads through the end of the headers, and
returns a plain-text response before closing the connection.

```bash
cd "Webserver & webclient"
python webserver.py
```

In a second terminal, from the same directory:

```bash
python webclient.py
```

Both programs use `localhost:28333` by default.

### File-serving web server

**Directory:** [`A_Better_Web_Server`](./A_Better_Web_Server/)

Extends the basic server by parsing the HTTP request line, reading files as
bytes, selecting a MIME type from the file extension, calculating
`Content-Length`, and returning `400`, `404`, or `200` responses. The included
text and HTML files provide simple test resources.

```bash
cd A_Better_Web_Server
python webserver.py 28333
```

Then request a sample file with a browser or another HTTP client:

```text
http://127.0.0.1:28333/file2.html
```

If the port argument is omitted, the server defaults to port `28333`.

### Atomic clock client

**Directory:** [`Atomic_Clock`](./Atomic_Clock/)

Connects to the NIST time service over TCP port 37, decodes its four-byte
big-endian timestamp, and compares it with the local system time converted from
the Unix epoch (1970) to the RFC 868 epoch (1900).

```bash
cd Atomic_Clock
python Atomic_Time.py
```

This project requires outbound network access to `time.nist.gov:37`. Some
networks and firewalls block the legacy time protocol.

### Word protocol

**Directory:** [`The_Word_Server`](./The_Word_Server/)

Implements a small application-layer protocol over TCP. Each UTF-8 word is
preceded by a two-byte big-endian length field. The client maintains a receive
buffer so it can reconstruct messages correctly even when TCP combines or
splits data across `recv()` calls.

Start the server:

```bash
cd The_Word_Server
python wordserver.py 3490
```

In a second terminal:

```bash
cd The_Word_Server
python wordclient.py localhost 3490
```

### TCP checksum validation

**Directory:** [`Validating_A_TCP_Packet`](./Validating_A_TCP_Packet/)

Validates captured TCP segments by rebuilding the IPv4 pseudo-header, clearing
the stored checksum field, padding odd-length input, and calculating the
16-bit one's-complement checksum. This demonstrates what the TCP checksum
covers and how corrupted test data is detected.

```bash
cd Validating_A_TCP_Packet
python checksum.py
```

The bundled fixtures contain five valid segments followed by five invalid
segments, so the expected result is five `PASS!` lines and five `FAIL!` lines.

### IPv4 subnet computation

**Directory:** [`Computing_Subnets`](./Computing_Subnets/)

Converts dotted-decimal IPv4 addresses to 32-bit integer values, constructs
CIDR subnet masks, calculates network addresses, checks whether hosts share a
subnet, and maps hosts to their matching routers.

```bash
cd Computing_Subnets
python netfuncs.py example1.json
```

The generated report can be compared with `example1_output.txt`.

### Dijkstra routing

**Directory:** [`Dijkstra!`](./Dijkstra!/)

Models routers and their connections as a weighted graph, associates endpoint
IPs with their local routers, and uses Dijkstra's algorithm to find the
lowest-cost route based on administrative-distance values in the input data.

```bash
cd "Dijkstra!"
python dijkstra.py example1.json
```

The expected routes are recorded in `example1_output.txt`.

### Packet Tracer topology

**File:** [`final_test.pkt`](./final_test.pkt)

A Cisco Packet Tracer exercise that applies network configuration in a
multi-router topology. Open the file in Cisco Packet Tracer to inspect the
devices, addressing, router connections, and end-to-end connectivity.

### `select()` server

**Directory:** [`Select`](./Select/)

Demonstrates single-threaded concurrency with `select.select()`. One server
monitors the listening socket and all connected client sockets, accepting new
connections and processing whichever sockets are ready without blocking on a
single client.

Start the server:

```bash
cd Select
python select_server.py 3490
```

Run one or more clients in separate terminals, changing the label for each:

```bash
cd Select
python select_client.py alice localhost 3490
python select_client.py bob localhost 3490
```

Each client sends randomly generated messages at varying intervals so the
server's multiplexing behavior is visible.

### Multi-client chat

**Directory:** [`Multichat-Project`](./Multichat-Project/)

Combines the earlier concepts into a multi-client chat system. The server uses
`select()` to manage connected clients and keeps a separate receive buffer for
each socket. Messages are JSON documents framed with two-byte length prefixes.
The protocol supports `hello`, `chat`, `join`, and `leave` events, which the
server broadcasts to connected users. The client uses a background input
thread and a terminal UI that keeps incoming messages from overwriting the
active prompt.

Start the server:

```bash
cd Multichat-Project
python server.py 3490
```

Start clients in separate terminals:

```bash
cd Multichat-Project
python client.py alice 3490
python client.py bob 3490
```

Use a terminal with ANSI escape-sequence support for the intended client UI.

## Security and networking takeaways

- TCP delivers a byte stream, so application protocols must define and enforce
  their own message boundaries.
- Checksums detect accidental corruption; they do not provide authentication or
  protect against intentional modification.
- Network-facing programs must validate message lengths, request structure, and
  file paths before using untrusted input.
- Multiplexing allows one process to serve multiple connections, while
  per-connection state keeps partially received messages isolated.
- Small protocol implementations are useful for observing behavior that mature
  networking libraries normally abstract away.

## Learning reference

The exercises were created while working through
[Beej's Guide to Network Concepts](https://beej.us/guide/bgnet/), an accessible
introduction to networking fundamentals and socket programming.
