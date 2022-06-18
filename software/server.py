"Middleware holding DataStructure, reacting to Requests via udp or mqtt"

import logging
import queue
import socket
import ssl
import threading
import json
import paho.mqtt.client as mqtt

with open("config.json", "r", encoding="utf-8") as fp:
    _CONFIG : dict = json.load(fp)

with open("protocol.json", "r", encoding="utf-8") as fp:
    _PROTOCOL : dict = json.load(fp)

class SensorNotSupportedException(Exception):
    def __init__(self, sensor_name) -> None:
        cause = "Sensor %s not supported" % sensor_name
        super().__init__(cause)

class CommandNotSupportedException(Exception):
    def __init__(self, command) -> None:
        cause = "Command %s not supported" % command
        super().__init__(cause)

def get_config_parameter(parameter_key : str ,
    config_dictionary : dict = _PROTOCOL):
    """recursivly searches configuration dictionary

    Args:
        parameter_key : str \\
        Parameterkeyword to access tict

        config_dictionary : dict \\
        Dictionary to look into recursivly.
        Gets called with default global _CONFIG Dictionary of Module.
        Can be subsituted with every dictionary to recursivly search key.

    Returns:
        str or dict depending of the value for key or 
        None if key is not in config_dictionary.\\
        if parameter_key is found multiple times only 
        the first occurence is returned

    use best to access constant configuration parameters like sensors or network ports

    raises exception if parameter_key is not found
    """

    for key, value in config_dictionary.items():
        if isinstance(value, dict):
            if key == parameter_key:
                return value
            ret = get_config_parameter(parameter_key, value)
            if ret != None:
                return ret
        elif isinstance(value, str):
            if key == parameter_key:
                return value


class MessageTypes():
    UPDATE_REQUEST = get_config_parameter("update_request")["type"]
    SENSOR_REQUEST = get_config_parameter("sensor_request")["type"]
    SENSOR_RESPONSE = get_config_parameter("sensor_response")["type"]
    RPC_REQUEST = get_config_parameter("rpc_request")["type"]
    RPC_RESPONSE = get_config_parameter("rpc_response")["type"]



class JsonMessagesWrapper():
    """This Class provides static methods to convert function calls to json"""

    @staticmethod
    def get_sensor_response(sensor_type, value):
        "get the value of a sensor"
        message : dict = get_config_parameter("sensor_response")
        message["sensor_type"] = sensor_type
        message["value"] = value
        return message

    @staticmethod
    def get_sensor_request(sensor_type) -> str:
        "get the value of a sensor"
        message : dict = get_config_parameter("sensor_request")
        message["sensor_type"] = sensor_type
        message = json.dumps(message)
        return message

    @staticmethod
    def get_rpc_request(command :str, value : str) ->str:
        """
        start an rpc on the smartphone
        raises: Exception if command is not found
        """
        command = get_config_parameter(command)
        if command == None:
            raise CommandNotSupportedException(command)
        message : dict = get_config_parameter("rpc_request")
        message["command"] = command
        message["value"] = value
        message = json.dumps(message)
        return message

    @staticmethod
    def get_rpc_response(command :str, value : str):
        """
        answers an rpc request
        raises: Exception if command is not found
        """
        command = get_config_parameter(command)
        if command == None:
            raise CommandNotSupportedException(command)
        message : dict = get_config_parameter("rpc_request")
        message["command"] = command
        message["value"] = value
        return message



class ReadOnlyDict(dict):
    def __init__(self) -> None:
        super().__init__()

    def __getitem__(self, __k):
        if __k in self:
            return super().__getitem__(__k)

    def __setitem__(self, __k, __v) -> None:
        pass

    def __internal__setitem__(self, __k, __v) -> None:
        return super().__setitem__(__k, __v)


class _RequestResponseDict(ReadOnlyDict):
    """constant dictionary which checks if key exists if accessed and does not throw an error
    if key is not inside.
    Also provides a check function to check if a request fits the received response
    """

    def __init__(self) -> None:
        super().__init__()
        dictionary = {
            "sensor_request":"sensor_response"
        }

        for k,v in dictionary.items():
            self.__internal__setitem__(k,v)

    def check(self, request, response):
        """
        returns false if the request does not match the response
        or if request is not in dictionary
        """
        return self[request] == response



REQUEST_RESPONSE_DICT = _RequestResponseDict()



class SensorDB():
    "data structure to hold sensor_data"
    def __init__(self) -> None:

        all_sensors = get_config_parameter("sensors")
        self.sensor_vals = {}

        for sensor_val in all_sensors.values():
            self.sensor_vals[sensor_val] = "5"

        self.lock = threading.Lock()

    def get(self, sensor_name):
        "gets value from internal db"
        if get_config_parameter(sensor_name) == None:
            raise SensorNotSupportedException(sensor_name)
        with self.lock:
            return self.sensor_vals[sensor_name]

    def update(self, sensor_name, value):
        "updates value from db"
        if get_config_parameter(sensor_name) == None:
            raise SensorNotSupportedException(sensor_name)
        with self.lock:
            self.sensor_vals[sensor_name]=value


class DataHandler():
    "Container for worker and handler threads"
    def __init__(self,
            udp_request_queue : queue.PriorityQueue,
            mqtt_request_queue : queue.Queue,
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
        self.udp_request_queue = udp_request_queue
        self.mqtt_request_queue = mqtt_request_queue
        self.answer_queue = queue.Queue()
        self.mqtt_sender_queue=mqtt_sender_queue
        self.data_structure = SensorDB()
        self.udp_ip=get_config_parameter("udp_ip", _CONFIG)
        network_config = get_config_parameter("middleware", _CONFIG)
        self.udp_listener_port = network_config["listener_port"]
        self.udp_sender_port = network_config["sender_port"]
        self.stop_handler_event = threading.Event()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        self.sock.settimeout(1)
        self.json_message_wrapper = JsonMessagesWrapper()
        self.logger = logging.getLogger(str(type(self).__name__))


    def start_handler(self):
        "starts all threads of the handler"
        threading.Thread(target=self.udp_requests_queue_worker).start()
        threading.Thread(target=self.answer_queue_worker).start()
        threading.Thread(target=self.mqtt_request_handler).start()
        threading.Thread(target=self.udp_request_handler).start()


    def stop_handler(self):
        "stop all handler and worker threads"
        self.stop_handler_event.set()


    def udp_requests_queue_worker(self):
        "handles mqtt and udp requests and puts it in a general request queue"
        # self.sock.bind(self.UDP_IP, self.UDP_LISTENER_PORT)
        self.sock.bind((self.udp_ip, self.udp_listener_port))

        while not self.stop_handler_event.is_set():
            try:
                data = self.sock.recvfrom(1024)
            except (socket.timeout, ConnectionResetError) as e:
                continue
            data_str = str(data[0].decode("UTF-8"))
            # self.logger.info("got udp request %s" % data_str)
            self.udp_request_queue.put((2, data_str))

    def answer_queue_worker(self):
        "sends back answers from the answer queue if there are any"
        while not self.stop_handler_event.is_set():
            try:
                res = str(self.answer_queue.get(timeout=1))
            except queue.Empty:
                continue
            self.sock.sendto(bytes(res, 'UTF-8'),
            (self.udp_ip, self.udp_sender_port))


    def udp_request_handler(self):
        while not self.stop_handler_event.is_set():
            try:
                request = self.udp_request_queue.get(timeout=1)[1]
            except queue.Empty:
                continue
            # self.result_stats()
            if not request is None:
                try:
                    request = json.loads(request)
                except json.JSONDecodeError:
                    self.logger.exception("Could not decode request: %s" % request)
                    break
                request_type = request["type"]
                if request_type == MessageTypes.RPC_REQUEST:
                    self.logger.info("rpc request: %s" % str(request))
                    self.mqtt_sender_queue.put(json.dumps(request))
                elif request_type == MessageTypes.SENSOR_REQUEST:
                    # self.logger.info("sensor request: %s" % request)
                    sensor_key = request["sensor_type"]
                    result = self.data_structure.get(sensor_key)
                    result = self.json_message_wrapper.get_sensor_response(sensor_type=request["sensor_type"], value=result)
                    result = json.dumps(result)
                    self.answer_queue.put(result)
                    # self.logger.info(result)
            else:
                continue

    def mqtt_request_handler(self):
        """decides weather to get answer for request from database and put it in answer queue
        or to put request in mqtt message answer queue"""
        while not self.stop_handler_event.is_set():
            try:
                request = self.mqtt_request_queue.get(timeout=1)[1]
            except queue.Empty:
                continue
            # self.result_stats()
            if not request is None:
                request = json.loads(request)
                request_type = request["type"]
                if request_type == MessageTypes.UPDATE_REQUEST:
                    sensor_key = request["sensor_type"]
                    value = request["sensor_value"]
                    self.data_structure.update(sensor_key, value)
                elif request_type == MessageTypes.RPC_RESPONSE:
                    self.answer_queue.put(json.dumps(request))
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
        mqtt_config = get_config_parameter("mqtt", _CONFIG)
        self.HOSTNAME = mqtt_config["network"]["hostname"]
        self.PORT =  mqtt_config["network"]["port"]
        self.TOPIC= mqtt_config["topics"]["normal"]
        self.USERNAME =  mqtt_config["credentials"]["username"]
        self.PASSWORD =  mqtt_config["credentials"]["password"]
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
        # self.logger.info("Got mqtt message: %s" % msg)

        if msg["type"] == "update_request":
            self.request_queue.put((1, message.payload.decode("utf-8")))
        if msg["type"] == "rpc_response":
            self.request_queue.put((1, message.payload.decode("utf-8")))

    def stop(self):
        "stop mqtt listener"
        self.stop_mqtt.set()

    def run(self):
        client = mqtt.Client("middleware")
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
        client.loop_start()
        while not self.stop_mqtt.is_set() or self.sender_queue.qsize() > 0:
            try:
                # nur auf dem topic mit hoher qos senden
                message = str(self.sender_queue.get(timeout=1))
                client.publish(topic=self.TOPIC, payload=message) 
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

    udp_request_queue = queue.Queue()
    mqtt_request_queue = queue.Queue()
    mqtt_sender_queue = queue.Queue()

    data_handler = DataHandler(udp_request_queue=udp_request_queue,
        mqtt_request_queue=mqtt_request_queue,
        mqtt_sender_queue=mqtt_sender_queue)
    mqtt_handler_thread = MqttHandlerThread(
        mqqt_sender_queue=mqtt_sender_queue,
        request_queue=mqtt_request_queue)

    try:
        mqtt_handler_thread.start()
        data_handler.start_handler()
    except KeyboardInterrupt:
        data_handler.stop_handler()
        mqtt_handler_thread.stop()


if __name__ == '__main__':
    main()
