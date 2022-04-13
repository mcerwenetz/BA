"Client Test simulates C-Library"

import threading
import socket
import queue
import logging
from time import sleep
import request_json_adapter as ra




class Client():
    "client class holding workerthreads"

    def __init__(self) -> None:
        self.keep_running = threading.Event()
        self.udp_ip="127.0.0.1"
        self.udp_sender_port = 5006
        self.udp_listener_port = 5005
        self.logger = logging.getLogger()

        self.sender_queue = queue.Queue()
        self.listener_thread = threading.Thread(target=self.client_listener_thread)
        self.sender_thread = threading.Thread(target=self.client_sender_thread,
             args=(self.sender_queue,))

    def start(self):
        "start client"
        self.keep_running.set()
        self.listener_thread.start()
        self.sender_thread.start()
        while True:
            # val = random.randint(1, 10)
            # request_1 = RequestJsonAdapter.get_update_request(sensor_type="accell_x",
                #  value=str(val))
            # if(command.startswith("accel_set")):
            #     request = RequestJsonAdapter.get_update_request("accell_x", "10")
            # elif(command.startswith("accell_get")):
            #     request = RequestJsonAdapter.get_sensor_request("accell_x")
            # self.sender_queue.put(request_1)
            # sensorlist = ["accell_x", "accell_y", "accell_z"]
            sensorlist = ["accell_x"]
            for sensor in sensorlist:
                request = ra.RequestJsonAdapter.get_sensor_request(sensor_type=sensor)
                self.sender_queue.put(request)
            # sleep(0.1)


    def stop(self):
        "stop client"
        self.keep_running.clear()
        self.listener_thread.join()
        self.sender_thread.join()

    def client_sender_thread(self, sender_queue):
        "sends all request from queue via udp"
        sock = socket.socket(socket.AF_INET, # Internet
                                socket.SOCK_DGRAM) # UDP
        while True:
            message = sender_queue.get()
            sock.sendto(bytes(message, 'UTF-8'), (self.udp_ip, self.udp_sender_port))

    def client_listener_thread(self):
        "get answers via udp, prints answer"
        sock = socket.socket(socket.AF_INET, # Internet
                                socket.SOCK_DGRAM) # UDP
        sock.bind((self.udp_ip, self.udp_listener_port))
        while self.keep_running.is_set():
            data = sock.recvfrom(1024)
            data_str = str(data[0].decode("UTF-8"))
            # if data_str.startswith("server"):
                #data_str = data_str.split(":")[1]
            print(f"got from server: {data_str}")

def main():
    "main"
    client = Client()
    client.start()

if __name__ == '__main__':
    main()
