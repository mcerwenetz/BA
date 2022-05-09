import socket
import threading
from  util import RequestJsonAdapter as rja
from util import REQUEST_RESPONSE_DICT


class Phone():

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
            rpc_message = rja.get_rpc_request(command="textview", value=text)
            self._sendMessage(message=rpc_message)

        threading.Thread(target=_write_text, args=(self, text_outer)).start()

    def toggle_button(self):

        def _toogle_button(self) -> None:
            """this toggles the button in the interface"""
            rpc_message = rja.get_rpc_request(command="button", value="")
            self._sendMessage(message=rpc_message)

        threading.Thread(target=_toogle_button, args=(self, )).start()

    def vibrate(self, time : str):
        "vibrates phone for time miliseconds"

        def _vibrate(self):
            rpc_message = rja.get_rpc_request(command="vibrate", value=time)
            self._sendMessage(rpc_message)

        threading.Thread(target=_vibrate, args=(self, )).start()


    def get_x_accello(self):
        self._get_sensor("accell_x")

    def _get_sensor(self, sensor_name):
        sensor_message = rja.get_sensor_request(sensor_name)
        self._sendMessage(message=sensor_message)
        request= dict(sensor_message)
        result = self._wait_on_result(request=request)
        result_sensor_type=result["sensor_type"]
        request_sensor_type=request["sensor_type"]
        if result_sensor_type  == request_sensor_type:
            return result
        else:
            raise Exception(f"""Sensortypes mismatch: wanted: {request_sensor_type}, 
                got {result_sensor_type}""")


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
