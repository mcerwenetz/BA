import queue
import socket
import threading
import json
import paho.mqtt.client as mqtt


class SensorDB():
    def __init__(self) -> None:
        self.sensor_vals = {
            "accel_x":0,
            "accell_y":0,
            "accell_z":0
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
   
    def __init__(self, req_queue, answer_queue, mqtt_sender_queue):
        #request queue get's shared between mqqt handler thread and Request_queue_worker
        self.request_queue = req_queue
        self.answer_queue = answer_queue
        self.mqtt_sender_queue=mqtt_sender_queue
        # Todo: Create Data Structure with all relevant sensor-data. Can be class too.
        self.data_structure = SensorDB()
        self.UDP_IP="127.0.0.1"
        self.UDP_LISTENER_PORT = 5006
        self.UDP_SENDER_PORT = 5005
        self.stop_handler = threading.Event()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP

        threading.Thread(target=self.requests_queue_worker).start()
        threading.Thread(target=self.answer_queue_worker).start()
        threading.Thread(target=self.request_handler).start()


    def requests_queue_worker(self):
        "handles mqtt and udp requests and puts it in a general request queue"
        self.sock.bind(self.UDP_IP, self.UDP_LISTENER_PORT)
        while not self.stop_handler.is_set():
            data = self.sock.recvfrom(1024)
            data_str = str(data.decode("UTF-8"))
            self.request_queue.put(data_str)

    def answer_queue_worker(self):
        "sends back answers from the answer queue if there are any"
        while not self.stop_handler.is_set():
            res = str(self.answer_queue.get())
            self.sock.sendto(bytes(res, 'UTF-8'),
                (self.UDP_IP, self.UDP_SENDER_PORT))

    def request_handler(self):
        """decides weather to get answer for request from database and put it in answer queue
        or to put request in mqtt message answer queue"""
        while not self.stop_handler.is_set():
            request = json.loads(self.request_queue.get())
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


class MqttHandlerThread(threading.Thread):

    def __init__(self, topic, sender_queue : queue.Queue, receiver_queue):
        super().__init__()
        self.topic=topic
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
        self.stop_mqtt.set()

    def run(self):
        client = mqtt.Client("c1")
        client.on_message = self.on_message
        client.connect("test.mosquitto.org")
        client.subscribe(self.topic)
        client.loop_start()
        while not self.stop_mqtt.is_set() and self.sender_queue.qsize() > 0:
            client.publish(self.sender_queue.get())
        client.loop_stop()



def main():
    pass


if __name__ == '__main__':
    main()
