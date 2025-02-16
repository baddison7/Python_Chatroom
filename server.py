import socket, threading, time, RSA, json, AES
from _thread import *

server = '192.168.1.22'
port = 5555
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    s.bind((server, port))
except socket.error as e:
    # print(f"Bind error: {e}")
    exit()

s.listen(10)
lock = threading.Lock()
clients = {}
filename = f"log_{int(time.time())}.txt"
public_key, private_key = RSA.generate_keys()
print("Waiting for connections...")

def log_message(text):
    with open(filename, "a") as file:
        file.write(text + "\n")

def broadcast(message, sender_addr=None):
    if message.lower() != "/exit":
        with lock:
            for addr, (conn, client_public_key) in list(clients.items()):
                if addr != sender_addr:
                    encrypted_message = RSA.encrypt(message, client_public_key)
                    try:
                        conn.sendall(json.dumps(encrypted_message).encode())
                    except socket.error as e:
                        # print(f"Error sending message: {e}")
                        conn.close()
                        with lock:
                            del clients[addr]

def client_thread(conn, addr):
    print(f"Connected to: {addr}")
    conn.sendall(f"{public_key[0]},{public_key[1]}".encode())
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
            encrypted_message = json.loads(data.decode("utf-8"))
            message = RSA.decrypt  (encrypted_message, private_key)
            log_message(message)
            if message.lower() == "/exit":
                break
            broadcast(message, addr)
    except Exception as e:
        # print(f"Error handling client {addr}: {e}")
        pass
    finally:
        with lock:
            if addr in clients:
                del clients[addr]
        conn.close()
        print(f"Disconnected from {addr}")

def end_server():
    if input("").lower() == "/exit":
        with lock:
            for addr, (conn, _) in list(clients.items()):
                try:
                    conn.sendall("SERVER_SHUTDOWN".encode())  # Notify clients
                    conn.close()
                except:
                    pass
            clients.clear()
        time.sleep(0.1)
        log_password = input("Enter log password: ")
        AES_key, salt = AES.generate_key(log_password)
        with open(filename, "r+") as file:
            content = file.read()
            encrypted_content = AES.encrypt_message(content, AES_key)
            file.seek(0)
            file.truncate()
            file.write(f"{salt.hex()}\n{encrypted_content}")
        s.close()
        print("Server shut down.")
        exit()

start_new_thread(end_server, ())
try:
    while True:
        conn, addr = s.accept()
        start_new_thread(client_thread, (conn, addr))
except Exception as e:
    # print(f"Server error: {e}")
    pass
finally:
    s.close()
