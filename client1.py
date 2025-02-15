from network import Network
import threading

n = Network()

send_thread = threading.Thread(target=n.send)
receive_thread = threading.Thread(target=n.receive)

send_thread.start()
receive_thread.start()

send_thread.join()
n.running = False
receive_thread.join()