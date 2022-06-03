# from time import sleep
from  library import Phone
import json



p = Phone()
# p.vibrate(5000)
erg = p.write_text("something else")
erg = json.loads(erg)
erg = erg["value"]
print(erg)
# val = 10
# while True:
#     val = p._get_sensor("prox")
#     val = json.loads(val)
#     val = val["value"]
#     # print(type(val))
#     if val == '0.0':
#         print("ALARM")
#     sleep(0.2)
