import socket, threading
from _thread import *

server = '10.1.148.22'
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    s.bind((server, port))
except socket.error as e:
    print(f"Bind error: {e}")
    exit()

s.listen(10)
print("Waiting for connections...")

clients = []  # List of connected clients
lock = threading.Lock()  # For thread-safe access to shared resources

def broadcast(message, conn=None):
    with lock:  # Ensure thread-safe access to clients
        for client in clients:
            if client != conn:
                try:
                    client.sendall(str.encode(message))
                except socket.error as e:
                    print(f"Error sending message to a client: {e}")

class ChatRoom:
    def __init__(self, name):
        self.name = name
        self.clients = []
        self.lock = threading.Lock()

    def client_thread(conn, addr):
        print(f"Connected to: {addr}")
        with lock:
            clients.append(conn)
        try:
            while True:
                data = conn.recv(2048)
                if not data:
                    break
                message = data.decode("utf-8").strip()
                if message.lower() != "exit":
                    broadcast(message, conn)
                else:
                    break

        except Exception as e:
            print(f"Error handling client {addr}: {e}")

        finally:
            with lock:
                clients.remove(conn)
            conn.close()
            print(f"Disconnected from {addr}")

try:
    while True:
        conn, addr = s.accept()
        start_new_thread(ChatRoom.client_thread, (conn, addr))
except Exception as e:
    print(f"Server error: {e}")
finally:
    s.close()

