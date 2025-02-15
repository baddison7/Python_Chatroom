import socket, threading, time, RSA, json, AES
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
lock = threading.Lock()
clients = {}  # Dictionary: addr -> (conn, client_public_key)
filename = f"log_{int(time.time())}.txt"

public_key, private_key = RSA.generate_keys()
print("Waiting for connections...")

def log_message(text):
    with open(filename, "a") as file:
        file.write(text + "\n")

def broadcast(message, sender_addr=None):
    with lock:
        for addr, (conn, client_public_key) in clients.items():
            if addr != sender_addr:
                encrypted_message = RSA.encrypt(message, client_public_key)
                try:
                    conn.sendall(json.dumps(encrypted_message).encode())
                except socket.error as e:
                    print(f"Error sending message: {e}")

def client_thread(conn, addr):
    print(f"Connected to: {addr}")

    # Send the server's public key
    conn.sendall(f"{public_key[0]},{public_key[1]}".encode())

    # Receive client's public key
    data = conn.recv(4096).decode()
    if data:
        e, n = map(int, data.split(","))
        client_public_key = (e, n)
        with lock:
            clients[addr] = (conn, client_public_key)

    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break

            # Convert JSON string back to list and decrypt
            encrypted_message = json.loads(data.decode("utf-8"))
            message = RSA.decrypt(encrypted_message, private_key)

            log_message(message)

            if message.lower() == "/exit":
                break
            broadcast(message, addr)

    except Exception as e:
        print(f"Error handling client {addr}: {e}")

    finally:
        with lock:
            del clients[addr]
        conn.close()
        print(f"Disconnected from {addr}")

def end_server():
    while True:
        if input("").lower() == "/exit":
            break
    # broadcast("/exit")
    log_password = input("enter log password: ")
    AES_key, salt = AES.generate_key(log_password)
    print(AES_key, salt)
    msg = AES.encrypt_message(filename, AES_key)
    with open(filename, "a") as file:
                file.seek(0)
                file.truncate()
                file.write(msg)

    s.close()
    exit()

try:
    while True:
        conn, addr = s.accept()
        start_new_thread(client_thread, (conn, addr))
        start_new_thread(end_server, ())
except Exception as e:
    print(f"Server error: {e}")
finally:
    s.close()