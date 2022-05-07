import asyncio as asy
from email import message
import socket

from zmq import Socket
from  util import RequestJsonAdapter as rja
from util import REQUEST_RESPONSE_DICT
from util import SensorTypeMissmatchException


class Phone():

    def __init__(self) -> None:
        self.sock = socket.socket(socket.AF_INET, # Internet
                                socket.SOCK_DGRAM) # UDP
        self.sock.settimeout(1)
        self.udp_ip="127.0.0.1"
        self.udp_sender_port = 5006
        self.udp_listener_port = 5005
        self.sock.bind((self.udp_ip, self.udp_listener_port))



    def write_text(self, text):

        async def _write_text(self, text : str) -> None:
            """can be called with various text to display on the smartphone display"""
            rpc_message = rja.get_rpc_request(command="textview", value=text)
            self._sendMessage(message=rpc_message)

        asy.run(_write_text, text)

    def get_sensor(self, sensor_name):
        sensor_message = rja.get_sensor_request(sensor_name)
        self._sendMessage(message=sensor_message)
        request= dict(sensor_message)
        result = self._wait_on_result(request=request)
        result_sensor_type=result["sensor_type"]
        request_sensor_type=request["sensor_type"]
        if result_sensor_type  == request_sensor_type:
            return result
        else:
            raise Exception(f"Sensortypes mismatch: wanted: {request_sensor_type}, got {result_sensor_type}")

    def 


    def _wait_on_result(self, request : dict) -> dict:
        """get's response blocking with socket timeout
        and checks if types match.
        """

        data = self.sock.recvfrom()[0]
        response = dict(data)

        
        request_type = request["type"]
        response_type= response["type"]


        if REQUEST_RESPONSE_DICT.check(request_type, response_type):
            return response



        
        

    def _sendMessage(self, message):
        self.sock.sendto(bytes(message, 'UTF-8'), (self.udp_ip, self.udp_sender_port))
