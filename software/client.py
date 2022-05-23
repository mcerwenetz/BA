"Client Test simulates C-Library"

import logging
import threading
import socket
import queue
from  util import JsonMessagesWrapper as rja



class Client():
    "client class holding workerthreads"

    def __init__(self) -> None:
        self.stop_client = threading.Event()
        self.udp_ip="127.0.0.1"
        self.udp_sender_port = 5006
        self.udp_listener_port = 5005

        self.sender_queue = queue.Queue()
        self.listener_thread = threading.Thread(target=self.client_listener_thread)
        self.sender_thread = threading.Thread(target=self.client_sender_thread,
             args=(self.sender_queue,))

    def start(self):
        "start client with threads"
        self.listener_thread.start()
        self.sender_thread.start()
        request = rja.get_rpc_request(command="checkbox", value="true")
        self.sender_queue.put(request)

    def stop(self):
        "stop client"
        self.stop_client.set()
        self.listener_thread.join()
        self.sender_thread.join()


    def client_sender_thread(self, sender_queue):
        "sends all request from queue via udp"
        sock = socket.socket(socket.AF_INET, # Internet
                                socket.SOCK_DGRAM) # UDP
        sock.settimeout(1)
        while not self.stop_client.is_set() or self.sender_queue.qsize() > 0:
            try:
                message = sender_queue.get(timeout=1)
            except queue.Empty:
                continue
            sock.sendto(bytes(message, 'UTF-8'), (self.udp_ip, self.udp_sender_port))
            # logging.info("sending request")


    def client_listener_thread(self):
        "get answers via udp, prints answer"
        sock = socket.socket(socket.AF_INET, # Internet
                                socket.SOCK_DGRAM) # UDP
        sock.settimeout(1)
        sock.bind((self.udp_ip, self.udp_listener_port))
        while not self.stop_client.is_set():
            try:
                data = sock.recvfrom(1024)[0]
            except socket.timeout:
                continue
            data_str = str(data.decode("UTF-8"))
            logging.info("Got answer from server %s" % data_str)
            
def main():
    "main"
    logging.basicConfig(level=logging.INFO)
    client = Client()
    try:
        client.start()
    except KeyboardInterrupt:
        client.stop()

if __name__ == '__main__':
    main()
