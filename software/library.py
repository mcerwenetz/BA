"""This module provides the Python-Client Software to use the framework"""
import socket
import threading
import json

with open("protocol.json", "r", encoding="utf-8") as fp:
    _PROTOCOL : dict = json.load(fp)

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

class Phone():
    """This class provides all the functions to interact with the Phone"""
    def __init__(self) -> None:
        self.sock = socket.socket(socket.AF_INET, # Internet
                                socket.SOCK_DGRAM) # UDP
        self.sock.settimeout(1)
        self.udp_ip="127.0.0.1"
        self.udp_sender_port = 5006
        self.udp_listener_port = 5005
        self.sock.bind((self.udp_ip, self.udp_listener_port))



    def write_text(self, text_outer):

        def _write_text(self, text : str) -> None:
            """can be called with various text to display on the smartphone display"""
            rpc_message = JsonMessagesWrapper.get_rpc_request(command=get_config_parameter("write_text"), value=text)
            self._sendMessage(message=rpc_message)

        threading.Thread(target=_write_text, args=(self, text_outer)).start()

    def toggle_button(self):

        def _toogle_button(self) -> None:
            """this toggles the button in the interface"""
            rpc_message = JsonMessagesWrapper.get_rpc_request(command="button", value="")
            self._sendMessage(message=rpc_message)

        threading.Thread(target=_toogle_button, args=(self, )).start()

    def vibrate(self, time : str):
        "vibrates phone for time miliseconds"

        def _vibrate(self):
            rpc_message = JsonMessagesWrapper.get_rpc_request(command="vibrate", value=time)
            self._sendMessage(rpc_message)

        threading.Thread(target=_vibrate, args=(self, )).start()


    def get_x_accello(self):
        return self._get_sensor("accell_x")


    def _get_sensor(self, sensor_name):
        sensor_message = JsonMessagesWrapper.get_sensor_request(sensor_name)
        self._sendMessage(message=str(sensor_message))
        request= json.loads(sensor_message)
        result = self._wait_on_result(request=request)
        return result
        # result_sensor_type=result["sensor_type"]
        # request_sensor_type=request["sensor_type"]
        # if result_sensor_type  == request_sensor_type:
        #     return result
        # else:
        #     raise Exception(f"""Sensortypes mismatch: wanted: {request_sensor_type}, 
        #         got {result_sensor_type}""")


    def _wait_on_result(self, request : dict = None) -> dict:
        """get's response blocking with socket timeout
        and checks if types match.
        """
        try:
            data = str(self.sock.recvfrom(1024)[0], encoding="utf-8")
        except TimeoutError:
            print("Timeout was reached")
            return
        return data


    def _sendMessage(self, message):
        self.sock.sendto(bytes(message, 'UTF-8'), (self.udp_ip, self.udp_sender_port))
