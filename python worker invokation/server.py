"Middleware holding DataStructure, reacting to Requests via udp or mqtt"

import queue
import socket
import threading
import json
import paho.mqtt.client as mqtt


class SensorDB():
    "data structure to hold sensor_data"
    def __init__(self) -> None:
        self.sensor_vals = {
            "accell_x":"0",
            "accell_y":"0",
            "accell_z":"0"
        }

        self.lock = threading.Lock()

    def get(self, key):
        "gets value from internal db"
        with self.lock:
            return self.sensor_vals[key]

    def update(self, key, value):
        "updates value from db"
        with self.lock:
            self.sensor_vals[key]=value


class DataHandler():
    "holds worker and handler threads"
    def __init__(self, req_queue, answer_queue, mqtt_sender_queue):
        #request queue get's shared between mqqt handler thread and Request_queue_worker
        self.request_queue = req_queue
        self.answer_queue = answer_queue
        self.mqtt_sender_queue=mqtt_sender_queue
        # Todo: Create Data Structure with all relevant sensor-data. Can be class too.
        self.data_structure = SensorDB()
        self.udp_ip="127.0.0.1"
        self.udp_listener_port = 5006
        self.udp_sender_port = 5005
        self.stop_handler_event = threading.Event()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP

        threading.Thread(target=self.requests_queue_worker).start()
        threading.Thread(target=self.answer_queue_worker).start()
        threading.Thread(target=self.request_handler).start()


    def stop_handler(self):
        "stop all handler and worker threads"
        self.stop_handler_event.set()


    def requests_queue_worker(self):
        "handles mqtt and udp requests and puts it in a general request queue"
        # self.sock.bind(self.UDP_IP, self.UDP_LISTENER_PORT)
        self.sock.bind((self.udp_ip, self.udp_listener_port))

        while not self.stop_handler_event.is_set():
            try:
                data = self.sock.recvfrom(1024)
            except KeyboardInterrupt:
                exit()
            data_str = str(data[0].decode("UTF-8"))
            self.request_queue.put(data_str)

    def answer_queue_worker(self):
        "sends back answers from the answer queue if there are any"
        while not self.stop_handler_event.is_set():
            try:
                res = str(self.answer_queue.get())
            except KeyboardInterrupt:
                exit()
            self.sock.sendto(bytes(res, 'UTF-8'),
                (self.udp_ip, self.udp_sender_port))

    def request_handler(self):
        """decides weather to get answer for request from database and put it in answer queue
        or to put request in mqtt message answer queue"""
        while not self.stop_handler_event.is_set():
            request = self.request_queue.get()
            request = json.loads(request)
            if request["type"] == "rpc":
                self.mqtt_sender_queue.put(request)
            elif request["type"] == "update_request":
                sensor_key = request["sensor_type"]
                value = request["sensor_value"]
                self.data_structure.update(sensor_key, value)
            #todo: responses auch als json. json adapter einführen?
            elif request["type"] == "sensor_request":
                sensor_key = request["sensor_type"]
                result = self.data_structure.get(sensor_key)
                self.answer_queue.put(result)
            elif request["type"] == "rpc_response":
                self.answer_queue.put(request["value"])

    # def request_handler(self):
    #     while not self.stop_handler_event.is_set():
    #         try:
    #             message = self.request_queue.get()
    #         except KeyboardInterrupt:
    #             exit()
    #         self.answer_queue.put(message)


class MqttHandlerThread(threading.Thread):
    "Reacts on mqtt messages, puts them in request queue which isshared with handler thread"

    def __init__(self, topic, sender_queue : queue.Queue, receiver_queue):
        super().__init__()
        self.HOSTNAME = "pma.inftech.hs-mannheim.de"
        self.TOPIC=topic
        self.USERNAME = "22thesis01"
        self.PASSWORD = "n4xdnp36"
        self.sender_queue=sender_queue
        #queue get's shared with handler
        self.receiver_queue=receiver_queue
        self.stop_mqtt = threading.Event()

    def on_message(self, message):
        "is called on every new mqtt message"
        msg = json.loads(message.payload.decode("utf-8"))
        if msg["type"] == "update_request" or msg["type"] == "rpc_response" :
            self.receiver_queue.put(message.payload.decode("utf-8"))

    def stop(self):
        "stop mqtt listener"
        self.stop_mqtt.set()

    def run(self):
        client = mqtt.Client("c1")
        client.on_message = self.on_message
        client.username_pw_set(self.USERNAME, self.PASSWORD)
        client.connect(self.HOSTNAME)
        client.subscribe(self.TOPIC)
        client.loop_start()
        while not self.stop_mqtt.is_set() and self.sender_queue.qsize() > 0:
            client.publish(self.sender_queue.get())
        client.loop_stop()



def main():
    "main"
    answer_queue = queue.Queue()
    request_queue = queue.Queue()
    mqtt_queue = queue.Queue()

    DataHandler(request_queue, answer_queue, mqtt_queue)

if __name__ == '__main__':
    main()
