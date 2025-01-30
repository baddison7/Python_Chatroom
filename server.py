import socket, threading
from _thread import *
from chatRoom.chatRoomIP import currentIP, port_number

# Server configuration
server = currentIP.currentIP
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
        conn.send(str.encode("Welcome to the chat server! Waiting for chat to start...\n"))
        with lock:
            clients.append(conn)

        try:
            while True:
                data = conn.recv(2048)
                if not data:
                    break

                message = data.decode("utf-8").strip()

                if message.lower() == "exit":
                    conn.send(str.encode("Goodbye!"))
                    break

                if not chat_started:
                    conn.send(str.encode("Chat has not started yet. Please wait.\n"))
                else:
                    broadcast(message, conn)

        except Exception as e:
            print(f"Error handling client {addr}: {e}")

        finally:
            with lock:
                clients.remove(conn)
            conn.close()
            print(f"Disconnected from {addr}")


def admin_commands():
    global chat_started
    global s  # Use the global socket object to close it

    while True:
        command = input("Enter server command (/start, /end, /quit): \n").strip().lower()

        if command == "/start":
            chat_started = True
            print("Chat started!")
            broadcast("Chat has been started by the admin.\n")
        elif command == "/end":
            chat_started = False
            print("Chat ended!")
            broadcast("Chat has been ended by the admin.\n")
        elif command == "/quit":
            print("Shutting down the server...")
            broadcast("Server is shutting down. Goodbye!")
            with lock:
                for client in clients:
                    client.close()  # Close all client connections
                clients.clear()
            s.close()  # Close the server socket
            break  # Exit the admin_commands loop to stop the thread
        else:
            print("Invalid command!")


try:
    while True:
        conn, addr = s.accept()
        print(f"New connection: {addr}")
        start_new_thread(start_client, (conn, addr))
except Exception as e:
    print(f"Server error: {e}")
finally:
    s.close()

