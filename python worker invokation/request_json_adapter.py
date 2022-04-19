import json

class RequestJsonAdapter():
    """This Class provides static methods to convert function calls to json"""
    def __init__(self) -> None:
        pass

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

    

