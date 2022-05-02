"Client Test simulates C-Library"

import logging
import threading
import socket
import queue
from time import sleep
from request_json_adapter import RequestJsonAdapter



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
        "start client"
        self.listener_thread.start()
        self.sender_thread.start()
        # a = True
        # for _ in range(100000):
        #     request = RequestJsonAdapter.get_rpc_request(command="button", value=str(a).lower())
        #     a = not a
        #     self.sender_queue.put(request)
        # self.stop()
        while True:
        #     # val = random.randint(1, 10)
        #     # request_1 = RequestJsonAdapter.get_update_request(sensor_type="accell_x",
        #     #      value=str(val))
        #     # if(command.startswith("accel_set")):
        #     #     request = RequestJsonAdapter.get_update_request("accell_x", "10")
        #     # elif(command.startswith("accell_get")):
        #     #     request = RequestJsonAdapter.get_sensor_request("accell_x")
        #     # self.sender_queue.put(request_1)
            request_2 = RequestJsonAdapter.get_sensor_request(sensor_type="accell_x")
            # logging.info("putting request in queue: %s" % request_2)
            self.sender_queue.put(request_2)
            sleep(1)


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
            if data_str.startswith("server"):
                data_str = data_str.split(":")[1]
            logging.info("Got answer from server %s" % data_str)
            # if(abs(float(data_str)) > 3.0):
                # logging.info("device was shaken")

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
