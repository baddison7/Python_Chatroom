from network import Network
import threading
n = Network

# Create threads for sending and receiving messages
send_thread = threading.Thread(target=n.send)
receive_thread = threading.Thread(target=n.receive)

# Start the threads
send_thread.start()
receive_thread.start()

# Wait for both threads to finish
send_thread.join()
receive_thread.join()