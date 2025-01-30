import socket, threading
from _thread import *
from chatRoomIP import currentIP, port_number

# Server configuration
server = currentIP
port = port_number
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    s.bind((server, port))
except socket.error as e:
    print(f"Bind error: {e}")
    exit()

s.listen(10)

rooms = {}  # Dictionary of room_name -> {clients: [list of sockets]}
lock = threading.Lock()  # so two different threads dont try change the same thing

def broadcast(message, room_name, conn=None): # sends mesage to all clients in a room
    with lock:
        for client in rooms[room_name]["clients"]:
            if client != conn:
                try:
                    client.sendall(str.encode(message))
                except socket.error as e:
                    print(f"Error sending message to a client: {e}")


def client_thread(conn, addr):
    conn.send(str.encode("Welcome to the chat server!\n"))
    room_name = None

    try:
        while True:
            data = conn.recv(2048)
            if not data:
                break

            message = data.decode("utf-8").strip()

            if message.startswith("/rooms"):
                # Send a list of available rooms
                with lock:
                    room_list = "\n".join(rooms.keys()) if rooms else "No rooms available."
                conn.send(str.encode(room_list))

            elif message.startswith("/join "):
                # Join a specific room
                room_name = message.split("/join ", 1)[1].strip()
                with lock:
                    if room_name in rooms:
                        rooms[room_name]["clients"].append(conn)
                        conn.send(str.encode("OK"))
                        broadcast(f"{addr} has joined the room {room_name}.\n", room_name)
                    else:
                        conn.send(str.encode("Room does not exist.\n"))

            elif message.startswith("/leave"):
                # Leave the current room
                if room_name and room_name in rooms:
                    with lock:
                        rooms[room_name]["clients"].remove(conn)
                    broadcast(f"{addr} has left the room {room_name}.\n", room_name)
                    room_name = None
                conn.send(str.encode("You have left the room.\n"))

            elif message.lower() == "exit":
                conn.send(str.encode("Goodbye!"))
                break

            elif room_name:
                # Broadcast message to the room
                broadcast(message, room_name, conn)
            else:
                conn.send(str.encode("You are not in a room. Use /rooms to see available rooms or /join <room_name> to join one.\n"))

    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        if room_name and room_name in rooms:
            with lock:
                if conn in rooms[room_name]["clients"]:
                    rooms[room_name]["clients"].remove(conn)
        conn.close()
        print(f"Disconnected from {addr}")


def admin_commands():
    """Admin command interface for managing rooms."""
    global s  # Use the global socket object to close it

    while True:
        command = input("Enter server command (/create, /quit, /quit_all): \n").strip().lower()

        if command.startswith("/create "):
            room_name = command.split("/create ", 1)[1].strip()
            with lock:
                if room_name in rooms:
                    print(f"Room '{room_name}' already exists.")
                else:
                    rooms[room_name] = {"clients": []}
                    print(f"Room '{room_name}' has been created.")
        
        elif command == "/quit_all":
            with lock:
                for room_name in list(rooms.keys()):
                    for client in rooms[room_name]["clients"]:
                        client.send(str.encode("Server is shutting down. Goodbye!\n"))
                        client.close()
                    del rooms[room_name]
                print("All rooms have been closed.")
            s.close()
            break

        elif command.startswith("/quit"):
            room_name = command.split("/quit ", 1)[1].strip()
            with lock:
                if room_name in rooms:
                    for client in rooms[room_name]["clients"]:
                        client.send(str.encode(f"Room '{room_name}' has been closed by the admin.\n"))
                        client.close()
                    del rooms[room_name]
                    print(f"Room '{room_name}' has been closed.")
                else:
                    print(f"Room '{room_name}' does not exist.")

        else:
            print("Invalid command!")


start_new_thread(admin_commands, ())

try:
    while True:
        conn, addr = s.accept()
        start_new_thread(client_thread, (conn, addr))
except Exception as e:
    print(f"Server shutting down: {e}")
finally:
    s.close()
