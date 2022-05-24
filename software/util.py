"""This Modules provied auxillary tools for the server and python library"""

import json

with open("config.json", "r") as fp:
    _CONFIG : dict = json.load(fp)

def get_config_parameter(parameter_key : str ,
    config_dictionary : dict = _CONFIG):
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
    PROTOCOL_REQUEST = get_config_parameter("protocol_request")["type"]
    PROTOCOL_RESPONSE = get_config_parameter("protocol_response")["type"]



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
    def get_sensor_request(sensor_type):
        "get the value of a sensor"
        message : dict = get_config_parameter("sensor_request")
        message["sensor_type"] = sensor_type
        return message

    @staticmethod
    def get_rpc_request(command :str, value : str):
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
        
class SensorNotSupportedException(Exception):
    def __init__(self, sensor_name) -> None:
        cause = "Sensor %s not supported" % sensor_name
        super().__init__(cause)

class CommandNotSupportedException(Exception):
    def __init__(self, command) -> None:
        cause = "Command %s not supported" % command
        super().__init__(cause)


REQUEST_RESPONSE_DICT = _RequestResponseDict()
