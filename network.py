import socket, time, threading
from chatRoomIP import currentIP, port_number

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = currentIP
        self.port = port_number
        self.addr = (self.server, self.port)
        self.name = 'XXX'  # Default name
        self.connect()

    def connect(self):
        self.name = input("Enter your name: ")
        try:
            self.client.connect(self.addr)
            self.client.send(str.encode(self.name))


            # welcome_message = self.client.recv(2048).decode()
            # print(welcome_message)
            # anything that needs to be done for connection

        except Exception as e:
            print(f"Connection error: {e}")

    def get_timestamp(self):
        # Get the current timestamp in the format hh:mm
        return time.strftime("%H:%M", time.localtime())

    def message(self):
        string = input(f"")
        timestamp = self.get_timestamp()
        message = f"{self.name} {timestamp}: {string}"
        self.client.send(str.encode(message))



    def send(self):
        try:
            while True:
                string = input(f"")

                if string.lower()[0] == '/':
                    # print("Closing connection")
                    # self.client.send(str.encode(f"{self.name} is exiting"))
                    # exit protocal
                    break
                else:
                    self.message()

        except socket.error as e:
            print(f"Socket error: {e}")
        finally:
            self.client.close()

    def receive(self):
        try:
            while True:
                response = self.client.recv(2048).decode()
                if not response:
                    break
                print(response)
        except socket.error as e:
            print(f"Socket error: {e}")
        finally:
            self.client.close()

n = Network()

# Create threads for sending and receiving messages
send_thread = threading.Thread(target=n.send)
receive_thread = threading.Thread(target=n.receive)

# Start the threads
send_thread.start()
receive_thread.start()

# Wait for both threads to finish
send_thread.join()
receive_thread.join()
