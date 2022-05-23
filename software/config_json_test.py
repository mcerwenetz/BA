import json
from util import JsonMessagesWrapper, get_config_parameter, _CONFIG


jmw = JsonMessagesWrapper()
with open("example.json") as fp:
    di = json.load(fp)
command = get_config_parameter(config_dictionary=_CONFIG, parameter_key="vibrate")

print(command)