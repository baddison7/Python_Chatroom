import socket, time, threading, RSA, json

class Network:
    def __init__(self):
        # Initialize the client socket with IPv4 and TCP
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = input("Enter your local IP: ")  # Get the server IP from the user
        self.port = 5555  # Default port number
        self.addr = (self.server, self.port)  # Server address tuple
        self.name = ''  # Placeholder for client username
        self.running = True  # Control flag for running threads
        self.public_key, self.private_key = RSA.generate_keys()  # Generate RSA key pair
        self.server_public_key = None  # Placeholder for server's public key
        self.connect()  # Establish connection to the server

    def connect(self):
        # Ensure user provides a non-empty name
        while self.name == '':
            self.name = input("Enter your name: ")
        try:
            self.client.connect(self.addr)  # Connect to the server
            server_key = self.client.recv(4096).decode()  # Receive server's public key
            e, n = map(int, server_key.split(","))  # Parse the key components
            self.server_public_key = (e, n)  # Store server's public key
            self.client.send(f"{self.public_key[0]},{self.public_key[1]}".encode())  # Send client's public key to the server
        except Exception as e:
            print(f"Connection error: {e}")

    def get_timestamp(self):
        return time.strftime("%H:%M", time.localtime())  # Get current time in HH:MM format

    def message(self, string):
        timestamp = self.get_timestamp()  # Generate timestamp for the message
        message = f"{self.name} {timestamp}: {string}"  # Format message with name and timestamp
        encrypted_message = RSA.encrypt(message, self.server_public_key)  # Encrypt message using server's public key
        try:
            self.client.send(json.dumps(encrypted_message).encode())  # Send the encrypted message
        except Exception as e:
            print(f"Send error: {e}")
            self.running = False  # Stop client if sending fails

    def send(self):
        try:
            while self.running:
                string = input("")  # Get user input for the message
                if string != '':
                    self.message(string)  # Send message
                    if string.lower() == '/exit':  # If exit command, close connection
                        self.running = False
                        self.client.close()
                        break
        except socket.error as e:
            print(f"Socket error: {e}")

    def receive(self):
        try:
            while self.running:
                response = self.client.recv(4096).decode()  # Receive response from server
                if not response:
                    break
                if response == "SERVER_SHUTDOWN":  # Check for server shutdown signal
                    print("Server is shutting down.")
                    self.running = False
                    break
                encrypted_message = json.loads(response)  # Load encrypted message from JSON
                if isinstance(encrypted_message, list):  # Check if response is a valid encrypted message
                    message = RSA.decrypt(encrypted_message, self.private_key)  # Decrypt the message
                    print(message)
        except OSError as e:
            if self.running:
                print(f"Socket error: {e}")
        finally:
            self.client.close()  # Close the client socket

# Create network instance and start send/receive threads
n = Network()
send_thread = threading.Thread(target=n.send)
receive_thread = threading.Thread(target=n.receive)
send_thread.start()
receive_thread.start()
send_thread.join()
n.running = False
receive_thread.join()
