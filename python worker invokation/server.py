"Middleware holding DataStructure, reacting to Requests via udp or mqtt"

import logging
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
    "Container for worker and handler threads"
    def __init__(self, request_queue : queue.Queue,
        receiver_queue: queue.Queue,
        mqtt_sender_queue : queue.Queue):
        """
        Parameters:
        -----------
        request_queue : queue:Queue
        Stores general requests for data_structure or mqtt_requests.
        Filled by the requestss_queue_worker thread which listens to
        udp requests, or by the MqttHandlerThread which listens to
        mqtt_requests.

        receiver_queue : queue.Queue
        Stores answers like sensor_requests or rpc_answers.
        Shared with MqttHandlerThread so answers can travel via MQTT.

        mqtt_sender_queue : queue.Queue
        Stores requests that should be sent via mqtt to invoke commands on smartphone.
        """
        #request queue get's shared between mqqt handler thread and Request_queue_worker
        self.request_queue = request_queue
        self.answer_queue = receiver_queue
        self.mqtt_sender_queue=mqtt_sender_queue
        self.data_structure = SensorDB()
        self.udp_ip="127.0.0.1"
        self.udp_listener_port = 5006
        self.udp_sender_port = 5005
        self.stop_handler_event = threading.Event()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        self.sock.settimeout(1)

    def start_handler(self):
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
            except socket.timeout:
                continue
            data_str = str(data[0].decode("UTF-8"))
            self.request_queue.put(data_str)

    def answer_queue_worker(self):
        "sends back answers from the answer queue if there are any"
        while not self.stop_handler_event.is_set():
            try:
                res = str(self.answer_queue.get(timeout=1))
            except queue.Empty:
                continue
            self.sock.sendto(bytes(res, 'UTF-8'),
            (self.udp_ip, self.udp_sender_port))

    def request_handler(self):
        """decides weather to get answer for request from database and put it in answer queue
        or to put request in mqtt message answer queue"""
        while not self.stop_handler_event.is_set():
            try:
                request = self.request_queue.get(timeout=1)
            except queue.Empty:
                continue
            if not request is None:
                request = json.loads(request)
                if request["type"] == "rpc":
                    self.mqtt_sender_queue.put(request)
                elif request["type"] == "update_request":
                    logging.info("got update-request: %s" % request)
                    sensor_key = request["sensor_type"]
                    value = request["sensor_value"]
                    self.data_structure.update(sensor_key, value)
                #todo: responses auch als json. json adapter einführen?
                elif request["type"] == "sensor_request":
                    logging.info("got sensor request via udp: %s " % request)
                    sensor_key = request["sensor_type"]
                    result = self.data_structure.get(sensor_key)
                    self.answer_queue.put(result)
                    logging.info("answer is: %s " % result )
                elif request["type"] == "rpc_response":
                    self.answer_queue.put(request["value"])
            else:
                continue


class MqttHandlerThread(threading.Thread):
    """Reacts on mqtt messages, puts them in request queue which isshared with handler thread
    """

    def __init__(self, mqqt_sender_queue : queue.Queue, receiver_queue):
        """

        Parameters:
        -----------
        mqqt_sender_queue : queue.Queue
            Queue in which requests are put that shall be executed on the smartphone.
            Shared with DataHandler so Client can make rpcs to smartphone.

        receiver_queue : queue.Queue
            Queue in which update and rpc_responses are put.
            Has to be the same queue as DataHandlers RequestQueue.
            Shared with DataHandler so client can receive answers via mqtt.
        """

        super().__init__()
        # self.HOSTNAME = "pma.inftech.hs-mannheim.de"
        self.HOSTNAME = "localhost"
        self.TOPIC= "test"
        self.USERNAME = "22thesis01"
        self.PASSWORD = "n4xdnp36"
        self.sender_queue=mqqt_sender_queue
        #queue get's shared with handler
        self.receiver_queue=receiver_queue
        self.stop_mqtt = threading.Event()

    def on_message(self, client, userdata, message):
        "is called on every new mqtt message"
        msg = json.loads(message.payload.decode("utf-8"))
        logging.info("Got mqtt message: %s" % msg)

        if msg["type"] == "update_request" or msg["type"] == "rpc_response" :
            self.receiver_queue.put(message.payload.decode("utf-8"))

    def stop(self):
        "stop mqtt listener"
        self.stop_mqtt.set()

    def run(self):
        client = mqtt.Client("c1")
        client.on_message = self.on_message
        # client.username_pw_set(self.USERNAME, self.PASSWORD)
        try:
            client.connect(self.HOSTNAME, port=1883)
            logging.info("connected to server %s" % self.HOSTNAME)
        except socket.timeout:
            logging.warn("mqtt: no connection could be established")
        client.subscribe(self.TOPIC)
        logging.info("mqtt subscribed to topic: %s" % self.TOPIC)
        client.loop_start()
        while not self.stop_mqtt.is_set() or self.sender_queue.qsize() > 0:
            try:
                client.publish(self.sender_queue.get(timeout=1))
            except queue.Empty:
                continue
        client.loop_stop()
        logging.info("mqtt: loop stopped")



def main():
    "main"
    logging.basicConfig(level=logging.INFO)
    receiver_queue = queue.Queue()
    request_queue = queue.Queue()
    mqtt_sender_queue = queue.Queue()

    data_handler = DataHandler(request_queue=request_queue, mqtt_sender_queue=mqtt_sender_queue, receiver_queue=receiver_queue )
    mqtt_handler_thread = MqttHandlerThread(mqqt_sender_queue=mqtt_sender_queue,
     receiver_queue=request_queue)

    try:
        mqtt_handler_thread.start()
        data_handler.start_handler()
    except KeyboardInterrupt:
        data_handler.stop_handler()
        mqtt_handler_thread.stop()


if __name__ == '__main__':
    main()
        
