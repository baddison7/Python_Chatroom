import socket, time, threading, RSA, json

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = '192.168.1.22'
        self.port = 5555
        self.addr = (self.server, self.port)
        self.name = ''
        self.running = True
        self.public_key, self.private_key = RSA.generate_keys()
        self.server_public_key = None
        self.connect()

    def connect(self):
        while self.name == '':
            self.name = input("Enter your name: ")
        try:
            self.client.connect(self.addr)
            server_key = self.client.recv(4096).decode()
            e, n = map(int, server_key.split(","))
            self.server_public_key = (e, n)
            self.client.send(f"{self.public_key[0]},{self.public_key[1]}".encode())
        except Exception as e:
            print(f"Connection error: {e}")

    def get_timestamp(self):
        return time.strftime("%H:%M", time.localtime())

    def message(self, string):
        timestamp = self.get_timestamp()
        message = f"{self.name} {timestamp}: {string}"
        encrypted_message = RSA.encrypt(message, self.server_public_key)
        try:
            self.client.send(json.dumps(encrypted_message).encode())
        except Exception as e:
            print(f"Send error: {e}")
            self.running = False

    def send(self):
        try:
            while self.running:
                string = input("")
                if string != '':
                    self.message(string)
                    if string.lower() == '/exit':
                        self.running = False
                        self.client.close()
                        break
        except socket.error as e:
            print(f"Socket error: {e}")

    def receive(self):
        try:
            while self.running:
                response = self.client.recv(4096).decode()
                if not response:
                    break
                if response == "SERVER_SHUTDOWN":
                    print("Server is shutting down.")
                    self.running = False
                    break
                # Decrypt only if it's not the shutdown message
                encrypted_message = json.loads(response)
                if isinstance(encrypted_message, list):  # Ensure it's encrypted data
                    message = RSA.decrypt(encrypted_message, self.private_key)
                    print(message)
        except OSError as e:
            if self.running:
                print(f"Socket error: {e}")
        finally:
            self.client.close()

        

n = Network()
send_thread = threading.Thread(target=n.send)
receive_thread = threading.Thread(target=n.receive)
send_thread.start()
receive_thread.start()
send_thread.join()
n.running = False
receive_thread.join()
