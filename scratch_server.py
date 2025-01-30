import socket
from _thread import *
from chatRoomIP import currentIP, port_number

server = currentIP
port = port_number

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow port reuse

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(10)
print("Waiting for a connection, Server Started")

# Client handler function
def client_thread(conn, addr):
    print("Connected to:", addr)
    conn.send(str.encode("Connected to server"))

    while True:
        try:
            data = conn.recv(2048)
            if not data:
                print(f"Disconnected from {addr}")
                break
            
            reply = data.decode("utf-8")
            print(f"Received: {reply}")
            conn.sendall(str.encode(f"Server received: {reply}"))
        except Exception as e:
            print(f"Error with {addr}: {e}")
            break

    conn.close()

# Accepting connections
while True:
    conn, addr = s.accept()
    start_new_thread(client_thread, (conn, addr))