import threading
import socket
from time import sleep


class Client():

    def __init__(self) -> None:
        self.keep_running = threading.Event()
        self.UDP_IP="127.0.0.1"
        self.UDP_SENDER_PORT = 5006
        self.UDP_LISTENER_PORT = 5005

        self.listener_thread = threading.Thread(target=self.client_listener_thread)
        self.sender_thread = threading.Thread(target=self.client_sender_thread)

    def start(self):
        self.keep_running.set()
        self.listener_thread.start()
        self.sender_thread.start()

    def stop(self):
        self.keep_running.clear()
        print("killing")
        self.listener_thread.join()
        self.sender_thread.join()

    def client_sender_thread(self):
        sock = socket.socket(socket.AF_INET, # Internet
                                socket.SOCK_DGRAM) # UDP
        MESSAGE = "client:gfsm"
        sleep(2)
        sock.sendto(bytes(MESSAGE, 'UTF-8'), (self.UDP_IP, self.UDP_SENDER_PORT))

    def client_listener_thread(self):
        sock = socket.socket(socket.AF_INET, # Internet
                                socket.SOCK_DGRAM) # UDP
        
        sock.bind((self.UDP_IP, self.UDP_LISTENER_PORT))
        
        while self.keep_running.is_set():
            data, addr = sock.recvfrom(1024)
            data_str = str(data.decode("UTF-8"))
            if data_str.startswith("server"):
                #data_str = data_str.split(":")[1]
                print(f"got from server: {data_str}")


def main():
    c = Client()
    c.start()


if __name__ == '__main__':
    main()