import socket, time, threading, RSA, json

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = '10.1.148.22'
        self.port = 5555
        self.addr = (self.server, self.port)
        self.name = 'XXX'
        self.running = True
        self.public_key, self.private_key = RSA.generate_keys()
        self.server_public_key = None
        self.connect()

    def connect(self):
        self.name = input("Enter your name: ")
        try:
            self.client.connect(self.addr)

            # Receive server public key
            server_key = self.client.recv(4096).decode()
            e, n = map(int, server_key.split(","))
            self.server_public_key = (e, n)

            # Send client public key
            self.client.send(f"{self.public_key[0]},{self.public_key[1]}".encode())

        except Exception as e:
            print(f"Connection error: {e}")

    def get_timestamp(self):
        return time.strftime("%H:%M", time.localtime())

    def message(self, string):
        timestamp = self.get_timestamp()
        message = f"{self.name} {timestamp}: {string}"

        # Encrypt message using the server's public key
        encrypted_message = RSA.encrypt(message, self.server_public_key)
        self.client.send(json.dumps(encrypted_message).encode())

    def send(self):
        try:
            while True:
                string = input("")
                self.message(string)
                if string.lower() == '/exit':
                    self.running = False
                    break
        except socket.error as e:
            print(f"Socket error: {e}")
        finally:
            self.client.close()

    def receive(self):
        try:
            while self.running:
                response = self.client.recv(4096).decode()
                if not response:
                    break

                # Decrypt received message
                encrypted_message = json.loads(response)
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
