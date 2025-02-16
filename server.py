import socket, threading, time, RSA, json, AES
from _thread import *

# Server configuration
server = "10.1.148.22"
port = 5555

# Create a socket (AF_INET for IPv4, SOCK_STREAM for TCP)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reusing the same address/port quickly

try:
    s.bind((server, port))  # Bind the socket to the server and port
except socket.error as e:
    exit()  # Exit if binding fails

s.listen(10)  # Start listening for up to 10 connections
lock = threading.Lock()  # Lock to prevent two threads from modifying the same thing
clients = {}  # Dictionary to store connected clients and their public keys
filename = f"log_{int(time.time())}.txt" # generate a log file with name as current time

# Generate RSA key pair for the server
public_key, private_key = RSA.generate_keys()
print("Waiting for connections...")

# Function to log messages to a file
def log_message(text):
    with open(filename, "a") as file:
        file.write(text + "\n")

# Broadcast a message to all clients except the sender
def broadcast(message, sender_addr=None):
    if message.lower() != "/exit":
        with lock:
            for addr, (conn, client_public_key) in list(clients.items()):
                if addr != sender_addr:
                    encrypted_message = RSA.encrypt(message, client_public_key)
                    try:
                        conn.sendall(json.dumps(encrypted_message).encode())  # Send encrypted message
                    except socket.error:
                        conn.close()
                        with lock:
                            del clients[addr]

# Handle communication with a single client
def client_thread(conn, addr):
    print(f"Connected to: {addr}")
    conn.sendall(f"{public_key[0]},{public_key[1]}".encode())  # Send server public key

    data = conn.recv(4096).decode()  # Receive client public key
    if data:
        e, n = map(int, data.split(","))
        client_public_key = (e, n)
        with lock:
            clients[addr] = (conn, client_public_key)  # Store connection and public key

    try:
        while True:
            data = conn.recv(4096)  # Receive encrypted data from client
            if not data:
                break

            encrypted_message = json.loads(data.decode("utf-8"))
            message = RSA.decrypt(encrypted_message, private_key)  # Decrypt message with server's private key
            log_message(message)  # Log the decrypted message

            if message.lower() == "/exit":
                break
            broadcast(message, addr)  # Send message to other clients
    finally:
        with lock:
            if addr in clients:
                del clients[addr]  # Remove client from list
        conn.close()  # Close the client socket
        print(f"Disconnected from {addr}")

# Function to handle server shutdown
def end_server():
    if input("").lower() == "/exit":
        with lock:
            for addr, (conn, _) in list(clients.items()):
                try:
                    conn.sendall("SERVER_SHUTDOWN".encode())  # Notify clients of shutdown
                    conn.close()
                except:
                    pass
            clients.clear()

        time.sleep(0.1)
        log_password = input("Enter log password: ")
        AES_key, salt = AES.generate_key(log_password)  # Generate AES key from password

        with open(filename, "r+") as file:
            content = file.read()
            encrypted_content = AES.encrypt_message(content, AES_key)
            file.seek(0)
            file.truncate()
            file.write(f"{salt.hex()}\n{encrypted_content}")  # Save encrypted log with salt

        s.close()  # Close the server socket
        print("Server shut down.")
        exit()

# Start the server shutdown thread
start_new_thread(end_server, ())

try:
    while True:
        conn, addr = s.accept()  # Accept incoming connection
        start_new_thread(client_thread, (conn, addr))  # Start a new thread for each client
except:
    pass
finally:
    s.close()  # Ensure the server socket is closed on exit
