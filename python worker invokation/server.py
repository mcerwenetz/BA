from socket import socket
import threading
from time import sleep
from typing import List


class Server:
    def __init__(self) -> None:
        self.keep_running = threading.Event()
        self.UDP_IP="127.0.0.1"
        self.UDP_LISTENER_PORT = 5006
        self.UDP_SENDER_PORT = 5005
        self.server_config={
            "ip":self.UDP_IP,
            "listener_port": self.UDP_LISTENER_PORT,
            "sender_port" : self.UDP_SENDER_PORT
        }

        self.req_queue=threading.Queue()
        self.res_queue=threading.Queue()

        self.listener_thread = self.Server_listener_thread()
        self.data_handler_thread = self.Data_handler_thread(req_queue=self.req_queue, res_queue=self.res_queue)
        self.mqtt_handler_thread = threading.Thread(target=self.mqtt_handler_thread)


    def start(self):
        self.keep_running.set()
        self.listener_thread.start()
        self.data_handler_thread.start()

    def stop(self):
        self.keep_running.clear()
        print("killing")
        self.listener_thread.join()
        self.data_handler_thread.join()


    class Server_listener_thread(threading.Thread):

        def __init__(self, req_queue : threading.Queue,
                res_queue : threading.Queue,
                keep_running : threading.Event,
                server_config : List[str]):

                self.req_queue = req_queue
                self.req_queue = res_queue
                self.keep_running = keep_running
                self.server_config=server_config
                

        
        def run(self):
            sock = socket.socket(socket.AF_INET, # Internet
                                    socket.SOCK_DGRAM) # UDP
            sock.bind((self.server_config["ip"], self.server_config["listener_port"]))
            while self.keep_running.is_set():
                data, addr = sock.recvfrom(1024)
                data_str = str(data.decode("UTF-8"))
                # get cached sensor_data
                if data_str.startswith("out"):
                    data_str = data_str.split(":")[1]
                    self.req_queue.put(data_str)
                    res = f"server:{str(self.res_queue.get(block=True, timeout=None))}"
                    sock.sendto(bytes(res, 'UTF-8'), (self.UDP_IP, self.UDP_SENDER_PORT))
                    break

    
    class Data_handler_thread(threading.Thread):
        
        def __init__(self, req_queue : threading.Queue,
            res_queue : threading.Queue):

            self.req_queue = req_queue
            self.req_queue = res_queue
            # Todo: Create Data Structure with all relevant sensor-data
            self.data_structure = None

        def run(self) -> None:
            pass
                

    def mqtt_handler_thread(self, topics):

        def on_message(client, userdata, message):
            req_queue.put(message.payload.decode("utf-8"))

        client = mqtt.Client("c1")
        client.on_message=on_message
        client.connect("test.mosquitto.org")
        client.loop_start()
        [client.subscribe(t) for t in topics]
        client.loop_stop()



def main():
    s = Server()
    s.start()


if __name__ == '__main__':
    main()