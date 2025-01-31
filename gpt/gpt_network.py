import socket, threading, time
from gpt.chatRoomIP import currentIP, port_number

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = currentIP
        self.port = port_number
        self.addr = (self.server, self.port)
        self.name = input("Enter your name: ")
        self.room = None  # The room the user joins
        self.connect()

    def connect(self):
        try:
            self.client.connect(self.addr)
            welcome_message = self.client.recv(2048).decode()
            print(welcome_message)
            self.get_rooms()
        except Exception as e:
            print(f"Connection error: {e}")

    def get_rooms(self):
        try:
            self.client.send(str.encode("/rooms"))  # Request room list
            room_list = self.client.recv(2048).decode()
            print("Available Rooms:")
            print(room_list)
            self.room = input("Enter the name of the room you want to join: ").strip()
            self.client.send(str.encode(f"/join {self.room}"))
            response = self.client.recv(2048).decode()
            if response.lower() == "ok":
                print(f"Joined room: {self.room}")
            else:
                print(response)
                self.get_rooms()
        except Exception as e:
            print(f"Error fetching rooms: {e}")

    def get_timestamp(self):
        # Get the current timestamp in the format hh:mm
        current_time = time.localtime()
        return time.strftime("%H:%M", current_time)

    def send(self):
        try:
            while True:
                string = input(f"({self.room}) {self.name}: ")
                if string.lower() == "exit":
                    print("Leaving room")
                    self.client.send(str.encode(f"/leave {self.room}"))
                    break
                # Get the current timestamp
                timestamp = self.get_timestamp()
                # Prepend the timestamp and user's name to the message
                message = f"[{self.room}] {self.name} {timestamp}: {string}"
                self.client.send(str.encode(message))
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
