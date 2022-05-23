import json
import os.path

class RequestJsonAdapter():
    """This Class provides static methods to convert function calls to json"""
    def __init__(self, path_to_config) -> None:
        "creates JSON Adapter"

    @staticmethod
    def get_update_request(sensor_type,value):
        "update a sensor value"
        res ={
            "type":"update_request",
            "sensor_type":str(sensor_type),
            "sensor_value":str(value)
        }
        return json.dumps(res)

    @staticmethod
    def get_sensor_response(sensor_type, value):
        "get the value of a sensor"
        res = {
            "type":"sensor_response",
            "sensor_type": str(sensor_type),
            "value": str(value)
        }
        return json.dumps(res)

    @staticmethod
    def get_sensor_request(sensor_type):
        "get the value of a sensor"
        res = {
            "type":"sensor_request",
            "sensor_type": str(sensor_type)
        }
        return json.dumps(res)

    @staticmethod
    def get_rpc_request(command :str, value : str):
        "start an rpc on the smartphone"
        res = {
            "type":"rpc_request",
            "command": str(command),
            "value" : str(value)
        }
        return json.dumps(res)


    @staticmethod
    def get_rpc_response(command :str, value : str):
        "answers an rpc request"
        res ={
            "type":"rpc_response",
            "command": str(command),
            "value" : str(value)
        }
        return res


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
CONFIG = json.load("config.json")
