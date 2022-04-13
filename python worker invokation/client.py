import threading
import socket
import queue
import json
import random
from time import sleep


class RequestJsonAdapter():

    def __init__(self) -> None:
        pass

    @staticmethod
    def get_update_request(sensor_type,value):
        res ={
            "type":"update_request",
            "sensor_type":str(sensor_type),
            "sensor_value":str(value)
        }
        return json.dumps(res)

    def get_sensor_request(sensor_type):
        res = {
            "type":"sensor_request",
            "sensor_type": str(sensor_type)
        }
        return json.dumps(res)


class Client():

    def __init__(self) -> None:
        self.keep_running = threading.Event()
        self.UDP_IP="127.0.0.1"
        self.UDP_SENDER_PORT = 5006
        self.UDP_LISTENER_PORT = 5005

        self.sender_queue = queue.Queue()
        self.listener_thread = threading.Thread(target=self.client_listener_thread)
        self.sender_thread = threading.Thread(target=self.client_sender_thread, args=(self.sender_queue,))

    def start(self):
        self.keep_running.set()
        self.listener_thread.start()
        self.sender_thread.start()
        while True:
            val = random.randint(1, 10)
            
            request_1 = RequestJsonAdapter.get_update_request(sensor_type="accell_x", value=str(val))
            
            # if(command.startswith("accel_set")):
            #     request = RequestJsonAdapter.get_update_request("accell_x", "10")
            # elif(command.startswith("accell_get")):
            #     request = RequestJsonAdapter.get_sensor_request("accell_x")
            self.sender_queue.put(request_1)
            
            request_2 = RequestJsonAdapter.get_sensor_request(sensor_type="accell_x")
            self.sender_queue.put(request_2)


    def stop(self):
        self.keep_running.clear()
        self.listener_thread.join()
        self.sender_thread.join()

    def client_sender_thread(self, queue):
        sock = socket.socket(socket.AF_INET, # Internet
                                socket.SOCK_DGRAM) # UDP
        while True:
            message = queue.get()
            sock.sendto(bytes(message, 'UTF-8'), (self.UDP_IP, self.UDP_SENDER_PORT))

    def client_listener_thread(self):
        sock = socket.socket(socket.AF_INET, # Internet
                                socket.SOCK_DGRAM) # UDP
        
        sock.bind((self.UDP_IP, self.UDP_LISTENER_PORT))
        
        while self.keep_running.is_set():
            data, addr = sock.recvfrom(1024)
            data_str = str(data.decode("UTF-8"))
            # if data_str.startswith("server"):
                #data_str = data_str.split(":")[1]
            print(f"got from server: {data_str}")

def main():
    client = Client()
    client.start()

if __name__ == '__main__':
    main()