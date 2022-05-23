"""This Modules provied auxillary tools for the server and python library"""

from asyncio.windows_events import NULL
import json

from numpy import isin


with open("config.json", "r") as fp:
    _CONFIG : dict = json.load(fp)


class JsonMessagesWrapper():
    """This Class provides static methods to convert function calls to json"""


    @staticmethod
    def get_update_request(sensor_type,value):
        "update a sensor value"
        return _CONFIG["messages"]["update_request"]


    @staticmethod
    def get_sensor_response(sensor_type, value):
        "get the value of a sensor"
        return _CONFIG["messages"]["sensor_response"]

    @staticmethod
    def get_sensor_request(sensor_type):
        "get the value of a sensor"
        return _CONFIG["messages"]["sensor_request"]

    @staticmethod
    def get_rpc_request(command :str, value : str):
        "start an rpc on the smartphone"
        return _CONFIG["messages"]["rpc_request"]


    @staticmethod
    def get_rpc_response(command :str, value : str):
        "answers an rpc request"
        return _CONFIG["messages"]["rpc_response"]


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

def get_config_parameter(parameter_key : str , config_dictionary : dict = _CONFIG):
    """recursivly searches configuration dictionary

    Args:
        parameter_key : str \\
        Parameterkeyword to access tict

        config_dictionary : dict \\
        Dictionary to look into recursivly.
        Gets called with default global _CONFIG Dictionary of Module.
        Can be subsituted with every dictionary to recursivly search key.

    Returns:
        str or dict depending of the value for key

    Raises:
        Exception if key not in provided dictionary which is _CONFIG by default

    use best to access constant configuration parameters like sensors or network ports

    raises exception if parameter_key is not found
    """
    
    for key, value in config_dictionary.items():
        if isinstance(value, dict):
            ret = get_config_parameter(parameter_key, value)
            if ret != None:
                return ret
        elif isinstance(value, str):
            if key == parameter_key:
                return value


