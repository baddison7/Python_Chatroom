import socket, time, threading

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = '10.1.148.22'
        self.port = 5555
        self.addr = (self.server, self.port)
        self.name = 'XXX'  # Default name
        self.running = True  # Flag to control receiving
        self.connect()

    def connect(self):
        self.name = input("Enter your name: ")
        try:
            self.client.connect(self.addr)
        except Exception as e:
            print(f"Connection error: {e}")

    def get_timestamp(self):
        return time.strftime("%H:%M", time.localtime())

    def message(self, string):
        timestamp = self.get_timestamp()
        message = f"{self.name} {timestamp}: {string}"
        self.client.send(str.encode(message))

    def send(self):
        try:
            while True:
                string = input("")
                self.message(string)
                if string.lower() == '/exit':
                    self.running = False  # Tell receive() to stop
                    break

        except socket.error as e:
            print(f"Socket error: {e}")
        finally:
            self.client.close()  # Close the socket here

    def receive(self):
        try:
            while self.running:
                response = self.client.recv(2048).decode()
                if not response:
                    break
                print(response)
        except OSError as e:  # Handle bad file descriptor error
            if self.running:  # Only print the error if we didn't intentionally close
                print(f"Socket error: {e}")
        finally:
            self.client.close()  # Ensure socket is closed

n = Network()

# Create threads for sending and receiving messages
send_thread = threading.Thread(target=n.send)
receive_thread = threading.Thread(target=n.receive)

# Start the threads
send_thread.start()
receive_thread.start()

# Wait for send_thread to finish before stopping receive()
send_thread.join()
n.running = False  # Ensure receive() stops
receive_thread.join()
