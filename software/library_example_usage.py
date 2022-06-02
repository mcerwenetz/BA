from time import sleep
from  library import Phone


p = Phone()

while True:
    data = dict(p.get_x_accello())
    print(data["value"])
    sleep(0.1)