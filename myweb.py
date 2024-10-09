## Copilot
# Sure! Here's a quick Python 3 script that listens on port 1026 for a web browser connection and then makes a reverse connection to the source IP on port 80 to check if it is a proxy:
# This is a quick non async test script to check if a proxy on port 80 is connecting to trio-ircproxy.py so the connection may be refused. This is to prevent proxy-to-proxy connections.

import socket

def listen_on_port(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(1)
    print(f"Listening on port {port}...")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")

        # Reverse connection to the source IP on port 80
        check_proxy(client_address[0])

        client_socket.close()

def check_proxy(ip):
    try:
        proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        proxy_socket.connect((ip, 80))
        proxy_socket.sendall(b"HEAD / HTTP/1.1\r\nHost: google.com\r\n\r\n")
        response = proxy_socket.recv(1024)
        proxy_socket.close()

        if b"HTTP" in response:
            print(f"{ip} is a proxy.")
        else:
            print(f"{ip} is not a proxy.")
    except Exception as e:
        print(f"Error connecting to {ip}: {e}")

if __name__ == "__main__":
    listen_on_port(1026)

# This script does the following:
# - Listens on port 1026 for incoming connections.
# - When a connection is received, it extracts the source IP address.
# - Makes a reverse connection to the source IP on port 80 and sends a simple HTTP request.
# - Checks the response to determine if the source IP is a proxy.# Please note that this is a basic example and may need further refinement for production use. If you have any questions or need further assistance, feel free to ask!
