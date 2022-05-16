"Middleware holding DataStructure, reacting to Requests via udp or mqtt"

import logging
import queue
import socket
import ssl
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
    def __init__(self, request_queue : queue.PriorityQueue,
        mqtt_sender_queue : queue.Queue):
        """
        Parameters:
        -----------
        request_queue : queue:Queue
        Stores general requests for data_structure or mqtt_requests.
        Filled by the requestss_queue_worker thread which listens to
        udp requests, or by the MqttHandlerThread which listens to
        mqtt_requests.

        mqtt_sender_queue : queue.Queue
        Stores requests that should be sent via mqtt to invoke commands on smartphone.
        """
        #request queue get's shared between mqqt handler thread and Request_queue_worker
        self.request_queue = request_queue
        self.answer_queue = queue.Queue()
        self.mqtt_sender_queue=mqtt_sender_queue
        self.data_structure = SensorDB()
        self.udp_ip="127.0.0.1"
        self.udp_listener_port = 5006
        self.udp_sender_port = 5005
        self.stop_handler_event = threading.Event()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        self.sock.settimeout(1)
        self.logger = logging.getLogger(str(type(self).__name__))


    def start_handler(self):
        "starts all threads of the handler"
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
            except (socket.timeout, ConnectionResetError):
                continue
            data_str = str(data[0].decode("UTF-8"))
            # self.logger.info("got udp request %s" % data_str)
            self.request_queue.put((2, data_str))

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
                request = self.request_queue.get(timeout=1)[1]
            except queue.Empty:
                continue
            # self.result_stats()
            if not request is None:
                request = json.loads(request)
                if request["type"] == "rpc_request":
                    self.logger.info("rpc request: %s" % str(request))
                    self.mqtt_sender_queue.put(request)
                elif request["type"] == "update_request":
                    sensor_key = request["sensor_type"]
                    value = request["sensor_value"]
                    self.data_structure.update(sensor_key, value)
                elif request["type"] == "sensor_request":
                    # self.logger.info("sensor request: %s" % request)
                    sensor_key = request["sensor_type"]
                    result = self.data_structure.get(sensor_key)
                    self.answer_queue.put(result)
                elif request["type"] == "rpc_response":
                    self.answer_queue.put(request["value"])
            else:
                continue


class MqttHandlerThread(threading.Thread):
    """Reacts on mqtt messages, puts them in request queue which isshared with handler thread
    """

    def __init__(self, mqqt_sender_queue : queue.Queue, request_queue):
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
        self.HOSTNAME = "pma.inftech.hs-mannheim.de"
        # self.HOSTNAME = "atborg"
        self.TOPIC= "22thesis01/test"
        self.QOSTOPIC = "22thesis01/test_qos"
        self.USERNAME = "22thesis01"
        self.PASSWORD = "n4xdnp36"
        self.PORT = 8883
        self.sender_queue=mqqt_sender_queue
        #queue get's shared with handler
        self.request_queue=request_queue
        self.stop_mqtt = threading.Event()
        self.logger = logging.getLogger(str(type(self).__name__))



    def on_message(self, client, userdata, message):
        "is called on every new mqtt message"
        try:
            msg = json.loads(message.payload.decode("utf-8"))
        except json.JSONDecodeError as json_exception:
            self.logger.warning("Json Exception" + str(json_exception))
            return
        self.logger.info("Got mqtt message: %s" % msg)

        if msg["type"] == "update_request" or msg["type"] == "rpc_response" :
            self.request_queue.put((1, message.payload.decode("utf-8")))

    def stop(self):
        "stop mqtt listener"
        self.stop_mqtt.set()

    def run(self):
        client = mqtt.Client("c1")
        client.on_message = self.on_message
        client.username_pw_set(self.USERNAME, self.PASSWORD)
        client.tls_set_context(ssl.create_default_context())
        client.tls_insecure_set(True)

        try:
            self.logger.info("trying to connect to mqtt server")
            client.connect(self.HOSTNAME, port=self.PORT)
            self.logger.info("connected to server %s" % self.HOSTNAME)
        except socket.timeout:
            self.logger.warning("no connection could be established")
            return
        client.subscribe(self.TOPIC)
        self.logger.info("mqtt subscribed to topic: %s" % self.TOPIC)
        client.subscribe(self.QOSTOPIC, qos=0)
        self.logger.info("mqtt subscribed to QOS-topic: %s" % self.QOSTOPIC)
        client.loop_start()
        while not self.stop_mqtt.is_set() or self.sender_queue.qsize() > 0:
            try:
                # nur auf dem topic mit hoher qos senden
                message = str(self.sender_queue.get(timeout=1))
                client.publish(topic=self.QOSTOPIC, payload=message, qos=2)
                self.logger.info("sent: %s" % message) 
            except queue.Empty:
                continue

            except TypeError as exception:
                self.logger.error(str(exception))
        client.loop_stop()
        self.logger.info("stopped loop")



def main():
    "main"
    logging.basicConfig(level=logging.INFO)
    # receiver_queue = queue.Queue(maxsize=100)
    # request_queue = queue.Queue(maxsize=100)

    request_queue = queue.PriorityQueue(maxsize=10)
    mqtt_sender_queue = queue.Queue(maxsize=100)

    data_handler = DataHandler(request_queue=request_queue, mqtt_sender_queue=mqtt_sender_queue)
    mqtt_handler_thread = MqttHandlerThread(mqqt_sender_queue=mqtt_sender_queue,
     request_queue=request_queue)

    try:
        mqtt_handler_thread.start()
        data_handler.start_handler()
    except KeyboardInterrupt:
        data_handler.stop_handler()
        mqtt_handler_thread.stop()


if __name__ == '__main__':
    main()