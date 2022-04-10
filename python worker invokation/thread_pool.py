import multiprocessing
import socket
import paho.mqtt.client as mqtt
from time import sleep


def client_sender_thread():
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5006
    sock = socket.socket(socket.AF_INET, # Internet
                            socket.SOCK_DGRAM) # UDP
    MESSAGE = "client:gfsm"
    sleep(2)
    sock.sendto(bytes(MESSAGE, 'UTF-8'), (UDP_IP, UDP_PORT))

def client_listener_thread():
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5005
    sock = socket.socket(socket.AF_INET, # Internet
                            socket.SOCK_DGRAM) # UDP
    
    sock.bind((UDP_IP, UDP_PORT))
    
    while True:
        data, addr = sock.recvfrom(1024)
        data_str = str(data.decode("UTF-8"))
        if data_str.startswith("server"):
            #data_str = data_str.split(":")[1]
            print(f"got from server: {data_str}")

def server_listener_thread(req_queue : multiprocessing.Queue,
    res_queue : multiprocessing.Queue, ev : multiprocessing.Event):
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5006
    UDP_PORT_CLIENT = 5005

    
    sock = socket.socket(socket.AF_INET, # Internet
                            socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))
    while True:
        data, addr = sock.recvfrom(1024)
        data_str = str(data.decode("UTF-8"))
        if data_str.startswith("client"):
            data_str = data_str.split(":")[1]
            print(f"call is {data_str}")
            req_queue.put(data_str)
            sleep(1)
            while not ev.is_set() and res_queue.qsize() != 0:
                res = f"server:{str(res_queue.get(block=True, timeout=None))}"
                sock.sendto(bytes(res, 'UTF-8'), (UDP_IP, UDP_PORT_CLIENT))
                sleep(0.5)
            break

class Point():
    def __init__(self) -> None:
        self.x=12
        self.y=0


    

def data_server_thread(req_queue : multiprocessing.Queue,
    res_queue : multiprocessing.Queue, ev : multiprocessing.Event):

    def on_message(client, userdata, message):
        res_queue.put(message.payload.decode("utf-8"))

    p = Point()

    def getX():
        pass

    def gfsm():
        client = mqtt.Client("c1")
        TOPIC = "testblabla"
        client.on_message=on_message
        client.connect("test.mosquitto.org")
        client.loop_start()
        client.publish(TOPIC, "server:start")
        client.subscribe(TOPIC)
        sleep(10)
        client.publish(TOPIC, "server:stop")
        client.loop_stop()
        ev.set()

    while True:
        fun = req_queue.get()
        if fun == "getX":
            res = getX()
        elif fun == "gfsm":
            gfsm()


if __name__ == '__main__':
    res_queue = multiprocessing.Queue()
    req_queue = multiprocessing.Queue()
    ev = multiprocessing.Event()

    client_sender_t = multiprocessing.Process(target=client_sender_thread)
    client_listener_t = multiprocessing.Process(target=client_listener_thread)
    server_listener_t = multiprocessing.Process(target=server_listener_thread,
        args=(req_queue, res_queue, ev))
    data_server_t = multiprocessing.Process(target=data_server_thread,
        args = (req_queue, res_queue, ev))



    client_sender_t.start()
    client_listener_t.start()
    server_listener_t.start()
    data_server_t.start()